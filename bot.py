import logging
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import Bot
from fastapi.responses import JSONResponse

# Initialize the FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your Telegram bot token and set the webhook URL
BOT_TOKEN = "your-telegram-bot-token"
WEBHOOK_URL = "https://web-production-58a4.up.railway.app/webhook/" + BOT_TOKEN

# Create the bot and application instance
application = Application.builder().token(BOT_TOKEN).build()

# Define a simple start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! This is your bot.')

# Add a handler for the start command
application.add_handler(CommandHandler("start", start))

# Set webhook
async def set_webhook():
    # Set the webhook for your bot
    await application.bot.set_webhook(WEBHOOK_URL)

# Define FastAPI endpoint for the webhook
@app.post("/webhook/{bot_token}", response_model=None)
async def webhook(update: Update):
    # Process the incoming update
    await application.process_update(update)
    return JSONResponse(content={"status": "OK"}, status_code=200)

# Start the webhook setup when FastAPI runs
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
