import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from SafoneAPI import SafoneAPI

# ⚠️ REPLACE THIS AFTER YOU REVOKE IT
BOT_TOKEN = "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

api = SafoneAPI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ChatGPT mode activated. Send me anything.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        resp = await api.chatgpt(user_message)

        # SafoneAPI usually returns object with .response
        if hasattr(resp, "response"):
            reply = resp.response
        else:
            reply = str(resp)

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
