import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from SafoneAPI import SafoneAPI

# ===== CONFIG =====
BOT_TOKEN = "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"

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
    await update.message.reply_text("ChatGPT mode activated.")

# ===== Handle Messages =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User: {user_message}")

    try:
        # Correct Safone ChatGPT call
        resp = await api.chatgpt(user_message)

        # Safely extract response
        reply = resp.response if hasattr(resp, "response") else str(resp)

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"ERROR: {e}")
        await update.message.reply_text("AI error occurred.")

# ===== Main =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
