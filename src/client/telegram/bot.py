import os

import telebot
from telebot import types

from rag.service import answer_with_rag
from shared.helper import get_message
from shared.storage.users_repo import create_user, get_user
from sources.google_calendar.google_auth import build_auth_url
from sources.google_calendar.google_calendar import load_all_events

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

LOGIN_BTN = "🔑 Залогиниться в Google Calendar"
SYNC_BTN = "🔄 Синхронизировать календарь"


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
    bot.send_message(
        chat_id,
        "Привет! Я — твой ассистент-планировщик. Я могу подсказать, что у тебя запланировано, во сколько встреча,"
        " где она проходит и многое другое. Сначала войди в Google Calendar, а затем синхронизируй календарь — после "
        "этого я смогу работать с твоим расписанием.",
        reply_markup=get_sync_bottom_menu(True),
    )


@bot.message_handler(func=lambda m: m.text == LOGIN_BTN)
def login_button_handler(message):
    """
    Handle the Google Calendar login button press.

    This handler initializes the user if necessary and sends an authorization
    link for Google Calendar when the user has not yet granted access.

    Args:
        message (telebot.types.Message): The Telegram message triggered by
            pressing the login button.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    user = get_user(user_id)
    if not user:
        user = create_user(
            user_id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
        )
    if not user.google_access_token:
        auth_url = build_auth_url(user_id)
        bot.send_message(
            chat_id,
            f'Авторизуйся в Google Calendar по ссылке: <a href="{auth_url}">Войти</a>',
            parse_mode="HTML",
        )


@bot.message_handler(func=lambda m: m.text == SYNC_BTN)
def sync_button_handler(message):
    """
    Handle synchronization requests triggered by the "Sync Calendar" button.

    This function retrieves the user's Google Calendar events, updates the local
    storage with inserted, updated, and deleted items, and sends a summary
    message back to the user. If synchronization fails, an explanatory error
    message is returned.

    Args:
        message (telebot.types.Message): The incoming Telegram message generated when the user presses
                the synchronization button.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = get_user(user_id)
    try:
        inserted, updated, deleted = load_all_events(user)
        bot.send_message(
            chat_id,
            get_message(inserted, updated, deleted),
            reply_markup=get_sync_bottom_menu(),
        )

    except Exception as e:
        print("Calendar sync error:", repr(e))
        bot.send_message(
            chat_id,
            "Не удалось синхронизировать календарь 😔\n"
            "Проверь настройки и попробуй ещё раз.",
            reply_markup=get_sync_bottom_menu(),
        )


@bot.message_handler(
    content_types=["text"], func=lambda m: m.text not in [LOGIN_BTN, SYNC_BTN]
)
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
        parse_mode="Markdown",
        reply_markup=get_sync_bottom_menu(),
    )


def get_sync_bottom_menu(is_login: bool = False) -> types.ReplyKeyboardMarkup:
    """
    Create a reply keyboard for calendar-related actions.

    Args:
        is_login (bool): Indicates whether the user needs to log in.
            If True, the "Log in to Google Calendar" button is shown.
            If False, only the synchronization button is displayed.

    Returns:
        ReplyKeyboardMarkup: A Telegram reply keyboard with one or two
        action buttons depending on the authentication state.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if is_login:
        login_to_calendar = types.KeyboardButton("🔑 Залогиниться в Google Calendar")
        keyboard.add(login_to_calendar)
    sync_calendar = types.KeyboardButton("🔄 Синхронизировать календарь")
    keyboard.add(sync_calendar)
    return keyboard


def run():
    bot.infinity_polling(skip_pending=True)
