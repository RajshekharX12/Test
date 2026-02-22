import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from SafoneAPI import SafoneAPI

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize API
api = SafoneAPI()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your AI assistant powered by SafoneAPI.\nSend me any message."
    )

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User: {user_message}")

    try:
        # Use chatbot() (async)
        response = await api.chatbot(user_message)

        if isinstance(response, dict) and response.get("success"):
            reply = response.get("response")
        else:
            reply = "AI failed to generate response."

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"ERROR: {e}")
        await update.message.reply_text("AI error occurred.")

def main():
    application = Application.builder().token(
        "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"
    ).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
