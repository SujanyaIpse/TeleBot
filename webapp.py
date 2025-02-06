from fastapi import FastAPI
import jwt
import os
from fastapi.responses import RedirectResponse
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

client = MongoClient(MONGO_URI)
db = client["secure_links_db"]
collection = db["links"]

@app.get("/")
def home():
    return {"message": "Secure Link API is running!"}

@app.get("/redirect")
def redirect_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        chat_id = payload["chat_id"]

        # Fetch the link from MongoDB
        link_data = collection.find_one({"chat_id": chat_id})
        if link_data:
            return RedirectResponse(url=link_data["link"])

        return {"error": "Invalid or expired link"}
    
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
