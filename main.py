"""
Telegram bot for gpt4free - Fixed version (no Markdown, handles API key errors)
"""
import os
import logging
import asyncio
from typing import Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from g4f.client import Client
from g4f.errors import MissingAuthError
import nest_asyncio

nest_asyncio.apply()

# ================== CONFIGURATION ==================
BOT_TOKEN = "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"  # 🔁 Replace with your new token
DEFAULT_MODEL = "llama-3.1-70b"  # Changed to a model likely using free providers
ALLOWED_MODELS = {
    "gpt-4o-mini": "GPT-4o Mini (may need API key)",
    "llama-3.1-70b": "Llama 3.1 70B (free)",
    "gemini-1.5-pro": "Gemini 1.5 Pro (free)",
    "claude-3-haiku": "Claude 3 Haiku (free)",
    "flux": "Flux (image generation)",
}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

client = Client()

# ================== HELPER FUNCTIONS ==================
def get_user_model(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("model", DEFAULT_MODEL)

def set_user_model(context: ContextTypes.DEFAULT_TYPE, model: str):
    context.user_data["model"] = model

# ================== COMMAND HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome to GPT4Free Telegram Bot!\n\n"
        "Commands:\n"
        "/models - List available models\n"
        "/model <name> - Set your model\n"
        "/image <prompt> - Generate an image\n"
        "/current - Show current model\n"
        "/help - This message\n\n"
        "Just send any message and I'll reply using your selected model."
    )
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for model_id, desc in ALLOWED_MODELS.items():
        keyboard.append([InlineKeyboardButton(desc, callback_data=f"model_{model_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🧠 Available Models (click to select):",
        reply_markup=reply_markup
    )

async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /model <name>")
        return
    model_name = context.args[0].lower()
    matched = next((m for m in ALLOWED_MODELS if m.lower() == model_name), None)
    if matched:
        set_user_model(context, matched)
        await update.message.reply_text(f"✅ Model set to: {matched}")
    else:
        await update.message.reply_text(f"❌ Unknown model. Use /models to see list.")

async def show_current_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model = get_user_model(context)
    await update.message.reply_text(f"🔄 Current model: {model}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("model_"):
        model_id = query.data.replace("model_", "")
        if model_id in ALLOWED_MODELS:
            set_user_model(context, model_id)
            await query.edit_message_text(text=f"✅ Model set to: {model_id}")
        else:
            await query.edit_message_text(text="❌ Unknown model.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    model = get_user_model(context)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
        )
        reply_text = response.choices[0].message.content

        # Telegram message length limit: 4096 characters
        if len(reply_text) <= 4096:
            await update.message.reply_text(reply_text)
        else:
            for i in range(0, len(reply_text), 4096):
                await update.message.reply_text(reply_text[i:i+4096])

    except MissingAuthError:
        await update.message.reply_text(
            f"❌ The model '{model}' requires an API key.\n\n"
            "Try a different model with /models (e.g., llama-3.1-70b, gemini-1.5-pro)."
        )
    except Exception as e:
        logger.exception(f"g4f error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)[:200]}")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📷 Usage: /image <prompt>")
        return
    prompt = " ".join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
    try:
        response = client.images.generate(
            model="flux",
            prompt=prompt,
            response_format="url"
        )
        image_url = response.data[0].url
        await update.message.reply_photo(photo=image_url, caption=f"🎨 {prompt[:100]}")
    except Exception as e:
        logger.exception(f"Image error: {e}")
        await update.message.reply_text(f"❌ Failed to generate image: {str(e)[:200]}")

# ================== MAIN ==================
def main():
    if BOT_TOKEN == "YOUR_NEW_BOT_TOKEN_HERE":
        print("ERROR: Please set your BOT_TOKEN!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("models", list_models))
    app.add_handler(CommandHandler("model", set_model))
    app.add_handler(CommandHandler("current", show_current_model))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
