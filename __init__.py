# __init__.py

import logging
from .bot import main
from .handlers import (
    start,
    show_emails,
    handle_document,
    show_calendar,
    add_event,
    handle_new_event,
    handle_email_selection,
    handle_response_selection,
    handle_confirmation,
    handle_event_selection,
    handle_summary_event_creation
)
from .gmail_auth import authenticate_google_services
from .google_calendar import list_calendar_events, create_calendar_event
from .document_summary import summarize_word_document
from .email_utils import list_emails, generate_summary, generate_ai_response, send_email

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
