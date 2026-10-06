import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    google_api_key: str
    model_name: str
    sqlite_path: str
    recursion_limit: int


def load_settings() -> Settings:
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise RuntimeError("Falta GOOGLE_API_KEY en el archivo .env")
    return Settings(
        google_api_key=api_key,
        model_name=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        sqlite_path=os.getenv("SQLITE_PATH", "checkpoints.db"),
        recursion_limit=int(os.getenv("RECURSION_LIMIT", "10")),
    )