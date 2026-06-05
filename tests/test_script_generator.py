"""Unit tests for scripts/script_generator.py"""

import json
from unittest.mock import patch, MagicMock

import pytest

from scripts.script_generator import ScriptGenerator


class TestScriptGeneratorInit:
    """Tests for ScriptGenerator initialisation and client setup."""

    @patch("scripts.script_generator.os.getenv", return_value="fake-key")
    def test_init_sets_api_provider(self, _mock_env):
        with patch.object(ScriptGenerator, "setup_client"):
            gen = ScriptGenerator(api_provider="openai")
            assert gen.api_provider == "openai"

    @patch("scripts.script_generator.os.getenv", return_value=None)
    def test_setup_client_anthropic_import_error(self, _mock_env):
        """When anthropic package is missing, client should be None."""
        with patch.dict("sys.modules", {"anthropic": None}):
            gen = ScriptGenerator(api_provider="anthropic")
            assert gen.client is None

    @patch("scripts.script_generator.os.getenv", return_value=None)
    def test_setup_client_openai_import_error(self, _mock_env):
        with patch.dict("sys.modules", {"openai": None}):
            gen = ScriptGenerator(api_provider="openai")
            assert gen.client is None

    @patch("scripts.script_generator.os.getenv", return_value=None)
    def test_setup_client_cohere_import_error(self, _mock_env):
        with patch.dict("sys.modules", {"cohere": None}):
            gen = ScriptGenerator(api_provider="cohere")
            assert gen.client is None


class TestParseScriptResponse:
    """Tests for _parse_script_response."""

    def _make_generator(self):
        with patch.object(ScriptGenerator, "setup_client"):
            gen = ScriptGenerator.__new__(ScriptGenerator)
            gen.api_provider = "openai"
            gen.client = None
            return gen

    def test_valid_json(self):
        gen = self._make_generator()
        payload = json.dumps({
            "title": "Cool Hack",
            "script": "Hello",
            "description": "desc",
            "tags": ["AI"],
        })
        result = gen._parse_script_response(payload)
        assert result["title"] == "Cool Hack"
        assert result["tags"] == ["AI"]

    def test_json_embedded_in_text(self):
        gen = self._make_generator()
        text = 'Here is your script:\n{"title": "Embedded", "script": "body"}\nEnjoy!'
        result = gen._parse_script_response(text)
        assert result["title"] == "Embedded"

    def test_no_json_returns_fallback(self):
        gen = self._make_generator()
        result = gen._parse_script_response("plain text with no json")
        assert "title" in result
        assert "tags" in result


class TestGenerateTemplate:
    """Tests for _generate_template fallback."""

    def _make_generator(self):
        with patch.object(ScriptGenerator, "setup_client"):
            gen = ScriptGenerator.__new__(ScriptGenerator)
            gen.api_provider = "openai"
            gen.client = None
            return gen

    def test_returns_dict_with_required_keys(self):
        gen = self._make_generator()
        result = gen._generate_template("My prompt", "tutorial", "5-min")
        assert "title" in result
        assert "hook" in result
        assert "script" in result
        assert "description" in result
        assert "tags" in result

    def test_title_contains_prompt(self):
        gen = self._make_generator()
        result = gen._generate_template("ChatGPT trick", "hack", "3-min")
        assert "ChatGPT trick" in result["title"]

    def test_tags_is_list(self):
        gen = self._make_generator()
        result = gen._generate_template("test", "tutorial", "5-min")
        assert isinstance(result["tags"], list)
        assert len(result["tags"]) > 0


class TestGenerateScript:
    """Tests for generate_script (integration-level with mocked APIs)."""

    def _make_generator(self):
        with patch.object(ScriptGenerator, "setup_client"):
            gen = ScriptGenerator.__new__(ScriptGenerator)
            gen.api_provider = "openai"
            gen.client = None
            return gen

    def test_fallback_when_no_client(self):
        gen = self._make_generator()
        result = gen.generate_script("AI hack", "tutorial", "5-min")
        assert "title" in result
        assert "script" in result

    def test_anthropic_api_call(self):
        gen = self._make_generator()
        gen.api_provider = "anthropic"
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text=json.dumps({"title": "From API", "script": "body", "description": "d", "tags": ["a"]}))
        ]
        mock_client.messages.create.return_value = mock_response
        gen.client = mock_client

        result = gen.generate_script("prompt", "tutorial", "5-min")
        assert result["title"] == "From API"
        mock_client.messages.create.assert_called_once()

    def test_openai_api_call(self):
        gen = self._make_generator()
        gen.api_provider = "openai"
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({"title": "OpenAI Result", "script": "s", "description": "d", "tags": []})
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        gen.client = mock_client

        result = gen.generate_script("prompt", "tutorial", "5-min")
        assert result["title"] == "OpenAI Result"

    def test_cohere_api_call(self):
        gen = self._make_generator()
        gen.api_provider = "cohere"
        mock_client = MagicMock()
        mock_gen = MagicMock()
        mock_gen.text = json.dumps({"title": "Cohere Result", "script": "s", "description": "d", "tags": []})
        mock_response = MagicMock()
        mock_response.generations = [mock_gen]
        mock_client.generate.return_value = mock_response
        gen.client = mock_client

        result = gen.generate_script("prompt", "tutorial", "5-min")
        assert result["title"] == "Cohere Result"

    def test_api_exception_falls_back_to_template(self):
        gen = self._make_generator()
        gen.api_provider = "anthropic"
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API down")
        gen.client = mock_client

        result = gen.generate_script("prompt", "tutorial", "5-min")
        assert "title" in result
        assert "script" in result
