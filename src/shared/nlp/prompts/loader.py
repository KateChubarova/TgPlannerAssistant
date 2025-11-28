import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_yaml_prompts(name: str) -> dict:
    """
    Загружает YAML-файл с промптами по указанному имени и возвращает его содержимое.
    """
    file_path = PROMPTS_DIR / f"{name}.yaml"
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
