import tempfile
import unittest
from pathlib import Path

from history import HistoryStore


class HistoryStoreTests(unittest.TestCase):
    def test_history_survives_restart_and_is_trimmed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            store = HistoryStore(path, max_messages=2)
            store.save(
                [
                    {"role": "user", "content": "one"},
                    {"role": "assistant", "content": "two"},
                    {"role": "user", "content": "three"},
                ]
            )
            reloaded = HistoryStore(path, max_messages=2).load()
            self.assertEqual([item["content"] for item in reloaded], ["two", "three"])

    def test_invalid_items_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            path.write_text('[{"role":"system","content":"x"},{"bad":1}]', encoding="utf-8")
            self.assertEqual(HistoryStore(path, 10).load(), [])


if __name__ == "__main__":
    unittest.main()

