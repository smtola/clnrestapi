from flask import Blueprint,request, jsonify
from app.extensions import mongo
from app.utils.mail_server import request_quote, contact_us
from app.models.request_quote import RequestQuote
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

web_bp = Blueprint('web', __name__)

@web_bp.route('/request-quote', methods=['POST'])
@jwt_required()
def handle_request_quote():
    try:
        user_id = get_jwt_identity()  # Extract user from JWT
        
        data = request.get_json()
        company_name = data.get('company_name')
        full_name = data.get('full_name')
        email = data.get('email')
        address = data.get('address')
        tel = data.get('tel')
        job = data.get('job')
        origin_destination = data.get('origin_destination')
        product_name = data.get('product_name')
        weight_dimensions = data.get('weight_dimensions')
        service = data.get('service')
        container_size = data.get('container_size')

        # Save Quote with user reference
        quote = RequestQuote(
            company_name=company_name,
            full_name=full_name,
            email=email,
            address=address,
            tel=tel,
            job=job,
            origin_destination=origin_destination,
            product_name=product_name,
            weight_dimensions=weight_dimensions,
            service=service,
            container_size=container_size,
            created_by=user_id  # store who requested
        )
        
        # Convert to dict for MongoDB
        quote_dict = vars(quote)
        quote_dict["created_by"] = user_id
        mongo.db.quotes.insert_one(quote_dict)
        # Send email
        request_quote(
            company_name, full_name, email, address, tel, job,
            origin_destination, product_name, weight_dimensions,service, container_size,
            user_id
        )

        return jsonify({"success": True, "message": "Quote request sent!","data":quote_dict}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

@web_bp.route('/contact-us', methods=['POST'])
@jwt_required()
def handle_contact_us():
    try:
        user_id = get_jwt_identity()  # Extract user from JWT
        
        data = request.get_json()
        company_name = data.get('company_name')
        full_name = data.get('full_name')
        email = data.get('email')
        address = data.get('address')
        tel = data.get('tel')
        job = data.get('job')
        origin_destination = data.get('origin_destination')
        product_name = data.get('product_name')
        weight_dimensions = data.get('weight_dimensions')
        service = data.get('service')
        container_size = data.get('container_size')

        # Save Quote with user reference
        quote = RequestQuote(
            company_name=company_name,
            full_name=full_name,
            email=email,
            address=address,
            tel=tel,
            job=job,
            origin_destination=origin_destination,
            product_name=product_name,
            weight_dimensions=weight_dimensions,
            service=service,
            container_size=container_size,
            created_by=user_id  # store who requested
        )
        
        # Convert to dict for MongoDB
        quote_dict = vars(quote)
        quote_dict["created_by"] = user_id
        mongo.db.contact_us.insert_one(quote_dict)
        # Send email
        contact_us(
            company_name, full_name, email, address, tel, job,
            origin_destination, product_name, weight_dimensions,service, container_size,
            user_id
        )

        return jsonify({"success": True, "message": "Contact Us request sent!","data":quote_dict}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500