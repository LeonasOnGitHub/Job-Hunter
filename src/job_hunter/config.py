
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
        raise ValueError("profile.yaml muss ein YAML-Dictionary enthalten.")

    return profile
