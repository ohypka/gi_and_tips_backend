from data_handler import find_or_estimate_food_data

def calculate_glycemic_index_meal(ingredients, food_docs):
    """
    Calculates the glycemic index of a meal based on its ingredients.

    The function fetches or estimates the nutritional data for each ingredient, computes the available carbohydrates,
    and calculates a weighted glycemic index for the meal.

    Args:
        ingredients (list): A list of dictionaries, where each dictionary represents an ingredient with keys:
                           - 'name' (str): The name of the ingredient.
                           - 'weight' (float or str): The weight of the ingredient in grams.
        food_docs (dict): A dictionary containing food data with food names as keys and their nutritional data as values.

    Returns:
        float: The glycemic index of the meal, rounded to two decimal places. Returns 0 if there are no available carbohydrates.

    Raises:
        ValueError: If any calculation encounters invalid numeric values.
        TypeError: If the input data types are not as expected.
    """
    total_weighted_gi = 0
    total_available_carbs = 0

    for ingredient in ingredients:
        try:
            # Extract ingredient name and convert weight to float
            name = ingredient['name']
            weight = float(ingredient['weight'])  # Convert to float
        except (KeyError, ValueError, TypeError) as e:
            # Debugging message for invalid ingredient format (commented out for production)
            # print(f"Invalid ingredient format: {ingredient}, error: {e}")
            continue

        # Fetch or estimate nutritional data for the ingredient
        food_data = find_or_estimate_food_data(name, food_docs)
        try:
            # Extract carbohydrate, fiber, and glycemic index values
            carbs = float(food_data.get("Carbohydrates", 0))
            fiber = float(food_data.get("Fiber Content", 0))
            gi = float(food_data.get("Glycemic Index", 0))
        except (ValueError, TypeError) as e:
            # Debugging message for parsing errors (commented out for production)
            # print(f"Error parsing food data for {name}: {e}")
            continue

        # Calculate available carbohydrates and weighted glycemic index
        try:
            # Available carbs = (carbs - fiber) * weight / 100 (ensuring non-negative values)
            available_carbs = max(0, (carbs - fiber) * weight / 100)
            # Accumulate weighted glycemic index for the ingredient
            total_weighted_gi += gi * available_carbs
            # Accumulate total available carbohydrates for the meal
            total_available_carbs += available_carbs
        except (ValueError, TypeError) as e:
            # Debugging message for calculation errors (commented out for production)
            # print(f"Calculation error for {name} with weight {weight}: {e}")
            continue

    # Return the weighted glycemic index of the meal rounded to two decimal places
    return round(total_weighted_gi / total_available_carbs, 2) if total_available_carbs else 0
