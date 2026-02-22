import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from SafoneAPI import SafoneAPI

# ===== Logging =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== Initialize SafoneAPI =====
api = SafoneAPI()

# ===== /start Command =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your AI assistant powered by SafoneAPI.\nSend me any message."
    )

# ===== Handle Messages =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User: {user_message}")

    try:
        # chatbot() is async in your version
        response = await api.chatbot(user_message)

        # SafoneAPI returns dict with "response"
        if isinstance(response, dict) and response.get("success"):
            reply = response.get("response")
        else:
            reply = "AI failed to generate response."

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"ERROR: {e}")
        await update.message.reply_text("AI error occurred.")

# ===== Main =====
def main():
    application = Application.builder().token(
        "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"
    ).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
