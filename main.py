import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from SafoneAPI import SafoneAPI

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize SafoneAPI client
api = SafoneAPI()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! I'm your AI assistant powered by SafoneAPI.\n"
        "Send me any message and I'll reply using AI."
    )

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    logger.info(f"User: {user_message}")

    try:
        # Call SafoneAPI's AI endpoint
        # Based on the library's structure, we assume a method like `ai` or `chat`
        # If it's different, adjust accordingly.
        # For example, the package might have `api.chat` or `api.gpt`.
        # Let's try `api.ai` (common naming) – you can check actual methods by printing dir(api)
        response = await api.ai(user_message)  # Adjust this line based on actual API
        # Assuming response is an object with a 'message' or 'text' field
        # Print the response to see its structure (optional, remove later)
        logger.info(f"API raw response: {response}")

        # Try to extract the reply text (common patterns)
        if hasattr(response, 'message'):
            reply = response.message
        elif hasattr(response, 'text'):
            reply = response.text
        elif isinstance(response, str):
            reply = response
        else:
            # If it's a dict or something else, try to get the most likely field
            reply = response.get('message') or response.get('text') or str(response)

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Sorry, I encountered an error. Please try again later.")

def main() -> None:
    # Create the Application
    application = Application.builder().token("8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE").build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
