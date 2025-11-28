import os
import telebot

from ingest.loaders.google_calendar_loader import load_all_events
from ingest.providers.google_auth import build_auth_url_for_user
from rag.service import answer_with_rag
from shared.db import SessionLocal
from shared.storage.users_repo import get_user, create_user

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def _get_message(inserted, updated, deleted) -> str:
    """
    Формирует текст отчёта о результатах синхронизации календаря
    (добавленные, обновлённые и удалённые события).
    """
    message = "Готово! ✨ Я синхронизировал твой календарь:\n"

    if inserted > 0:
        message += f"• ➕ Добавил: {inserted}\n"

    if updated > 0:
        message += f"• 🔄 Обновил: {updated}\n"

    if deleted > 0:
        message += f"• ➖ Убрал: {deleted}\n"

    return message


@bot.message_handler(commands=["start"])
def handle_start(message: telebot.types.Message):
    """
    Обрабатывает команду /start: создаёт пользователя при необходимости и отправляет ссылку для авторизации в
    Google Calendar, если токен отсутствует.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    with SessionLocal() as session:
        user = get_user(session, user_id)
        if not user:
            user = create_user(
                user_id,
                message.from_user.first_name,
                message.from_user.last_name,
                message.from_user.username)
        if not user.google_access_token:
            auth_url = build_auth_url_for_user(user_id)
            bot.send_message(chat_id, f"Используй эту ссылку для логина в Google Calendar {auth_url} \n\n"
                                      f"Затем используй команду /sync")


@bot.message_handler(commands=["sync"])
def handle_sync(message: telebot.types.Message):
    """
    Обрабатывает команду / sync: запускает синхронизацию календаря пользователя и
    отправляет сообщение с результатами.
    """
    with SessionLocal() as session:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user = get_user(session, user_id)
        try:
            inserted, updated, deleted = load_all_events(user)
            bot.send_message(
                chat_id,
                _get_message(inserted, updated, deleted)
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
    Обрабатывает входящие текстовые сообщения: передаёт текст в RAG и отправляет пользователю ответ.
    """
    user_text = message.text
    user_id = message.from_user.id

    with SessionLocal() as session:
        user = get_user(session, user_id)
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
