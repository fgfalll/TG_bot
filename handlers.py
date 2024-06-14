from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from document_summary import summarize_word_document
from google_calendar import list_calendar_events, create_calendar_event
from email_utils import list_emails, generate_summary, generate_ai_response, send_email
import os

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Type "Can you show me emails" to get started, send a Word document to summarize, or type "Show my calendar" to list your calendar events.')

def show_emails(update: Update, context: CallbackContext) -> None:
    emails = list_emails()
    if not emails:
        update.message.reply_text('No emails found.')
        return

    context.user_data['emails'] = emails

    keyboard = [[InlineKeyboardButton(email, callback_data=str(idx))] for idx, email in enumerate(emails)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Here are your emails:', reply_markup=reply_markup)

def handle_email_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    email_idx = int(query.data)
    selected_email = context.user_data['emails'][email_idx]
    context.user_data['selected_email'] = selected_email

    summary = generate_summary(selected_email)
    context.user_data['summary'] = summary
    update.effective_message.reply_text(f"Summary of the selected email:\n\n{summary}")

    keyboard = [
        [InlineKeyboardButton("Response 1", callback_data="response_1")],
        [InlineKeyboardButton("Response 2", callback_data="response_2")],
        [InlineKeyboardButton("Create Calendar Event", callback_data="create_event_from_summary")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(text="Choose an action:", reply_markup=reply_markup)

def handle_response_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    response_idx = int(query.data.split('_')[1])
    selected_response = context.user_data['response_options'][response_idx]
    context.user_data['selected_response'] = selected_response

    keyboard = [
        [InlineKeyboardButton("Yes", callback_data="confirm_yes")],
        [InlineKeyboardButton("No", callback_data="confirm_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Do you want to send this response?\n\n{selected_response}", reply_markup=reply_markup)

def handle_confirmation(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == "confirm_yes":
        send_email(context.user_data['selected_email'], context.user_data['selected_response'])
        query.edit_message_text(text="The response has been sent.")
    else:
        query.edit_message_text(text="Response not sent.")

def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    file_path = f"{document.file_id}.docx"
    document.get_file().download(file_path)

    summary = summarize_word_document(file_path)
    context.user_data['summary'] = summary
    os.remove(file_path)

    keyboard = [
        [InlineKeyboardButton("Create Calendar Event", callback_data="create_event_from_summary")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Summary of the document:\n\n{summary}", reply_markup=reply_markup)

def handle_summary_event_creation(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    summary = context.user_data['summary']
    update.effective_message.reply_text(f"Creating a calendar event from the summary:\n\n{summary}\n\nPlease provide the event details in the format: Title, Date (YYYY-MM-DD), Time (HH:MM), Duration (minutes)")

    context.user_data['add_event_from_summary'] = True

def show_calendar(update: Update, context: CallbackContext) -> None:
    events = list_calendar_events()
    if not events:
        update.message.reply_text('No upcoming events found.')
        return

    context.user_data['calendar_events'] = events

    keyboard = [[InlineKeyboardButton(event, callback_data=str(idx))] for idx, event in enumerate(events)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Here are your upcoming events:', reply_markup=reply_markup)

def handle_event_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    event_idx = int(query.data)
    selected_event = context.user_data['calendar_events'][event_idx]
    context.user_data['selected_event'] = selected_event

    update.effective_message.reply_text(f"You selected the event:\n\n{selected_event}")

def add_event(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Please provide the event details in the format: Title, Date (YYYY-MM-DD), Time (HH:MM), Duration (minutes)')
    context.user_data['add_event'] = True

def handle_new_event(update: Update, context: CallbackContext) -> None:
    if 'add_event' in context.user_data and context.user_data['add_event']:
        context.user_data['add_event'] = False
    elif 'add_event_from_summary' in context.user_data and context.user_data['add_event_from_summary']:
        context.user_data['add_event_from_summary'] = False

        event_details = update.message.text.split(',')
        if len(event_details) != 4:
            update.message.reply_text('Invalid format. Please provide the event details in the format: Title, Date (YYYY-MM-DD), Time (HH:MM), Duration (minutes)')
            return

        title, date, time, duration = event_details
        try:
            create_calendar_event(title.strip(), date.strip(), time.strip(), int(duration.strip()), context.user_data.get('summary', ''))
            update.message.reply_text('Event added to your calendar.')
        except Exception as error:
            update.message.reply_text(f"An error occurred: {error}")
