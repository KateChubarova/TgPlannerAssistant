import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_yaml_prompts(name: str) -> dict:
    """
    Load a YAML prompt file by name and return its parsed contents.

    This function constructs the file path for the YAML prompt, opens it,
    and loads its content into a Python dictionary.

    Args:
        name (str): The base name of the YAML file (without extension) to load.

    Return:
         dict: A dictionary containing the parsed YAML data from the prompt file.
    """
    file_path = PROMPTS_DIR / f"{name}.yaml"
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
