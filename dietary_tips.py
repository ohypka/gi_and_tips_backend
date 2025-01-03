import os
import openai
from utils import debug_log

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Raise an error if the OpenAI API key is not set
if not openai.api_key:
    raise EnvironmentError("OpenAI API key not found. Set 'OPENAI_API_KEY' environment variable.")

def generate_personalized_tips(ingredients):
    """
    Generates personalized tips to lower the glycemic index of a meal.

    The function constructs a prompt based on the ingredients provided, sends the prompt to OpenAI's API,
    and parses the response to generate three tips. If the API fails, fallback tips are returned.

    Args:
        ingredients (list of dict): A list of dictionaries, where each dictionary contains:
                                    - 'name' (str): The name of the ingredient.
                                    - 'weight' (float): The weight of the ingredient in grams.

    Returns:
        list: A list of three tips (strings) to lower the glycemic index of the meal.
    """
    try:
        # Debugging input to the function
        debug_log(f"Input to generate_personalized_tips: {ingredients}")

        # Create a string listing all ingredients with their weights
        ingredient_list = ", ".join([f"{ingredient['name']} ({ingredient['weight']}g)" for ingredient in ingredients])
        debug_log(f"Constructed ingredient list for prompt: {ingredient_list}")

        # Construct the prompt for the AI
        prompt = (
            f"The meal contains the following ingredients with their respective weights: {ingredient_list}. "
            f"Provide 3 short and specific tips to lower the glycemic index of this meal by suggesting alternative ingredients "
            f"or adjustments to the listed items. Each tip should start with a number (1., 2., 3.)."
        )
        debug_log(f"Constructed AI prompt: {prompt}")

        # Send the prompt to OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        debug_log(f"AI response received: {response}")

        # Extract content from the API response
        content = response["choices"][0]["message"]["content"]
        debug_log(f"Extracted content from AI response: {content}")

        # Split the response into lines and strip whitespace
        tips = [line.strip() for line in content.split("\n") if line.strip()]
        debug_log(f"Processed tips: {tips}")

        # Return exactly three tips
        return tips[:3]

    except Exception as e:
        # Debugging message for API errors
        debug_log(f"Error generating tips: {e}")

        # Fallback tips in case of an error
        return [
            "1. Add lean proteins like chicken or tofu.",
            "2. Include healthy fats like avocado or olive oil.",
            "3. Add more non-starchy vegetables like spinach or broccoli."
        ]

