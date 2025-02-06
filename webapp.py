from fastapi import FastAPI
import jwt
import os
from fastapi.responses import RedirectResponse
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up FastAPI app
app = FastAPI()

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["secure_links_db"]
collection = db["links"]

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def home():
    return {"message": "Secure Link API is running!"}

@app.get("/redirect")
def redirect_user(token: str):
    try:
        # Decode the JWT token
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

if __name__ == "__main__":
    import uvicorn
    # Get the dynamic port from Railway's environment variable or use 8080 by default
    port = int(os.getenv("PORT", 8080))

    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
