import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from config import ConfigurationError, Settings, load_env_file


class ConfigTests(unittest.TestCase):
    def test_env_file_does_not_override_existing_variable(self):
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text("PROXYAPI_KEY=from-file\n", encoding="utf-8")
            with patch.dict(os.environ, {"PROXYAPI_KEY": "from-shell"}, clear=True):
                load_env_file(env_path)
                self.assertEqual(os.environ["PROXYAPI_KEY"], "from-shell")

    def test_missing_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ConfigurationError):
                    Settings.from_env(Path(directory) / "missing.env")


if __name__ == "__main__":
    unittest.main()

