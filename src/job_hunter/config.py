import os
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = PROJECT_ROOT / "config" / "profile.yaml"


def load_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    """Load the user profile from YAML."""

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError("Profile configuration must be a YAML object.")

    return data


def get_openai_api_key() -> str:
    value = os.getenv("OPENAI_API_KEY")

    if not value:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return value


def get_telegram_config() -> tuple[str, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not configured."
        )

    if not chat_id:
        raise RuntimeError(
            "TELEGRAM_CHAT_ID is not configured."
        )

    return token, chat_id