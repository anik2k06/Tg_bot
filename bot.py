import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

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
    
    # Initialize and run the Telegram Bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(ChatMemberHandler(greet_new_member, ChatMemberHandler.CHAT_MEMBER))
    
    logger.info("Starting Telegram polling...")
    application.run_polling(allowed_updates=[Update.CHAT_MEMBER])

if __name__ == "__main__":
    main()

