import os
import telebot

from sources.google_calendar.google_auth import build_auth_url
from rag.service import answer_with_rag
from shared.helper import get_message
from shared.storage.users_repo import get_user, create_user
from sources.google_calendar.google_calendar import load_all_events

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
def handle_start(message: telebot.types.Message):
    """
    Handle the /start command in the Telegram bot.

    This function initializes a user in the system and sends an authorization link for Google Calendar if the user
    has not authenticated yet.

    Args:
        message(telebot.types.Message): The Telegram message object that contains metadata about the user,
        chat, and the command that triggered the handler.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    user = get_user(user_id)
    if not user:
        user = create_user(
            user_id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username)
    if not user.google_access_token:
        auth_url = build_auth_url(user_id)
        bot.send_message(chat_id, f"Используй эту ссылку для логина в Google Calendar {auth_url} \n\n"
                                  f"Затем используй команду /sync")


@bot.message_handler(commands=["sync"])
def handle_sync(message: telebot.types.Message):
    """
    Handle the /sync command to synchronize a user's Google Calendar.

    This function retrieves the user's Google Calendar events, updates local
    storage with inserted/updated/deleted entries, and sends a summary
    message back to the user.

    Args:
        message (telebot.types.Message):  The Telegram message object containing user and chat information,
            including the command that triggered synchronization.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = get_user(user_id)
    try:
        inserted, updated, deleted = load_all_events(user)
        bot.send_message(
            chat_id,
            get_message(inserted, updated, deleted)
        )

    except Exception as e:
        print("Calendar sync error:", repr(e))
        bot.send_message(
            chat_id,
            "Не удалось синхронизировать календарь 😔\n"
            "Проверь настройки и попробуй ещё раз.",
        )


@bot.message_handler(content_types=["text"])
def process_message(message: telebot.types.Message):
    """
    Process incoming text messages and generate a response using the RAG system.

    This function passes the user's message into the retrieval-augmented
    generation pipeline to produce a reply, then sends that reply back
    to the user.

    Args:
        message (telebot.types.Message): The Telegram message object containing the text sent by the user
            along with metadata such as user ID and chat ID.
    """
    user_text = message.text
    user_id = message.from_user.id

    user = get_user(user_id)
    try:
        reply = answer_with_rag(user, user_text)
    except Exception as e:
        print("RAG error:", repr(e))
        reply = "У меня сейчас проблемы с доступом к данным. Попробуй ещё раз позже 🛠️"
    bot.send_message(
        message.chat.id,
        reply,
        parse_mode="Markdown"
    )


bot.infinity_polling()
