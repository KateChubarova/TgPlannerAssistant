import os
from datetime import datetime

from langsmith.wrappers import wrap_openai
from openai import OpenAI

from rag.prompts.loader import load_yaml_prompts

WEEKDAY_RU = [
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
]

day = WEEKDAY_RU[datetime.now().weekday()]

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")

prompts = load_yaml_prompts("prompt")
_base_client = OpenAI(api_key=OPENAI_TOKEN)
openai_client = wrap_openai(_base_client)

system_prompt = prompts["system"].format(
    now=datetime.now(), day_of_week=WEEKDAY_RU[datetime.now().weekday()]
)
