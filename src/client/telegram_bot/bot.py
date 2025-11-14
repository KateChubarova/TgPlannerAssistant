import os
import telebot

from ingest.loaders.google_calendar_loader import load_all_events
from rag.service import answer_with_rag

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в .env")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
def handle_start(message: telebot.types.Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Сейчас синхронизирую твой Google Calendar...")

    try:
        count = load_all_events()
        bot.send_message(
            chat_id,
            f"Готово 🎉 Я загрузил {count} событий из календаря.\n"
            f"Теперь можешь спрашивать, например: «Что у меня на завтра?»",
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
    user_text = message.text or ""
    try:
        reply = answer_with_rag(user_text)
    except Exception as e:
        print("RAG error:", repr(e))
        reply = "У меня сейчас проблемы с доступом к данным. Попробуй ещё раз позже 🛠️"
    bot.send_message(message.chat.id, reply)


bot.infinity_polling()
