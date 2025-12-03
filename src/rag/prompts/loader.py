import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_yaml_prompts(name: str) -> dict:
    file_path = PROMPTS_DIR / f"{name}.yaml"
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
