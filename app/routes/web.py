from flask import Blueprint,request, jsonify
from app.extensions import mongo
from app.utils.mail_server import request_quote, contact_us
from app.models.request_quote import RequestQuote
from app.models.category import CategoryModel
from app.models.product import ProductModel
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from bson.objectid import ObjectId
from bson.errors import InvalidId

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
        return jsonify({"error": False, "error": str(e)}), 500
    
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
        return jsonify({"error": False, "error": str(e)}), 500

@web_bp.route('/categories', methods=['GET'])
def handle_category():
    try:
        # Fetch all categories from MongoDB
        categories_cursor = mongo.db.categories.find({})
        
        # Convert cursor to list and serialize documents
        categories = []
        for category in categories_cursor:
            category_dict = {
                "_id": str(category["_id"]),
                "name": category.get("name", ""),
                "created_by": category.get("created_by")
            }
            categories.append(category_dict)

        return jsonify({"success": True, "message": "Category fetching successful!", "data": categories}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/categories', methods=['POST'])
def handle_create_category():
    try:
        user_id = get_jwt_identity()  # Extract user from JWT
        data = request.get_json()

        name = data.get('name')
        
        if not name:
            return jsonify({"success": False, "error": "Category name is required"}), 400

        # Check if category already exists
        existing_category = mongo.db.categories.find_one({"name": name})
        if existing_category:
            return jsonify({"success": False, "error": "Category with this name already exists"}), 409

        # Create category model
        category = CategoryModel(
            name=name,
            created_by=user_id
        )
        
        # Convert to dict for MongoDB
        category_dict = vars(category)
        category_dict["created_by"] = user_id
        
        # Save to MongoDB
        result = mongo.db.categories.insert_one(category_dict)
        
        # Add MongoDB _id to the response
        category_dict["_id"] = str(result.inserted_id)
        
        return jsonify({"success": True, "message": "Category created successfully!", "data": category_dict}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/categories/<category_id>', methods=['GET'])
def handle_get_category(category_id):
    try:
        # Validate ObjectId format
        try:
            object_id = ObjectId(category_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid category ID format"}), 400
        
        # Find category by ID
        category = mongo.db.categories.find_one({"_id": object_id})
        
        if not category:
            return jsonify({"success": False, "error": "Category not found"}), 404
        
        # Serialize category
        category_dict = {
            "_id": str(category["_id"]),
            "name": category.get("name", ""),
            "created_by": category.get("created_by")
        }
        
        return jsonify({"success": True, "message": "Category fetched successfully!", "data": category_dict}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/categories/<category_id>', methods=['PUT'])
def handle_update_category(category_id):
    try:
        user_id = get_jwt_identity()  # Extract user from JWT
        data = request.get_json()
        
        # Validate ObjectId format
        try:
            object_id = ObjectId(category_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid category ID format"}), 400
        
        # Check if category exists
        existing_category = mongo.db.categories.find_one({"_id": object_id})
        if not existing_category:
            return jsonify({"success": False, "error": "Category not found"}), 404
        
        name = data.get('name')
        
        if not name:
            return jsonify({"success": False, "error": "Category name is required"}), 400
        
        # Check if another category with the same name exists (excluding current one)
        duplicate_category = mongo.db.categories.find_one({
            "name": name,
            "_id": {"$ne": object_id}
        })
        if duplicate_category:
            return jsonify({"success": False, "error": "Category with this name already exists"}), 409
        
        # Update category
        update_data = {"name": name}
        result = mongo.db.categories.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Category not found"}), 404
        
        # Fetch updated category
        updated_category = mongo.db.categories.find_one({"_id": object_id})
        category_dict = {
            "_id": str(updated_category["_id"]),
            "name": updated_category.get("name", ""),
            "created_by": updated_category.get("created_by")
        }
        
        return jsonify({"success": True, "message": "Category updated successfully!", "data": category_dict}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/categories/<category_id>', methods=['DELETE'])
def handle_delete_category(category_id):
    try:
        # Validate ObjectId format
        try:
            object_id = ObjectId(category_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid category ID format"}), 400
        
        # Check if category exists
        existing_category = mongo.db.categories.find_one({"_id": object_id})
        if not existing_category:
            return jsonify({"success": False, "error": "Category not found"}), 404
        
        # Delete category
        result = mongo.db.categories.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Category not found"}), 404
        
        return jsonify({"success": True, "message": "Category deleted successfully!"}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== PRODUCT ENDPOINTS ====================

@web_bp.route('/products', methods=['GET'])
def handle_products():
    try:
        # Optional query parameters for filtering
        category = request.args.get('category')
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        
        # Fetch all products from MongoDB
        products_cursor = mongo.db.products.find(query)
        
        # Convert cursor to list and serialize documents
        products = []
        for product in products_cursor:
            product_dict = {
                "_id": str(product["_id"]),
                "key": product.get("key", ""),
                "category": product.get("category", ""),
                "product": product.get("product", ""),
                "caption": product.get("caption", ""),
                "image": product.get("image", []),
                "created_by": product.get("created_by")
            }
            products.append(product_dict)

        return jsonify({"success": True, "message": "Products fetched successfully!", "data": products}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/products', methods=['POST'])
def handle_create_product():
    try:
        user_id = get_jwt_identity()  # Extract user from JWT
        data = request.get_json()

        key = data.get('key')
        category = data.get('category')
        product = data.get('product')
        caption = data.get('caption')
        image = data.get('image', [])
        
        # Validate required fields
        if not key:
            return jsonify({"success": False, "error": "Product key is required"}), 400
        if not category:
            return jsonify({"success": False, "error": "Product category is required"}), 400
        if not product:
            return jsonify({"success": False, "error": "Product name is required"}), 400
        if not caption:
            return jsonify({"success": False, "error": "Product caption is required"}), 400
        if not image:
            return jsonify({"success": False, "error": "Product image is required"}), 400

        # Check if product with same key already exists
        existing_product = mongo.db.products.find_one({"key": key})
        if existing_product:
            return jsonify({"success": False, "error": "Product with this key already exists"}), 409

        # Verify category exists (optional validation)
        existing_category = mongo.db.categories.find_one({"name": category})
        if not existing_category:
            return jsonify({"success": False, "error": f"Category '{category}' does not exist"}), 404

        # Ensure image is a list
        if not isinstance(image, list):
            image = [image]

        # Create product model
        product_model = ProductModel(
            key=key,
            category=category,
            product=product,
            caption=caption,
            image=image,
            created_by=user_id
        )
        
        # Convert to dict for MongoDB
        product_dict = vars(product_model)
        product_dict["created_by"] = user_id
        
        # Save to MongoDB
        result = mongo.db.products.insert_one(product_dict)
        
        # Add MongoDB _id to the response
        product_dict["_id"] = str(result.inserted_id)
        
        return jsonify({"success": True, "message": "Product created successfully!", "data": product_dict}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/products/<product_id>', methods=['GET'])
def handle_get_product(product_id):
    try:
        # Validate ObjectId format
        try:
            object_id = ObjectId(product_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid product ID format"}), 400
        
        # Find product by ID
        product = mongo.db.products.find_one({"_id": object_id})
        
        if not product:
            return jsonify({"success": False, "error": "Product not found"}), 404
        
        # Serialize product
        product_dict = {
            "_id": str(product["_id"]),
            "key": product.get("key", ""),
            "category": product.get("category", ""),
            "product": product.get("product", ""),
            "caption": product.get("caption", ""),
            "image": product.get("image", []),
            "created_by": product.get("created_by")
        }
        
        return jsonify({"success": True, "message": "Product fetched successfully!", "data": product_dict}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/products/<product_id>', methods=['PUT'])
def handle_update_product(product_id):
    try:
        user_id = get_jwt_identity()  # Extract user from JWT
        data = request.get_json()
        
        # Validate ObjectId format
        try:
            object_id = ObjectId(product_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid product ID format"}), 400
        
        # Check if product exists
        existing_product = mongo.db.products.find_one({"_id": object_id})
        if not existing_product:
            return jsonify({"success": False, "error": "Product not found"}), 404
        
        # Get update data
        key = data.get('key')
        category = data.get('category')
        product = data.get('product')
        caption = data.get('caption')
        image = data.get('image')
        
        # Build update data
        update_data = {}
        
        if key is not None:
            # Check if another product with the same key exists (excluding current one)
            duplicate_product = mongo.db.products.find_one({
                "key": key,
                "_id": {"$ne": object_id}
            })
            if duplicate_product:
                return jsonify({"success": False, "error": "Product with this key already exists"}), 409
            update_data["key"] = key
        
        if category is not None:
            # Verify category exists
            existing_category = mongo.db.categories.find_one({"name": category})
            if not existing_category:
                return jsonify({"success": False, "error": f"Category '{category}' does not exist"}), 404
            update_data["category"] = category
        
        if product is not None:
            update_data["product"] = product
        
        if caption is not None:
            update_data["caption"] = caption
        
        if image is not None:
            # Ensure image is a list
            if not isinstance(image, list):
                image = [image]
            update_data["image"] = image
        
        if not update_data:
            return jsonify({"success": False, "error": "No fields to update"}), 400
        
        # Update product
        result = mongo.db.products.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Product not found"}), 404
        
        # Fetch updated product
        updated_product = mongo.db.products.find_one({"_id": object_id})
        product_dict = {
            "_id": str(updated_product["_id"]),
            "key": updated_product.get("key", ""),
            "category": updated_product.get("category", ""),
            "product": updated_product.get("product", ""),
            "caption": updated_product.get("caption", ""),
            "image": updated_product.get("image", []),
            "created_by": updated_product.get("created_by")
        }
        
        return jsonify({"success": True, "message": "Product updated successfully!", "data": product_dict}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@web_bp.route('/products/<product_id>', methods=['DELETE'])
def handle_delete_product(product_id):
    try:
        # Validate ObjectId format
        try:
            object_id = ObjectId(product_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid product ID format"}), 400
        
        # Check if product exists
        existing_product = mongo.db.products.find_one({"_id": object_id})
        if not existing_product:
            return jsonify({"success": False, "error": "Product not found"}), 404
        
        # Delete product
        result = mongo.db.products.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Product not found"}), 404
        
        return jsonify({"success": True, "message": "Product deleted successfully!"}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    