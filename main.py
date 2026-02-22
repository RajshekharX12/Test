"""
Telegram bot for gpt4free - Access multiple LLM models via Telegram
Author: Based on g4f community project
Requirements: pip install python-telegram-bot==20.7 g4f[all] nest-asyncio
"""
import os
import logging
import asyncio
from typing import Dict, Optional
from functools import wraps

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
from g4f import models
import nest_asyncio

# Apply nest_asyncio to allow nested event loops (useful for some environments)
nest_asyncio.apply()

# ================== CONFIGURATION ==================
BOT_TOKEN = "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"  # Replace with your actual token
DEFAULT_MODEL = "gpt-4o-mini"
ALLOWED_MODELS = {
    "gpt-4o-mini": "GPT-4o Mini (fast, general)",
    "gpt-4o": "GPT-4o (powerful)",
    "claude-3-haiku": "Claude 3 Haiku",
    "llama-3.1-70b": "Llama 3.1 70B",
    "gemini-1.5-pro": "Gemini 1.5 Pro",
    "deepseek-v3": "DeepSeek v3",
    "flux": "Flux (image generation)",
    "dall-e-3": "DALL-E 3 (image generation)",
}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize g4f client
client = Client()

# ================== HELPER FUNCTIONS ==================
def get_user_model(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get the current model for a user, or default."""
    return context.user_data.get("model", DEFAULT_MODEL)

def set_user_model(context: ContextTypes.DEFAULT_TYPE, model: str):
    """Set the model for a user."""
    context.user_data["model"] = model

def error_handler(func):
    """Decorator to handle exceptions gracefully."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            await update.message.reply_text(
                f"❌ An error occurred: {str(e)[:200]}\n\nPlease try again later."
            )
    return wrapper

# ================== COMMAND HANDLERS ==================
@error_handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    welcome_text = (
        "👋 *Welcome to GPT4Free Telegram Bot!*\n\n"
        "I provide free access to multiple AI models including GPT-4, Claude, Gemini, and more.\n\n"
        "📌 *Commands:*\n"
        "/models - List available models\n"
        "/model <name> - Set your preferred model (e.g., /model gpt-4o-mini)\n"
        "/image <prompt> - Generate an image (uses flux or dalle)\n"
        "/current - Show your current model\n"
        "/help - Show this help\n\n"
        "Just send me any message and I'll reply using your selected model!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

@error_handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    await start(update, context)

@error_handler
async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available models with inline buttons to select."""
    keyboard = []
    for model_id, desc in ALLOWED_MODELS.items():
        keyboard.append([InlineKeyboardButton(desc, callback_data=f"model_{model_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🧠 *Available Models*\n\nClick a model to select it:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

@error_handler
async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set model via command: /model <name>"""
    if not context.args:
        await update.message.reply_text(
            f"⚠️ Please specify a model name.\nExample: `/model gpt-4o-mini`\n\nSee /models for list.",
            parse_mode="Markdown"
        )
        return

    model_name = context.args[0].lower()
    # Find best match (case-insensitive)
    matched = next((m for m in ALLOWED_MODELS if m.lower() == model_name), None)

    if matched:
        set_user_model(context, matched)
        await update.message.reply_text(
            f"✅ Model set to *{matched}*: {ALLOWED_MODELS[matched]}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ Model '{model_name}' not found. Use /models to see available models."
        )

@error_handler
async def show_current_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the user's current model."""
    model = get_user_model(context)
    desc = ALLOWED_MODELS.get(model, "Unknown")
    await update.message.reply_text(
        f"🔄 Your current model: *{model}*\n{desc}",
        parse_mode="Markdown"
    )

@error_handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses (model selection)."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("model_"):
        model_id = query.data.replace("model_", "")
        if model_id in ALLOWED_MODELS:
            set_user_model(context, model_id)
            await query.edit_message_text(
                text=f"✅ Model set to *{model_id}*: {ALLOWED_MODELS[model_id]}",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(text="❌ Unknown model.")

@error_handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process text messages and generate AI responses."""
    user_input = update.message.text
    model = get_user_model(context)

    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Call g4f client
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            web_search=False,  # Can be enabled for models that support it
        )
        reply_text = response.choices[0].message.content

        # Split long messages if needed (Telegram limit: 4096 chars)
        if len(reply_text) <= 4096:
            await update.message.reply_text(reply_text)
        else:
            # Split into multiple messages
            for i in range(0, len(reply_text), 4096):
                await update.message.reply_text(reply_text[i:i+4096])

    except Exception as e:
        logger.error(f"g4f error with model {model}: {e}")
        await update.message.reply_text(
            f"❌ Error with model *{model}*: {str(e)[:200]}\n\nTry switching models with /models",
            parse_mode="Markdown"
        )

@error_handler
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate an image from a prompt."""
    if not context.args:
        await update.message.reply_text(
            "📷 Please provide a prompt.\nExample: `/image a beautiful sunset over mountains`",
            parse_mode="Markdown"
        )
        return

    prompt = " ".join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")

    try:
        # Try flux first, fallback to dalle
        response = client.images.generate(
            model="flux",
            prompt=prompt,
            response_format="url"
        )
        image_url = response.data[0].url

        await update.message.reply_photo(
            photo=image_url,
            caption=f"🎨 Generated image for: {prompt[:100]}"
        )
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await update.message.reply_text(
            f"❌ Failed to generate image: {str(e)[:200]}"
        )

# ================== MAIN ==================
def main():
    """Start the bot."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("ERROR: Please set your BOT_TOKEN in the script!")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("models", list_models))
    application.add_handler(CommandHandler("model", set_model))
    application.add_handler(CommandHandler("current", show_current_model))
    application.add_handler(CommandHandler("image", image_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    print("🤖 Bot is starting... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
