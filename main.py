from flask import Flask, request, jsonify
from data_handler import fetch_all_food_docs
from gi_calculator import calculate_glycemic_index_meal
from dietary_tips import generate_personalized_tips
from utils import debug_log

app = Flask(__name__)

# Debugging flag
DEBUG_MODE = True

def debug_log(message):
    """
    Prints debug messages if DEBUG_MODE is enabled.

    Args:
        message (str): The debug message to print.
    """
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

# Endpoint for calculating glycemic index (GI) and generating recommendations
@app.route('/process-meal', methods=['POST'])
def process_meal():
    """
    Processes a meal by calculating its glycemic index and generating dietary tips.

    This endpoint accepts a JSON payload containing a list of ingredients with their weights,
    fetches food data from the database, calculates the glycemic index of the meal,
    and generates personalized tips to lower its glycemic index.

    Returns:
        JSON response:
            - glycemicIndex (float): The calculated glycemic index of the meal.
            - recommendations (list): A list of dietary tips.
    """
    try:
        # Parse incoming JSON request
        data = request.json
        debug_log(f"Received data: {data}")

        # Extract ingredients from the request payload
        user_ingredients = data.get('ingredients', [])
        debug_log(f"User ingredients: {user_ingredients}")

        if not user_ingredients:
            return jsonify({"error": "Ingredients are required"}), 400

        # Fetch food documents from the database
        food_documents = fetch_all_food_docs()
        debug_log(f"Fetched food documents: {food_documents}")

        # Calculate the glycemic index of the meal
        meal_gi = calculate_glycemic_index_meal(user_ingredients, food_documents)
        debug_log(f"Calculated glycemic index: {meal_gi}")

        # Generate personalized dietary tips
        tips = generate_personalized_tips(user_ingredients)
        debug_log(f"Generated tips: {tips}")

        # Return the calculated glycemic index and tips
        response = {
            "glycemicIndex": round(meal_gi, 2),
            "recommendations": tips
        }
        debug_log(f"Response: {response}")

        return jsonify(response)

    except Exception as e:
        # Handle exceptions and return a meaningful error response
        debug_log(f"Error in process-meal: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """
    Health check endpoint to verify if the server is running.

    Returns:
        str: A message indicating the server is running.
        int: HTTP status code 200.
    """
    debug_log("Index endpoint accessed.")
    return "Server is running!", 200

if __name__ == "__main__":
    debug_log("Starting Flask server...")
    app.run(debug=True)
