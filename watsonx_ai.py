"""
TravelPlannerAI — AI helpers
The chat assistant is now handled by the embedded IBM watsonx Orchestrate widget.
This module only provides itinerary generation and destination-info via the
structured mock/fallback engine (no watsonx.ai SDK or Project ID required).
"""

# ── Public API ─────────────────────────────────────────────────────────────

def generate_itinerary(trip_data: dict) -> dict:
    """Generate a full day-wise travel itinerary."""
    return _mock_itinerary(trip_data)


def get_destination_info(destination: str) -> dict:
    """Get quick destination highlights."""
    return _mock_destination(destination)


# ── Helpers ────────────────────────────────────────────────────────────────

def _mock_destination(destination: str) -> dict:
    return {
        "destination": destination,
        "tagline": f"Discover the wonders of {destination}.",
        "highlights": [
            "Iconic landmarks and historic sites",
            "Vibrant local markets and street food",
            "World-class museums and galleries",
            "Scenic viewpoints and natural beauty",
            "Rich culture, traditions, and festivals",
        ],
        "best_months": "Spring (March–May) and Autumn (September–November)",
        "avg_budget_per_day": "$100–200 USD per person",
        "visa_info": "Check your country's embassy website for current visa requirements.",
        "weather": "Varies by season — check a forecast closer to your travel date.",
    }


def _mock_itinerary(trip_data: dict) -> dict:
    destination = trip_data.get("destination", "Paris, France")
    travelers   = trip_data.get("travelers", 2)
    return {
        "destination": destination,
        "overview": f"{destination} is a breathtaking destination that offers a perfect blend of culture, history, and natural beauty. This itinerary has been crafted to give you the best possible experience.",
        "best_time_to_visit": "Spring (March-May) and Fall (September-November)",
        "currency": "Local currency — check current exchange rates",
        "language": "Local language",
        "days": [
            {
                "day": 1,
                "date": trip_data.get("start_date", "Day 1"),
                "theme": "Arrival & City Exploration",
                "morning":   {"activity": "Arrive & Check-in", "description": f"Arrive at {destination} and check into your hotel.", "duration": "2 hours", "cost": "Included"},
                "afternoon": {"activity": "City Center Walk",  "description": "Explore the main city center, visit the central square and local markets.", "duration": "3 hours", "cost": "$10–20 per person"},
                "evening":   {"activity": "Welcome Dinner",    "description": "Enjoy a traditional local dinner at a highly-rated restaurant.", "duration": "2 hours", "cost": "$30–50 per person"},
                "meals": {"breakfast": "Hotel breakfast or local café", "lunch": "Local bistro in the city center", "dinner": "Signature traditional restaurant"},
                "hotel": "4-star city center hotel — comfortable, well-located",
                "tips": "Get a local SIM card or activate international roaming on arrival."
            },
            {
                "day": 2,
                "date": trip_data.get("start_date", "Day 2"),
                "theme": "Cultural Immersion",
                "morning":   {"activity": "Famous Landmarks",  "description": "Visit the iconic landmarks and monuments the destination is known for.", "duration": "3 hours", "cost": "$15–25 per person"},
                "afternoon": {"activity": "Museum & History",  "description": "Explore the city's history through its world-class museums.", "duration": "3 hours", "cost": "$10–15 per person"},
                "evening":   {"activity": "Local Night Market","description": "Experience the vibrant night market with local food and crafts.", "duration": "2 hours", "cost": "$20–40"},
                "meals": {"breakfast": "Cozy local bakery", "lunch": "Museum café", "dinner": "Night market street food"},
                "hotel": "Same hotel as Day 1",
                "tips": "Book museum tickets online in advance to skip the queue."
            }
        ],
        "attractions": [
            {"name": "Main City Landmark", "description": "The most iconic landmark of the destination.", "entry_fee": "$15", "best_time": "Morning"},
            {"name": "Historical Museum",  "description": "World-class museum showcasing local history and art.", "entry_fee": "$10", "best_time": "Afternoon"},
            {"name": "Local Market",       "description": "Vibrant market with local produce and crafts.", "entry_fee": "Free", "best_time": "Morning"},
            {"name": "Scenic Viewpoint",   "description": "Stunning panoramic views of the city.", "entry_fee": "$5", "best_time": "Sunset"},
            {"name": "Cultural District",  "description": "Historic quarter with traditional architecture.", "entry_fee": "Free", "best_time": "Anytime"}
        ],
        "hotels": [
            {"name": "Grand City Hotel",    "rating": "5 stars", "price_per_night": "$200–300", "location": "City Center", "amenities": "Pool, Spa, Restaurant, WiFi"},
            {"name": "Boutique Heritage Inn","rating": "4 stars", "price_per_night": "$100–150", "location": "Old Town",    "amenities": "WiFi, Breakfast Included"},
            {"name": "Budget Traveler's Lodge","rating": "3 stars","price_per_night": "$40–70",  "location": "Near Transit","amenities": "WiFi, Common Kitchen"}
        ],
        "restaurants": [
            {"name": "The Local Table",  "cuisine": "Traditional Local", "price_range": "$$",  "specialty": "Signature regional dish", "location": "Old Town"},
            {"name": "Fusion Bistro",    "cuisine": "Modern Fusion",     "price_range": "$$$", "specialty": "Chef's tasting menu",     "location": "City Center"},
            {"name": "Street Food Lane", "cuisine": "Street Food",       "price_range": "$",   "specialty": "Local snacks & skewers",  "location": "Night Market"}
        ],
        "transportation": {
            "getting_there": "International flights available. Check major airlines for the best fares.",
            "local_transport": "Metro, buses, and taxis are widely available. Consider getting a travel card for unlimited rides.",
            "tips": "Download the local transport app for real-time schedules and route planning."
        },
        "budget_breakdown": {
            "accommodation":   "$150–400 total",
            "food":            "$80–200 total",
            "attractions":     "$50–100 total",
            "transportation":  "$40–100 total",
            "shopping":        "$50–200 total",
            "miscellaneous":   "$30–80 total",
            "total_estimated": f"$400–1,080 for {travelers} travelers"
        },
        "packing_checklist": {
            "documents":     ["Passport", "Visa (if required)", "Travel insurance", "Flight tickets", "Hotel bookings"],
            "clothing":      ["Comfortable walking shoes", "Weather-appropriate clothing", "Light jacket", "Formal outfit for dining"],
            "electronics":   ["Phone & charger", "Camera", "Universal power adapter", "Portable battery bank"],
            "health":        ["Prescribed medications", "Sunscreen SPF 50+", "Insect repellent", "First aid kit", "Hand sanitizer"],
            "miscellaneous": ["Reusable water bottle", "Travel pillow", "Guidebook or maps", "Snacks for travel", "Local currency cash"]
        },
        "safety_tips": [
            "Always keep copies of your passport and important documents in a separate bag.",
            "Use official taxis or ride-hailing apps; avoid unlicensed vehicles.",
            "Keep your belongings secure in crowded tourist areas — beware of pickpockets.",
            "Purchase comprehensive travel insurance before your trip.",
            "Share your itinerary with a trusted friend or family member at home.",
            "Stay aware of local laws, customs, and cultural sensitivities.",
            "Keep emergency contact numbers and your hotel address easily accessible."
        ],
        "emergency_contacts": {
            "police":    "Local emergency number (112 in most countries)",
            "ambulance": "Local ambulance number",
            "embassy":   "Check your country's embassy website for local contact details"
        }
    }
