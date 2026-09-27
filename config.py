"""Загрузка настроек консольного AI-ассистента."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ConfigurationError(ValueError):
    """Ошибка конфигурации приложения."""


def load_env_file(path: Path) -> None:
    """Загрузить простой KEY=VALUE-файл, не перезаписывая переменные окружения."""
    if not path.exists():
        return

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigurationError(
                f"Неверная строка {line_number} в {path.name}: ожидается KEY=VALUE"
            )
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value[:1] == value[-1:] and value.startswith(("'", '"')):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _positive_int(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} должен быть целым числом") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} должен быть больше нуля")
    return value


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    normal_model: str
    thinking_model: str
    system_prompt: str
    timeout_seconds: int
    max_output_tokens: int
    max_history_messages: int
    history_file: Path
    log_level: str

    @classmethod
    def from_env(cls, env_path: Optional[Path] = None) -> "Settings":
        project_dir = Path(__file__).resolve().parent
        load_env_file(env_path or project_dir / ".env")

        api_key = os.getenv("PROXYAPI_KEY", "").strip()
        if not api_key or api_key == "your_proxyapi_key_here":
            raise ConfigurationError(
                "Не задан PROXYAPI_KEY. Скопируйте .env.example в .env и добавьте ключ."
            )

        history_value = os.getenv("HISTORY_FILE", "history.json").strip()
        history_file = Path(history_value)
        if not history_file.is_absolute():
            history_file = project_dir / history_file

        return cls(
            api_key=api_key,
            base_url=os.getenv("PROXYAPI_BASE_URL", "https://api.proxyapi.ru/v1").rstrip("/"),
            normal_model=os.getenv("NORMAL_MODEL", "openai/gpt-6-luna"),
            thinking_model=os.getenv("THINKING_MODEL", "anthropic/claude-opus-5-5"),
            system_prompt=os.getenv(
                "SYSTEM_PROMPT",
                "Ты полезный ассистент. Отвечай на русском языке.",
            ),
            timeout_seconds=_positive_int("REQUEST_TIMEOUT_SECONDS", 60),
            max_output_tokens=_positive_int("MAX_OUTPUT_TOKENS", 1200),
            max_history_messages=_positive_int("MAX_HISTORY_MESSAGES", 20),
            history_file=history_file,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
