import os
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Initialize Firebase Admin
try:
    cred = credentials.Certificate("glycemicassist-cc328-firebase-adminsdk-wl77v-bc74e4d7f2.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    # Debugging: Successful Firebase connection
    # print("Firebase connection established successfully.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OpenAI API key not found.")

def fetch_all_food_docs():
    try:
        docs = db.collection("DiabetesFoodDataset").stream()
        food_docs = {doc.id: doc.to_dict().get("Food Name", "") for doc in docs}
        # Debugging: Fetched food documents
        # print("Fetched food documents:", food_docs)
        return food_docs
    except Exception as e:
        print(f"Error fetching food documents: {e}")
        return {}

def fetch_food_data_by_id(doc_id):
    try:
        doc = db.collection("DiabetesFoodDataset").document(doc_id).get()
        if not doc.exists:
            print(f"Document with ID {doc_id} does not exist.")
            return None

        data = doc.to_dict()
        required_fields = ["Carbohydrates", "Fiber Content", "Glycemic Index"]
        if not all(field in data and data[field] for field in required_fields):
            print(f"Document with ID {doc_id} has incomplete data: {data}")
            return None

        return data
    except Exception as e:
        print(f"Error fetching data for document ID {doc_id}: {e}")
        return None

def find_or_estimate_food_data(name, food_docs):
    # Debugging: Search initiation
    # print(f"Searching for: {name}")
    matching_doc_id = next(
        (doc_id for doc_id, food_name in food_docs.items()
         if isinstance(food_name, str) and food_name.lower() == name.lower()),
        None
    )
    # Debugging: Matching document ID
    # print(f"Matching doc ID: {matching_doc_id}")

    if matching_doc_id:
        data = fetch_food_data_by_id(matching_doc_id)
        # Debugging: Data fetched from database
        # print(f"Data fetched from database: {data}")
        if data:
            try:
                return {
                    "Carbohydrates": float(data.get("Carbohydrates", 0)),
                    "Fiber Content": float(data.get("Fiber Content", 0)),
                    "Glycemic Index": float(data.get("Glycemic Index", 0))
                }
            except ValueError as e:
                print(f"Error converting data for {name}: {e}")

    # Debugging: Data estimation
    # print(f"Estimating data for: {name}")
    estimated_data = estimate_food_data_with_ai(name)
    # Debugging: Estimated data
    # print(f"Estimated data: {estimated_data}")
    return estimated_data

def estimate_food_data_with_ai(input_name):
    prompt = (
        f"Provide the estimated glycemic index (GI), carbohydrates (in grams), "
        f"and fiber content (in grams) for 100g of '{input_name}' in the following JSON format:\n"
        f"{{\n"
        f'  "Glycemic Index": <GI>,\n'
        f'  "Carbohydrates": <Carbs>,\n'
        f'  "Fiber Content": <Fiber>\n'
        f"}}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        content = response['choices'][0]['message']['content']
        # Debugging: AI response
        # print(f"AI response: {content}")

        # Remove formatting markers
        if content.startswith("```json"):
            content = content[7:]  # Removes "```json\n"
        if content.endswith("```"):
            content = content[:-3]  # Removes "```"

        # Parse JSON response
        estimated_data = json.loads(content.strip())

        # Convert to expected format
        return {
            "Carbohydrates": float(estimated_data.get("Carbohydrates", 0)),
            "Fiber Content": float(estimated_data.get("Fiber Content", 0)),
            "Glycemic Index": float(estimated_data.get("Glycemic Index", 0))
        }
    except Exception as e:
        print(f"Error estimating data for {input_name}: {e}")
        return {
            "Carbohydrates": 10.0,
            "Fiber Content": 1.5,
            "Glycemic Index": 50.0
        }
