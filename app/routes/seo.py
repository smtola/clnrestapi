from flask import Blueprint, jsonify, request
from app.extensions import mongo
from bson.objectid import ObjectId

seo_bp = Blueprint("seo", __name__)

# ✅ Get all SEO entries
@seo_bp.route("", methods=['GET'])
def get_all_seo():
    try:
        # Fetch all SEO entries from MongoDB
        seo_cursor = mongo.db.seo.find({})
        
        # Convert cursor to list and serialize documents
        seo_list = []
        for seo in seo_cursor:
            seo_dict = {
                "page": seo.get("page", ""),
                "title": seo.get("title", ""),
                "description": seo.get("description", ""),
                "keywords": seo.get("keywords", ""),
                "ogTitle": seo.get("ogTitle", ""),
                "ogDescription": seo.get("ogDescription", ""),
                "ogImage": seo.get("ogImage", ""),
                "url": seo.get("url", "")
            }
            seo_list.append(seo_dict)

        return jsonify(seo_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Create SEO
@seo_bp.route("/<page>", methods=["POST"])
def create_seo():
    data = request.json
    page = data.get("page")
    if mongo.db.seo.find_one({"page": page}):
        return jsonify({"error": "SEO for this page already exists"}), 400
    mongo.db.seo.insert_one(data)
    return jsonify({"message": "SEO created"}), 201

# ✅ Read SEO
@seo_bp.route("/<page>", methods=["GET"])
def get_seo(page):
    tab = request.args.get("tab")
    products = request.args.get("products")

    if tab:
        page_key = f"{page}?tab={tab}"
    elif products:
        page_key = f"{page}?products={products}"
    else:
        page_key = page

    seo = mongo.db.seo.find_one({"page": page_key}, {"_id": 0})
    if not seo:
        return jsonify({"error": "Page not found"}), 404
    return jsonify(seo)

# ✅ Update SEO
@seo_bp.route("/<page>", methods=["PUT"])
def update_seo(page):
    data = request.json
    result = mongo.db.seo.update_one({"page": page}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Page not found"}), 404
    return jsonify({"message": "SEO updated"})

# ✅ Delete SEO
@seo_bp.route("/<page>", methods=["DELETE"])
def delete_seo(page):
    result = mongo.db.seo.delete_one({"page": page})
    if result.deleted_count == 0:
        return jsonify({"error": "Page not found"}), 404
    return jsonify({"message": "SEO deleted"})
