from app import create_app
from app.extensions import mongo
from datetime import datetime

# Create Flask app
app = create_app()

# Push app context
with app.app_context():

    # ==================== CLEAR DATA ====================
    mongo.db.rate_cards.delete_many({})
    mongo.db.zones.delete_many({})

    print("🗑️  Cleared existing data")

    # ==================== RATE CARDS ====================

    rate_cards = [
        {
            'country': 'KH',
            'mode': 'road',
            'service': 'economy',
            'rate_per_km': 0.30,
            'rate_per_kg': 0.80,
            'fuel_surcharge': 10,
            'handling_fee': 2.00,
            'currency': 'USD',
            'active': True,
            'created_at': datetime.utcnow()
        },
        {
            'country': 'KH',
            'mode': 'road',
            'service': 'standard',
            'rate_per_km': 0.45,
            'rate_per_kg': 1.20,
            'fuel_surcharge': 12,
            'handling_fee': 3.00,
            'currency': 'USD',
            'active': True,
            'created_at': datetime.utcnow()
        },
        {
            'country': 'KH',
            'mode': 'road',
            'service': 'express',
            'rate_per_km': 0.65,
            'rate_per_kg': 1.80,
            'fuel_surcharge': 15,
            'handling_fee': 5.00,
            'currency': 'USD',
            'active': True,
            'created_at': datetime.utcnow()
        },
        # (keep all your other rate cards here)
    ]

    result = mongo.db.rate_cards.insert_many(rate_cards)
    print(f"✅ Inserted {len(result.inserted_ids)} rate cards")

    # ==================== ZONES ====================

    zones = [
        {
            'name': 'Phnom Penh Metro',
            'country': 'KH',
            'locations': ['Phnom Penh', 'Ta Khmau', 'Kandal'],
            'zone_type': 'urban',
            'active': True,
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Siem Reap Region',
            'country': 'KH',
            'locations': ['Siem Reap', 'Angkor'],
            'zone_type': 'tourist',
            'active': True,
            'created_at': datetime.utcnow()
        },
    ]

    result = mongo.db.zones.insert_many(zones)
    print(f"✅ Inserted {len(result.inserted_ids)} zones")

    print("\n🎉 Database seeded successfully!")
    print("\n📊 Summary:")
    print(f"   Rate Cards: {mongo.db.rate_cards.count_documents({})}")
    print(f"   Zones: {mongo.db.zones.count_documents({})}")
