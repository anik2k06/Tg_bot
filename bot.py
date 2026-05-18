import os
import logging
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes

# Enable logging to track bot activity and errors
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detects when a user joins the group and sends a stylized welcome message."""
    result = update.chat_member
    
    # Check if the status updated from 'left/none' to an active 'member'
    if result.old_chat_member.status in ["left", "kicked", "none"] and result.new_chat_member.status == "member":
        user = result.new_chat_member.user
        user_mention = user.mention_markdown_v2() # Safely handles special characters in usernames
        group_name = update.effective_chat.title
        
        # Escape special characters for Telegram's MarkdownV2 formatting
        escaped_group = group_name.replace("!", "\\!").replace("-", "\\-").replace(".", "\\.")
        
        welcome_text = (
            f"👋 Welcome {user_mention} to *{escaped_group}*\\!\n\n"
            f"Please read the pinned messages and follow the rules\\."
        )
        
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_text,
                parse_mode="MarkdownV2"
            )
            logger.info(f"Greeted {user.first_name} in chat {group_name}")
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")

def main():
    # Looks for a cloud environment variable first, falls back to local testing string
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_LOCAL_TESTING_TOKEN_HERE")
    
    if TOKEN == "YOUR_LOCAL_TESTING_TOKEN_HERE" or not TOKEN:
        logger.warning("Running with default local token. Replace with your actual BotFather token.")

    # Initialize the application
    application = Application.builder().token(TOKEN).build()
    
    # Listen explicitly for chat member status changes
    application.add_handler(ChatMemberHandler(greet_new_member, ChatMemberHandler.CHAT_MEMBER))
    
    # Start the bot via long polling
    logger.info("Bot service initialized. Polling started...")
    application.run_polling(allowed_updates=[Update.CHAT_MEMBER])

if __name__ == "__main__":
    main()

