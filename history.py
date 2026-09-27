"""Хранение истории диалога в JSON."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

Message = Dict[str, str]


class HistoryStore:
    def __init__(self, path: Path, max_messages: int) -> None:
        self.path = path
        self.max_messages = max_messages

    def load(self) -> List[Message]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Не удалось прочитать историю: {exc}") from exc

        if not isinstance(data, list):
            raise ValueError("Файл истории должен содержать JSON-массив")

        messages: List[Message] = []
        for item in data:
            if (
                isinstance(item, dict)
                and item.get("role") in {"user", "assistant"}
                and isinstance(item.get("content"), str)
            ):
                messages.append({"role": item["role"], "content": item["content"]})
        return messages[-self.max_messages :]

    def save(self, messages: List[Message]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        trimmed = messages[-self.max_messages :]
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = json.dumps(trimmed, ensure_ascii=False, indent=2)
        temporary_path.write_text(payload + "\n", encoding="utf-8")
        os.replace(temporary_path, self.path)

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()

