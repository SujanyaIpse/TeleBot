import os
import jwt
import time
import logging
import pymongo
import certifi
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB setup
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["secure_links_db"]
collection = db["links"]

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key for JWT tokens
SECRET_KEY = "your_super_secret_key"

# FastAPI app
app = FastAPI()

# Define start command for the Telegram bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text("Send /getlink <your-private-group-link> to generate a secure link.")

# Define get_link command to generate a secure link
async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a secure link dynamically for any provided private group link"""
    if not context.args:
        await update.message.reply_text("Usage: /getlink <private_group_link>")
        return

    private_group_link = context.args[0]
    chat_id = update.message.chat_id
    timestamp = int(time.time()) + 600  # Link expires in 10 minutes

    # Generate JWT token
    token = jwt.encode({"chat_id": chat_id, "group_link": private_group_link, "exp": timestamp}, SECRET_KEY, algorithm="HS256")
    secure_link = f"https://your-deployed-app-url.com/redirect?token={token}"

    # Store in DB
    collection.insert_one({"chat_id": chat_id, "link": secure_link, "expiry": timestamp, "group_link": private_group_link})

    await update.message.reply_text(f"Your secure link: {secure_link} (Expires in 10 mins)")

# Define FastAPI route for webhook
@app.post("/webhook/{bot_token}")
async def webhook(update: Update):
    """Process incoming updates from Telegram"""
    # Ensure the bot token matches the URL token
    if bot_token != BOT_TOKEN:
        return JSONResponse(content={"error": "Invalid bot token"}, status_code=400)

    # Process the update with your existing bot logic
    await application.process_update(update)

    return JSONResponse(content={"status": "OK"}, status_code=200)

# Main function to run the Telegram bot
def main():
    """Start the bot"""
    # Set up the bot application with your existing bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getlink", get_link))

    # Run the bot (polling)
    logger.info("Bot is running...")
    application.run_polling()

# Ensure webhook is set up
async def set_webhook():
    webhook_url = f"https://your-deployed-app-url.com/webhook/{BOT_TOKEN}"
    await application.bot.set_webhook(webhook_url)

if __name__ == "__main__":
    # Run the FastAPI app in one thread, and set the webhook in another thread
    import uvicorn
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())  # Set the webhook for the bot

    # Start FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
