import json
import socket
import unittest
import urllib.error

from proxyapi_client import ProxyAPIClient, ProxyAPIError, parse_response


class ProxyAPIClientTests(unittest.TestCase):
    def test_parses_reasoning_usage(self):
        response = parse_response(
            {
                "model": "anthropic/claude-opus-5-5",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "42"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 9,
                    "total_tokens": 21,
                    "completion_tokens_details": {"reasoning_tokens": 7},
                },
            },
            0.5,
        )
        self.assertEqual(response.text, "42")
        self.assertEqual(response.usage.reasoning_tokens, 7)

    def test_request_contains_model_history_and_reasoning(self):
        captured = {}

        def transport(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            captured["timeout"] = timeout
            return {
                "model": "anthropic/claude-opus-5-5",
                "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                "usage": {},
            }

        client = ProxyAPIClient("secret", "https://example.test/v1", 15, transport)
        client.chat(
            "anthropic/claude-opus-5-5",
            [{"role": "user", "content": "hi"}],
            max_tokens=123,
            reasoning_effort="high",
        )
        self.assertEqual(captured["body"]["reasoning_effort"], "high")
        self.assertEqual(captured["body"]["max_tokens"], 123)
        self.assertEqual(captured["body"]["messages"][0]["content"], "hi")
        self.assertEqual(captured["timeout"], 15)

    def test_gpt6_uses_max_completion_tokens(self):
        captured = {}

        def transport(request, timeout):
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return {
                "model": "openai/gpt-6-luna",
                "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                "usage": {},
            }

        client = ProxyAPIClient("secret", "https://example.test/v1", 15, transport)
        client.chat("openai/gpt-6-luna", [{"role": "user", "content": "hi"}], 321)
        self.assertEqual(captured["body"]["max_completion_tokens"], 321)
        self.assertNotIn("max_tokens", captured["body"])

    def test_timeout_becomes_safe_error(self):
        def transport(request, timeout):
            raise socket.timeout("timed out")

        client = ProxyAPIClient("secret", "https://example.test/v1", 1, transport)
        with self.assertRaisesRegex(ProxyAPIError, "ProxyAPI"):
            client.chat("openai/gpt-6-luna", [], 10)

    def test_http_error_does_not_expose_key(self):
        def transport(request, timeout):
            raise urllib.error.HTTPError(
                request.full_url,
                402,
                "Payment Required",
                {},
                None,
            )

        client = ProxyAPIClient("very-secret-key", "https://example.test/v1", 1, transport)
        with self.assertRaises(ProxyAPIError) as context:
            client.chat("openai/gpt-6-luna", [], 10)
        self.assertNotIn("very-secret-key", str(context.exception))


if __name__ == "__main__":
    unittest.main()
