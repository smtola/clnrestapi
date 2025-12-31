from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from bson import ObjectId
from datetime import datetime
import math
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from app.extensions import mongo

price_bp = Blueprint("price", __name__)
geolocator = Nominatim(
    user_agent="logistics_port_finder",
    timeout=10
)
# =========================================================
# Helper: External Port Search (Nominatim fallback)
# =========================================================

def search_port_external(query):
    try:
        locations = geolocator.geocode(
            f"{query} port",
            exactly_one=False,
            limit=5,
            addressdetails=True
        )

        results = []
        if locations:
            for loc in locations:
                results.append({
                    'name': loc.address,
                    'lat': loc.latitude,
                    'lon': loc.longitude,
                    'source': 'nominatim'
                })
        return results
    except Exception as e:
        print("Nominatim error:", e)
        return []

# ==================== HELPER FUNCTIONS ====================

def calculate_distance(origin, destination):
    try:
        origin_loc = geolocator.geocode(origin)
        dest_loc = geolocator.geocode(destination)

        if not origin_loc or not dest_loc:
            return None

        return round(
            geodesic(
                (origin_loc.latitude, origin_loc.longitude),
                (dest_loc.latitude, dest_loc.longitude)
            ).kilometers,
            2
        )
    except Exception as e:
        print(f"Distance calculation error: {e}")
        return None



def get_chargeable_weight(container_max_weight, container_quantity):
    return container_max_weight * container_quantity


def get_rate_card(country, mode, service):
    query = {
        'country': country,
        'mode': mode.lower(),
        'service': service,
        'active': True
    }
    return mongo.db.rate_cards.find_one(query)


def calculate_quote_price(distance, weight, container_qty, rate_card, mode, service):
    trucking = rate_card.get('trucking', 0)
    docs = rate_card.get('docs', 0)
    freight = rate_card.get('freight', 0)
    othc = rate_card.get('othc', 0)
    minimum = rate_card.get('minimum_charge', 0)  # safe default

    breakdown = {}

    # 🚚 ROAD – LOCAL
    if mode == 'road' and service == 'local_charge':
        trucking_cost = trucking + docs 

        subtotal = trucking_cost + othc

        breakdown = {
            'trucking': round(trucking, 2),
            'docs': round(docs, 2),
            'othc': round(othc, 2)
        }

    # 🚢 SEA – FREIGHT
    elif mode == 'sea' and service == 'freight':
        freight_cost = container_qty * freight
        subtotal = freight_cost + othc

        breakdown = {
            'freight_cost': round(freight_cost, 2),
            'othc': othc
        }

    else:
        return None

    total = max(subtotal, minimum)

    return {
        'subtotal': round(subtotal, 2),
        'minimum_applied': total != subtotal,
        'total': round(total, 2),
        'breakdown': breakdown
    }

def estimate_delivery_time(distance, service, rate_card=None):
    if rate_card and rate_card.get('transit_time'):
        tt = rate_card['transit_time']
        return f"{tt['min']}–{tt['max']} {tt['unit']}"

    # fallback logic
    if service == 'local_charge':
        if distance < 150:
            return 'Same day'
        elif distance < 400:
            return '1 day'
        return '1–2 days'

    if service == 'freight':
        return '5–10 days'

    return 'N/A'

def generate_quotes(origin, destination, container_max_weight, container_quantity, country, mode):
    distance = None
    mode = mode.lower()  # ✅ normalize once

    if mode == 'road':
        distance = calculate_distance(origin, destination)
        if distance is None:
            return None, 'Unable to calculate distance'

    chargeable_weight = get_chargeable_weight(container_max_weight, container_quantity)

    # ✅ Correct services by transport mode
    if mode == 'road':
        services = ['local_charge']
    elif mode == 'sea':
        services = ['freight']
    else:
        return None, 'Unsupported transport mode'

    quotes = {}

    for service in services:
        rate_card = get_rate_card(country, mode, service)
        print("RATE CARD:", rate_card)

        if not rate_card:
            continue

        pricing = calculate_quote_price(
            distance=distance or 0,
            weight=chargeable_weight,
            container_qty=container_quantity,
            rate_card=rate_card,
            mode=mode,
            service=service
        )

        if not pricing:
            continue

        eta = estimate_delivery_time(distance or 0, service)

        quotes[service] = {
            'price': pricing['total'],
            'eta': eta,
            'currency': rate_card.get('currency', 'USD'),
            'breakdown': pricing
        }

    if not quotes:
        return None, 'No available rates'

    return {
        'distance_km': distance,
        'chargeable_weight': chargeable_weight,
        'quotes': quotes
    }, None


# ==================== API ENDPOINTS ====================

@price_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200

@price_bp.route('/quote', methods=['POST'])
def create_quote():
    try:
        data = request.json

        required = ['origin', 'destination', 'containerMaxWeight', 'containerQuantity', 'commodity']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        quote_data, error = generate_quotes(
            origin=data['origin'],
            destination=data['destination'],
            container_max_weight=float(data['containerMaxWeight']),
            container_quantity=int(data['containerQuantity']),
            country=data.get('country', 'Cambodia'),
            mode=data.get('mode', 'Road')
        )

        if error:
            return jsonify({'error': error}), 400

        quote_doc = {
            **quote_data,
            'origin': data['origin'],
            'destination': data['destination'],
            'commodity': data['commodity'],
            'mode': data.get('mode', 'Road'),
            'country': data.get('country', 'Cambodia'),
            'created_at': datetime.utcnow(),
            'converted': False
        }

        result = mongo.db.quotes.insert_one(quote_doc)

        return jsonify({
            'quote_id': str(result.inserted_id),
            **quote_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@price_bp.route('/quote/<quote_id>', methods=['GET'])
def get_quote_by_id(quote_id):
    try:
        quote = mongo.db.quotes.find_one({'_id': ObjectId(quote_id)})
        if not quote:
            return jsonify({'error': 'Quote not found'}), 404
        quote['_id'] = str(quote['_id'])
        return jsonify(quote), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@price_bp.route('/quote/<quote_id>', methods=['PUT'])
def update_quote(quote_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        quote = mongo.db.quotes.find_one({'_id': ObjectId(quote_id)})
        if not quote:
            return jsonify({'error': 'Quote not found'}), 404

        # Merge updates
        quote.update(data)

        # Recalculate
        quote_data, error = generate_quotes(
            origin=quote['origin'],
            destination=quote['destination'],
            container_max_weight=float(quote['container_max_weight']),
            container_quantity=int(quote['container_quantity']),
            country=quote.get('country', 'KH'),
            mode=quote.get('mode', 'sea')
        )

        if error:
            return jsonify({'error': error}), 400

        update_data = {
            'distance_km': quote_data['distance_km'],
            'chargeable_weight': quote_data['chargeable_weight'],
            'quotes': quote_data['quotes'],
            'updated_at': datetime.utcnow()
        }

        mongo.db.quotes.update_one({'_id': ObjectId(quote_id)}, {'$set': update_data})
        updated_quote = mongo.db.quotes.find_one({'_id': ObjectId(quote_id)})
        updated_quote['_id'] = str(updated_quote['_id'])

        return jsonify(updated_quote), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@price_bp.route('/quotes/history', methods=['GET'])
def get_quote_history():
    """Get quote history with pagination"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit

        quotes = list(mongo.db.quotes.find().sort('created_at', -1).skip(skip).limit(limit))
        total = mongo.db.quotes.count_documents({})

        for quote in quotes:
            quote['_id'] = str(quote['_id'])

        return jsonify({
            'quotes': quotes,
            'total': total,
            'page': page,
            'pages': math.ceil(total / limit)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
# =========================================================
# SEARCH PORT (AUTOCOMPLETE)
# =========================================================
# GET /finder_port/search?q=singapore
# =========================================================

@price_bp.route('/finder_port/search', methods=['GET'])
def search_finder_port():
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return jsonify([]), 200

    ports = list(mongo.db.finder_ports.find({
        'active': True,
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},
            {'city': {'$regex': query, '$options': 'i'}},
            {'code': {'$regex': query, '$options': 'i'}},
            {'country': {'$regex': query, '$options': 'i'}}
        ]
    }).limit(10))

    results = []
    for p in ports:
        results.append({
            'id': str(p['_id']),
            'name': p['name'],
            'code': p.get('code', ''),
            'country': p.get('country', ''),
            'city': p.get('city', ''),
            'lat': p['lat'],
            'lon': p['lon'],
            'type': p.get('type', 'sea')
        })

    # Fallback to Nominatim if DB empty
    if not results:
        results = search_port_external(query)

    return jsonify(results), 200


# =========================================================
# GET ALL PORTS (ADMIN / LIST)
# =========================================================
# GET /finder_port
# =========================================================

@price_bp.route('/finder_port', methods=['GET'])
def get_all_ports():
    ports = list(mongo.db.finder_ports.find({'active': True}))

    for p in ports:
        p['_id'] = str(p['_id'])

    return jsonify(ports), 200


# =========================================================
# GET SINGLE PORT
# =========================================================
# GET /finder_port/<id>
# =========================================================

@price_bp.route('/finder_port/<port_id>', methods=['GET'])
def get_port(port_id):
    port = mongo.db.finder_ports.find_one({'_id': ObjectId(port_id)})

    if not port:
        return jsonify({'error': 'Port not found'}), 404

    port['_id'] = str(port['_id'])
    return jsonify(port), 200


# =========================================================
# CREATE PORT (ADMIN)
# =========================================================
# POST /finder_port
# =========================================================

@price_bp.route('/finder_port', methods=['POST'])
def create_port():
    data = request.json

    required_fields = ['name', 'country', 'lat', 'lon']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    port_doc = {
        'name': data['name'],
        'code': data.get('code', ''),
        'country': data['country'],
        'city': data.get('city', ''),
        'type': data.get('type', 'sea'),   # sea | air | inland
        'lat': float(data['lat']),
        'lon': float(data['lon']),
        'source': 'manual',
        'active': True,
        'created_at': datetime.utcnow()
    }

    result = mongo.db.finder_ports.insert_one(port_doc)

    return jsonify({
        'id': str(result.inserted_id),
        'message': 'Port created successfully'
    }), 201


# =========================================================
# UPDATE PORT
# =========================================================
# PUT /finder_port/<id>
# =========================================================

@price_bp.route('/finder_port/<port_id>', methods=['PUT'])
def update_port(port_id):
    data = request.json
    data['updated_at'] = datetime.utcnow()

    result = mongo.db.finder_ports.update_one(
        {'_id': ObjectId(port_id)},
        {'$set': data}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Port not found'}), 404

    return jsonify({'message': 'Port updated'}), 200


# =========================================================
# DELETE PORT (SOFT DELETE)
# =========================================================
# DELETE /finder_port/<id>
# =========================================================

@price_bp.route('/finder_port/<port_id>', methods=['DELETE'])
def delete_port(port_id):
    result = mongo.db.finder_ports.update_one(
        {'_id': ObjectId(port_id)},
        {'$set': {
            'active': False,
            'deleted_at': datetime.utcnow()
        }}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Port not found'}), 404

    return jsonify({'message': 'Port deactivated'}), 200

@price_bp.route('/rate-cards', methods=['GET'])
def get_rate_cards():
    """Get all active rate cards"""
    try:
        rate_cards = list(mongo.db.rate_cards.find({'active': True}))
        for card in rate_cards:
            card['_id'] = str(card['_id'])
        return jsonify(rate_cards), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@price_bp.route('/rate-cards', methods=['POST'])
def create_rate_card():
    """Create new rate card (Admin)"""
    try:
        data = request.json
        
        required = ['country', 'mode', 'service']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        data['active'] = True
        data['created_at'] = datetime.utcnow()

        result = mongo.db.rate_cards.insert_one(data)
        return jsonify({'id': str(result.inserted_id), 'message': 'Rate card created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@price_bp.route('/rate-cards/<card_id>', methods=['PUT'])
def update_rate_card(card_id):
    """Update rate card (Admin)"""
    try:
        data = request.json
        data['updated_at'] = datetime.utcnow()
        
        result = mongo.db.rate_cards.update_one(
            {'_id': ObjectId(card_id)},
            {'$set': data}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Rate card not found'}), 404
        
        return jsonify({'message': 'Rate card updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@price_bp.route('/rate-cards/<card_id>', methods=['DELETE'])
def delete_rate_card(card_id):
    """Deactivate rate card (Admin)"""
    try:
        result = mongo.db.rate_cards.update_one(
            {'_id': ObjectId(card_id)},
            {'$set': {'active': False}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Rate card not found'}), 404
        
        return jsonify({'message': 'Rate card deactivated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@price_bp.route('/commodities', methods=['GET'])
def get_commodities():
    """Get all commodities"""
    try:
        commodities = list(mongo.db.commodities.find())
        for c in commodities:
            c['_id'] = str(c['_id'])
        return jsonify(commodities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@price_bp.route('/commodities/<commodity_id>', methods=['GET'])
def get_commodity(commodity_id):
    """Get single commodity by ID"""
    try:
        commodity = mongo.db.commodities.find_one({'_id': ObjectId(commodity_id)})
        if not commodity:
            return jsonify({'error': 'Commodity not found'}), 404
        commodity['_id'] = str(commodity['_id'])
        return jsonify(commodity), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@price_bp.route('/commodities', methods=['POST'])
def create_commodities():
    """Create one or multiple commodities"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Wrap single object into a list for uniform processing
        if isinstance(data, dict):
            data = [data]

        created = []
        for item in data:
            if 'name' not in item:
                return jsonify({'error': 'Missing required field: name'}), 400

            commodity_doc = {
                'name': item['name'],
                'description': item.get('description', ''),
                'code': item.get('code', ''),
                'created_at': datetime.utcnow(),
                'active': True
            }
            result = mongo.db.commodities.insert_one(commodity_doc)
            created.append({'id': str(result.inserted_id), 'name': item['name']})

        return jsonify({'created': created, 'message': 'Commodities created'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@price_bp.route('/commodities/<commodity_id>', methods=['PUT'])
def update_commodity(commodity_id):
    """Update commodity"""
    try:
        data = request.json
        data['updated_at'] = datetime.utcnow()

        result = mongo.db.commodities.update_one(
            {'_id': ObjectId(commodity_id)},
            {'$set': data}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Commodity not found'}), 404

        return jsonify({'message': 'Commodity updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@price_bp.route('/commodities/<commodity_id>', methods=['DELETE'])
def delete_commodity(commodity_id):
    """Deactivate commodity"""
    try:
        result = mongo.db.commodities.update_one(
            {'_id': ObjectId(commodity_id)},
            {'$set': {'active': False, 'deleted_at': datetime.utcnow()}}
        )
        if result.matched_count == 0:
            return jsonify({'error': 'Commodity not found'}), 404

        return jsonify({'message': 'Commodity deactivated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500