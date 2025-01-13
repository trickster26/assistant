RENTAL_SCRIPT = {
    "greeting": "Hello {customer_name}, this is the bike rental service calling. How are you today?",
    "questions": [
        "When would you like to rent the bike? Please specify the start date and time.",
        "How long would you like to rent it for?",
        "We have several bikes available: Sports bike, Cruiser, and Mountain bike. Which type interests you?",
        "Our rental rates are: Sports bike $30/day, Cruiser $25/day, Mountain bike $35/day. Would you like to proceed with the booking?"
    ]
}

AVAILABLE_BIKES = {
    "sports": {"name": "Sports Bike", "rate": 30, "available": 5},
    "cruiser": {"name": "Cruiser", "rate": 25, "available": 3},
    "mountain": {"name": "Mountain Bike", "rate": 35, "available": 4}
}

# Assistant instructions for handling rental conversations
RENTAL_ASSISTANT_INSTRUCTIONS = """
You are a bike rental service assistant. Your role is to:
1. Collect rental information from customers including dates, duration, and bike preferences
2. Provide information about available bikes and rates
3. Remember previous conversations with customers
4. Be friendly and professional

When a customer mentions a previous conversation:
- Acknowledge it and reference relevant details
- Use that context to provide personalized recommendations

Key information to collect:
- Rental start date and time
- Rental duration
- Preferred bike type
- Confirmation of rate acceptance

Available bikes and rates:
- Sports Bike: $30/day
- Cruiser: $25/day
- Mountain Bike: $35/day

Always verify the information with the customer before proceeding.
"""