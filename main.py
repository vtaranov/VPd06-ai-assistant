"""Консольный AI-ассистент для задания VPd06."""

from __future__ import annotations

import logging
from typing import List, Tuple

from config import ConfigurationError, Settings
from history import HistoryStore, Message
from proxyapi_client import AssistantResponse, ProxyAPIClient, ProxyAPIError

EXIT_COMMANDS = {"exit", "quit", "выход"}


def choose_mode(raw_choice: str) -> Tuple[str, bool]:
    choice = raw_choice.strip().lower()
    if choice in {"", "2", "thinking", "claude", "думающая"}:
        return "thinking", True
    if choice in {"1", "normal", "gpt", "обычная"}:
        return "normal", False
    raise ValueError("Введите 1 или 2")


def format_usage(response: AssistantResponse, show_reasoning: bool) -> str:
    fields = [f"модель={response.model}", f"время={response.duration_seconds:.2f}с"]
    if response.usage.prompt_tokens is not None:
        fields.append(f"вход={response.usage.prompt_tokens}")
    if response.usage.completion_tokens is not None:
        fields.append(f"выход={response.usage.completion_tokens}")
    if response.usage.total_tokens is not None:
        fields.append(f"всего={response.usage.total_tokens}")
    if show_reasoning:
        reasoning = response.usage.reasoning_tokens
        fields.append(f"reasoning={reasoning if reasoning is not None else 'н/д'}")
    if response.finish_reason:
        fields.append(f"завершение={response.finish_reason}")
    return " | ".join(fields)


def build_api_messages(system_prompt: str, history: List[Message], user_text: str) -> List[Message]:
    return [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_text},
    ]


def run() -> int:
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        print(f"Ошибка конфигурации: {exc}")
        return 2

    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("vpd06")

    print("\nAI-ассистент VPd06")
    print("1 — обычная модель (GPT-6 Luna)")
    print("2 — думающая модель (Claude Opus 5.5, по умолчанию)")
    while True:
        try:
            mode_name, thinking_mode = choose_mode(input("Выбор [2]: "))
            break
        except ValueError as exc:
            print(exc)

    model = settings.thinking_model if thinking_mode else settings.normal_model
    store = HistoryStore(settings.history_file, settings.max_history_messages)
    try:
        history = store.load()
    except ValueError as exc:
        logger.warning("%s; начинаю новый диалог", exc)
        history = []

    client = ProxyAPIClient(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout_seconds=settings.timeout_seconds,
    )
    logger.info("Режим=%s, модель=%s, история=%d сообщений", mode_name, model, len(history))
    print("Команды: exit / quit / выход, /clear\n")

    while True:
        try:
            user_text = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДиалог завершён.")
            break

        if not user_text:
            continue
        if user_text.lower() in EXIT_COMMANDS:
            print("Диалог сохранён. До свидания!")
            break
        if user_text.lower() == "/clear":
            history.clear()
            store.clear()
            print("История очищена.")
            continue

        logger.info("Отправляю запрос в ProxyAPI")
        try:
            response = client.chat(
                model=model,
                messages=build_api_messages(settings.system_prompt, history, user_text),
                max_tokens=settings.max_output_tokens,
                reasoning_effort="high" if thinking_mode else None,
            )
        except ProxyAPIError as exc:
            logger.error("%s", exc)
            print("Запрос не выполнен. Можно повторить или выйти командой exit.\n")
            continue

        print(f"\nАссистент: {response.text}")
        print(f"[{format_usage(response, thinking_mode)}]\n")
        history.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": response.text},
            ]
        )
        history = history[-settings.max_history_messages :]
        try:
            store.save(history)
        except OSError as exc:
            logger.error("Не удалось сохранить историю: %s", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(run())

