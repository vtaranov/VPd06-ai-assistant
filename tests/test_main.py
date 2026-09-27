import unittest

from main import build_api_messages, choose_mode, format_usage
from proxyapi_client import AssistantResponse, Usage


class MainTests(unittest.TestCase):
    def test_thinking_mode_is_default(self):
        self.assertEqual(choose_mode(""), ("thinking", True))

    def test_normal_mode(self):
        self.assertEqual(choose_mode("1"), ("normal", False))

    def test_context_order(self):
        messages = build_api_messages(
            "system",
            [{"role": "assistant", "content": "old"}],
            "new",
        )
        self.assertEqual([item["role"] for item in messages], ["system", "assistant", "user"])

    def test_reasoning_indicator_is_printed(self):
        response = AssistantResponse(
            text="ok",
            model="anthropic/claude-opus-5-5",
            finish_reason="stop",
            duration_seconds=1.25,
            usage=Usage(10, 20, 30, 12),
        )
        self.assertIn("reasoning=12", format_usage(response, True))


if __name__ == "__main__":
    unittest.main()

