from fastapi import FastAPI
import jwt
import os
from fastapi.responses import RedirectResponse
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Retrieve values from .env
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

# Ensure SECRET_KEY is a string (to avoid NoneType errors)
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the .env file!")

client = MongoClient(MONGO_URI)
db = client["secure_links_db"]
collection = db["links"]

@app.get("/")
def home():
    return {"message": "Secure Link API is running!"}

@app.get("/redirect")
def redirect_user(token: str):
    try:
        # Debugging: Print received token
        print(f"Received token: {token}")

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        chat_id = payload["chat_id"]

        # Fetch the link from MongoDB
        link_data = collection.find_one({"chat_id": chat_id})
        if link_data:
            return RedirectResponse(url=link_data["group_link"])  # Redirect to the actual group link

        return {"error": "Invalid or expired link"}
    
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
