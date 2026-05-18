import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes
import asyncio

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. Setup a minimal Flask app to satisfy Render's Web Service requirements
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render automatically assigns a PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Telegram Bot Logic
async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result.old_chat_member.status in ["left", "kicked", "none"] and result.new_chat_member.status == "member":
        user = result.new_chat_member.user
        user_mention = user.mention_markdown_v2()
        group_name = update.effective_chat.title
        
        escaped_group = group_name.replace("!", "\\!").replace("-", "\\-").replace(".", "\\.")
        welcome_text = f"👋 Welcome {user_mention} to *{escaped_group}*\\!\n\nPlease follow the rules\\."
        
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_text,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")


def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Start the web server in a separate background thread
    Thread(target=run_flask).start()
    
    # Initialize the Telegram Bot Application
    application = Application.builder().token(TOKEN).build()
    application.add_handler(ChatMemberHandler(greet_new_member, ChatMemberHandler.CHAT_MEMBER))
    
    logger.info("Starting Telegram polling...")
    
    # FIX: Explicitly handle the asyncio event loop lifecycle
    try:
        # Try to get the existing running loop (common in some IDE environments)
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If no loop exists, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    # Use the application's built-in initialization sequences safely
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())
    
    # Start checking for Telegram updates
    loop.create_task(application.updater.start_polling(allowed_updates=[Update.CHAT_MEMBER]))
    
    # Keep the main thread alive while the loop runs
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot...")
    finally:
        loop.run_until_complete(application.stop())
        loop.run_until_complete(application.shutdown())

if __name__ == "__main__":
    main()

