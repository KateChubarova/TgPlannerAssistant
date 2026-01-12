import os
from datetime import datetime

import tzlocal
from langsmith.wrappers import wrap_openai
from openai import OpenAI

from rag.prompts.loader import load_yaml_prompts

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")

prompts = load_yaml_prompts("prompt")
_base_client = OpenAI(api_key=OPENAI_TOKEN)
openai_client = wrap_openai(_base_client)

tz = tzlocal.get_localzone()
now = datetime.now(tz).isoformat(timespec="seconds")

system_prompt = prompts["system"].format(now=now, timezone=tz)
