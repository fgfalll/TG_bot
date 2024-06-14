import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from email_utils import list_emails, send_email
from gmail_auth import authenticate_google_services
from google_calendar import create_calendar_event
from document_summary import summarize_word_document

# Define your bot token
TOKEN = '7229543975:AAGQ4Q-W9zNIWP-rQjBPzr4SusNvrQrVljY'

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your assistant bot. How can I help you today?')

def show_emails(update: Update, context: CallbackContext) -> None:
    try:
        # Retrieve emails using Gmail API service
        gmail_service = authenticate_google_services
        emails = list_emails(gmail_service)

        if not emails:
            update.message.reply_text("No unread emails found.")
            return

        email_list = "\n".join(f"{i+1}. {email['subject']}" for i, email in enumerate(emails))
        update.message.reply_text(f"Here are your emails:\n{email_list}")

    except Exception as e:
        logger.error(f"An error occurred while fetching emails: {e}")
        update.message.reply_text("Error fetching emails. Please try again later.")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'Can you show me emails'), show_emails))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()