from flask import Blueprint, request, jsonify
from app.extensions import mongo
from app.utils.jwt_utils import create_access_token
from flask_jwt_extended import (
    create_refresh_token,  
    jwt_required,
    get_jwt_identity,
    set_refresh_cookies,
    unset_jwt_cookies
)
from app.utils.email_otp import send_otp_email, generate_otp
from app.models.user import User
import requests
from user_agents import parse 
from datetime import datetime, timedelta,timezone

auth_bp = Blueprint('auth', __name__)

# ---------------- Helpers ----------------
def serialize_user(doc):
    """Convert Mongo document to JSON-serializable dict (hide sensitive fields)."""
    return {
        "_id": str(doc["_id"]),
        "username": doc["username"],
        "email": doc["email"],
        "role": doc.get("role", "user"),
        "is_verified": doc.get("is_verified", False)
    }

def get_client_ip():
    # Check common headers first
    if 'X-Forwarded-For' in request.headers:
        # Might contain multiple IPs if behind multiple proxies
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    elif 'X-Real-IP' in request.headers:
        ip = request.headers['X-Real-IP']
    else:
        ip = request.remote_addr
    return ip or 'Unknown'

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'USER')
    client_local_ip = data.get('local_ip', 'Unknown')  # Sent from frontend

    if not username or not email or not password:
        return jsonify({"msg": "Missing required fields", "status": False, "statusCode":400}), 400

    if mongo.db.users.find_one({"username": username}):
        return jsonify({"msg": "Username already exists", "status": False, "statusCode":409}), 409
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"msg": "Email already exists", "status": False, "statusCode":409}), 409

    # Device Info
    user_agent_str = request.headers.get('User-Agent', '')
    user_agent = parse(user_agent_str)
    device_info = {
        "browser": f"{user_agent.browser.family} {user_agent.browser.version_string}",
        "os": f"{user_agent.os.family} {user_agent.os.version_string}",
        "device": f"{user_agent.device.family}"
    }

    # Public IP
    public_ip = get_client_ip()

    # Location from public IP
    location = {}
    try:
        res = requests.get(f"https://ipapi.co/{public_ip}/json/").json()
        location = {
            "city": res.get("city"),
            "region": res.get("region"),
            "country": res.get("country_name"),
            "latitude": res.get("latitude"),
            "longitude": res.get("longitude"),
        }
    except:
        location = {}

    # Save user
    user = User(username=username, email=email, password=password, role=role)
    otp = generate_otp()
    otp_expire = datetime.utcnow() + timedelta(minutes=5)
    user_doc = user.__dict__.copy()
    user_doc.update({
        "requires_otp":False,
        "otp": otp,
        "is_verified": False,
        "public_ip": public_ip,
        "local_ip": client_local_ip,   # stored from frontend
        "device_info": device_info,
        "location": location,
        "otp_expire": otp_expire,
        "created_at": datetime.utcnow() - timedelta(minutes=1)
    })

    # Insert user
    result = mongo.db.users.insert_one(user_doc)

    if not result.inserted_id:
        return jsonify({
            "msg": "Something went wrong saving the user",
            "status": False,
            "statusCode": 500
        }), 500
        
    send_otp_email(email, otp)
    
    return jsonify({
        "msg": "Signup successful. Please verify your email using the OTP sent.",
        "status": True
        }), 201

# ---------------- Login ----------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    client_local_ip = data.get('local_ip', 'Unknown')  # Frontend sends local IP

    if not username or not password:
        return jsonify({"msg": "Missing username or password","status": False}), 400

    user_doc = mongo.db.users.find_one({"username": username})
    if not user_doc:
        return jsonify({"msg": "User not found","status": False}), 404
    if not User.check_password(user_doc["password_hash"], password):
        return jsonify({"msg": "Incorrect password", "status": False}), 401
    
    # Check if email is verified
    if not user_doc.get("is_verified", False):
        return jsonify({
            "msg": "Please verify your email before logging in. Check your email for the verification OTP.",
            "status": False,
            "statusCode": 403,
            "email": user_doc.get("email")
        }), 403

    # --------- Device Info ---------
    user_agent_str = request.headers.get('User-Agent', '')
    user_agent = parse(user_agent_str)
    device_info = {
        "browser": f"{user_agent.browser.family} {user_agent.browser.version_string}",
        "os": f"{user_agent.os.family} {user_agent.os.version_string}",
        "device": f"{user_agent.device.family}"
    }

    # --------- Public IP ---------
    public_ip = get_client_ip()

    # --------- Location ---------
    location = {}
    try:
        res = requests.get(f"https://ipapi.co/{public_ip}/json/").json()
        location = {
            "city": res.get("city"),
            "region": res.get("region"),
            "country": res.get("country_name"),
            "latitude": res.get("latitude"),
            "longitude": res.get("longitude"),
        }
    except:
        location = {}

    # --------- Update user login metadata ---------
    mongo.db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {
            "last_login": datetime.utcnow(),
            "public_ip": public_ip,
            "local_ip": client_local_ip,
            "device_info": device_info,
            "location": location
        }}
    )

    # --------- Handle OTP ---------
    requires_otp = user_doc.get("requires_otp", False)

    if requires_otp == False:
        otp_code = generate_otp()
        otp_expire = datetime.utcnow() + timedelta(minutes=5)
        mongo.db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"otp_code": otp_code, "otp_expire": otp_expire}}
        )

        # Send OTP via email
        if not send_otp_email(user_doc.get("email"), otp_code):
            return jsonify({
                "msg": "Failed to send OTP. Please try again later.",
                "requiresOtp": False,
                "status": False
            }), 500

        return jsonify({
            "msg": "OTP required. Please check your email.",
            "requiresOtp": True,
            "username": username,
            "status": True
        }), 200
    else:
        # If requires_otp is True, proceed with login (OTP already handled or not needed)
        access_token = create_access_token(
            identity=str(user_doc["_id"]),
            additional_claims={"role": user_doc.get("role", "user")}
        )
        refresh_token = create_refresh_token(identity=str(user_doc["_id"]))

        resp = jsonify({
            "msg": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": serialize_user(user_doc),
            "status": True
        })
        set_refresh_cookies(resp, refresh_token)
        return resp, 200

# ---------------- Refresh Token ----------------
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token,"status": True}), 200

# ---------------- Logout ----------------
@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(resp)
    return resp, 200

# ---------------- Verify Email ----------------
@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({"msg": "Missing email or OTP"}), 400

    user_doc = mongo.db.users.find_one({"email": email})
    otp_expire = user_doc.get("otp_expire")
    if not user_doc:
        return jsonify({"msg": "User not found"}), 404
    if user_doc.get("is_verified", False):
        return jsonify({"msg": "Email already verified"}), 400
    if user_doc.get("otp") != otp:
        return jsonify({"msg": "Invalid OTP"}), 400
    if otp_expire and datetime.utcnow() > otp_expire:
        return jsonify({"msg": "OTP expired"}), 401

    mongo.db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"is_verified": True}, "$unset": {"otp": ""}}
    )

    # Build safe response (exclude sensitive fields)
    safe_user = {
        "_id": str(user_doc["_id"]),
        "username": user_doc.get("username"),
        "email": user_doc.get("email"),
        "role": user_doc.get("role"),
        "is_verified": True,  
        "requires_otp": user_doc.get("requires_otp", False),
        "public_ip": user_doc.get("public_ip"),
        "local_ip": user_doc.get("local_ip"),
        "device_info": user_doc.get("device_info"),
        "location": user_doc.get("location"),
        "created_at": user_doc.get("created_at"),
    }

    return jsonify({
            "msg": "Email verified successfully.", 
            "user": safe_user,
            "status": True
        }), 200

# ---------------- Verify OTP ----------------
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    username = data.get('username')
    otp = data.get('otp')

    if not username or not otp:
        return jsonify({"msg": "Missing username or OTP"}), 400

    user_doc = mongo.db.users.find_one({"username": username})
    if not user_doc:
        return jsonify({"msg": "User not found"}), 404

    stored_otp = user_doc.get("otp_code")
    otp_expire = user_doc.get("otp_expire")

    if not stored_otp or stored_otp != otp:
        return jsonify({"msg": "Invalid OTP"}), 401
    if otp_expire and datetime.utcnow() > otp_expire:
        return jsonify({"msg": "OTP expired"}), 401

    # OTP valid → remove OTP, mark verified
    mongo.db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$unset": {"otp_code": "", "otp_expire": ""}, "$set": {"is_verified": True}}
    )

    access_token = create_access_token(
        identity=str(user_doc["_id"]),
        additional_claims={"role": user_doc.get("role", "user")}
    )
    refresh_token = create_refresh_token(identity=str(user_doc["_id"]))

    resp = jsonify({
        "msg": "OTP verified successfully",
        "access_token": access_token,
        "refresh_token":refresh_token,
        "user": {
            "username": user_doc["username"],
            "email": user_doc.get("email"),
            "role": user_doc.get("role", "user")
        },
        "status": True
    })
    set_refresh_cookies(resp, refresh_token)
    return resp, 200
 
# ---------------- Resend OTP ----------------

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username and not email:
        return jsonify({"msg": "Missing username or email"}), 400

    user_doc = mongo.db.users.find_one({
        "$or": [
            {"username": username},
            {"email": email}
        ]
    })
    if not user_doc:
        return jsonify({"msg": "User not found"}), 404

    otp = generate_otp()
    otp_expire = datetime.utcnow() + timedelta(minutes=5)

    if username:  # 🔹 Resend by username
        mongo.db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"otp_code": otp, "otp_expire": otp_expire}}
        )
        send_otp_email(user_doc.get("email"), otp)

        return jsonify({
            "msg": "OTP resent successfully",
            "username": username,
            "otp_expire": otp_expire.isoformat(),
            "status": True
        }), 200

    elif email:  # 🔹 Resend by email
        mongo.db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"otp": otp, "otp_expire": otp_expire}}
        )
        send_otp_email(email, otp)

        return jsonify({
            "msg": "OTP resent successfully",
            "email": email,
            "otp_expire": otp_expire.isoformat(),
            "status": True
        }), 200

# ---------------- Get Users (Protected) ----------------
@auth_bp.route('/users', methods=["GET"])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    users_cursor = mongo.db.users.find({}, {"password_hash": 0, "otp": 0})
    users = [serialize_user(u) for u in users_cursor]

    return jsonify({
        "data": users,
        "msg": f"Fetching users successful (requested by {current_user_id})",
        "status": True
    }), 200

