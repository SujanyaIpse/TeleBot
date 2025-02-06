import os
import jwt
import time
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key for JWT tokens
SECRET_KEY = "your_super_secret_key"

# FastAPI or any external URL you deploy your app to
your_deployed_app_url = "your-deployed-app-url.com"  # Replace this with your actual deployed URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text("Send /getlink <your-private-group-link> to generate a secure link.")

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
    secure_link = f"https://{your_deployed_app_url}/redirect?token={token}"

    await update.message.reply_text(f"Your secure link: {secure_link} (Expires in 10 mins)")

async def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Set webhook URL
    webhook_url = f"https://{your_deployed_app_url}/webhook/{BOT_TOKEN}"  # Ensure it's HTTPS
    await application.bot.set_webhook(webhook_url)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getlink", get_link))

    logger.info("Bot is running with webhook.")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
