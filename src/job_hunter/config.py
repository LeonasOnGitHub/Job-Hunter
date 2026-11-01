
import os
from pathlib import Path

import yaml


def load_profile() -> dict:
    project_root = Path(__file__).resolve().parents[2]
    default_path = project_root / "config" / "profile.yaml"

    profile_path = Path(
        os.getenv("JOB_HUNTER_PROFILE", str(default_path))
    )

    if not profile_path.is_absolute():
        profile_path = project_root / profile_path

    if not profile_path.exists():
        raise FileNotFoundError(
            f"Profil nicht gefunden: {profile_path}"
        )

    with profile_path.open("r", encoding="utf-8") as file:
        profile = yaml.safe_load(file)

    if not isinstance(profile, dict):
        raise ValueError(
            "profile.yaml muss ein YAML-Dictionary enthalten."
        )

    return profile


def get_openai_api_key() -> str:
    value = os.getenv("OPENAI_API_KEY")

    if not value:
        raise RuntimeError(
            "OPENAI_API_KEY ist nicht konfiguriert."
        )

    return value


def get_telegram_config() -> tuple[str, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID fehlt."
        )

    return token, chat_id
