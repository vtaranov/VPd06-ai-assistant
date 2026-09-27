# VPd06: консольный AI-ассистент

Домашняя работа к уроку «VPd06. Кейс 3: AI API (OpenAI/Claude)».

Приложение общается с моделями через единый OpenAI-совместимый API ProxyAPI:

- обычный режим — `openai/gpt-6-luna`;
- думающий режим — `anthropic/claude-opus-5-5` с `reasoning_effort=high`.

## Что умеет проект

- выбирать один из двух режимов при старте;
- сохранять диалог в `history.json` и подгружать его при следующем запуске;
- показывать модель, время ответа, расход токенов и показатель reasoning;
- обрабатывать HTTP-ошибки, таймауты и неверные ответы;
- завершать работу по `exit`, `quit`, `выход` и очищать историю по `/clear`;
- не публиковать API-ключ и историю в Git.

ProxyAPI не всегда отдаёт текст внутренних рассуждений. Поэтому проект показывает безопасные и воспроизводимые показатели: `reasoning_tokens`, длительность запроса и общий расход токенов. Если провайдер не вернул отдельный счётчик, будет показано `reasoning=н/д`.

## Быстрый старт

Требуется Python 3.9 или новее. Сторонних зависимостей нет.

```bash
git clone https://github.com/vtaranov/VPd06-ai-assistant.git
cd VPd06-ai-assistant
cp .env.example .env
```

Откройте `.env` и замените `your_proxyapi_key_here` на ключ из кабинета ProxyAPI. Затем:

```bash
python3 main.py
```

Виртуальное окружение не обязательно, так как проект не устанавливает пакеты. Пустой `requirements.txt` с комментарием оставлен для привычного формата учебных проектов.

## Настройки

| Переменная | Назначение | По умолчанию |
| --- | --- | --- |
| `PROXYAPI_KEY` | Секретный ключ ProxyAPI | обязательно |
| `NORMAL_MODEL` | Модель обычного режима | `openai/gpt-6-luna` |
| `THINKING_MODEL` | Модель думающего режима | `anthropic/claude-opus-5-5` |
| `REQUEST_TIMEOUT_SECONDS` | Таймаут HTTP-запроса | `60` |
| `MAX_OUTPUT_TOKENS` | Лимит ответа | `1200` |
| `MAX_HISTORY_MESSAGES` | Число реплик в контексте | `20` |

## Тесты

```bash
python3 -m unittest discover -s tests -v
```

Тесты не делают платных запросов: HTTP-транспорт подменяется фиктивным.

### Проверено

27 сентября 2026 года:

- `13` модульных тестов — `OK`;
- живой ответ `openai/gpt-6-luna` — получен;
- живой ответ `anthropic/claude-opus-5-5` с `reasoning_effort=high` — получен;
- история из предыдущего запуска загружается и учитывается моделью;
- файл с ключом и файл истории игнорируются Git.

## Безопасность

- `.env` и `history.json` добавлены в `.gitignore`.
- API-ключ не печатается ни в ошибках, ни в логах.
- Для каждого учебного проекта лучше выпускать отдельный ключ с ограниченным бюджетом.

## Источники

- [ProxyAPI: единый API](https://proxyapi.ru/docs/api-overview)
- [ProxyAPI: модели и их идентификаторы](https://proxyapi.ru/docs/models)
- [ProxyAPI: reasoning](https://proxyapi.ru/docs/reasoning)
- [OpenAI: GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
