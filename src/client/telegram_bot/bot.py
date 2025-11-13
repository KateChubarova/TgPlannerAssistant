import os
import telebot

from rag.service import answer_with_rag

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в .env")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


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
