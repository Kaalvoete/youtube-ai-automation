"""Unit tests for setup.py"""

import importlib
import os
from pathlib import Path
from unittest.mock import patch

import pytest


def _get_setup_module():
    """Import setup.py without triggering pytest's setup_module hook."""
    import setup as _setup
    return _setup


class TestCreateDirectories:
    """Tests for create_directories."""

    def test_creates_all_directories(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mod = _get_setup_module()
        mod.create_directories()

        expected = ["output", "assets/templates", "assets/music", "logs", "cache"]
        for d in expected:
            assert (tmp_path / d).is_dir(), f"Directory {d} was not created"

    def test_idempotent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mod = _get_setup_module()
        mod.create_directories()
        mod.create_directories()  # should not raise

        assert (tmp_path / "output").is_dir()


class TestSetupEnv:
    """Tests for setup_env."""

    def test_creates_env_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mod = _get_setup_module()
        # Simulate user inputs: openai key, cohere key, elevenlabs key, channel id
        with patch("builtins.input", side_effect=["sk-test", "co-test", "el-test", ""]):
            mod.setup_env()

        env_file = tmp_path / ".env"
        assert env_file.exists()
        content = env_file.read_text()
        assert "OPENAI_API_KEY=sk-test" in content
        assert "COHERE_API_KEY=co-test" in content
        assert "ELEVENLABS_API_KEY=el-test" in content
        # Default channel ID
        assert "UCcItHjCePEXykLke8QIhqZQ" in content

    def test_skip_overwrite(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        env_file = tmp_path / ".env"
        env_file.write_text("EXISTING=value\n")

        mod = _get_setup_module()
        # User says "n" to overwrite
        with patch("builtins.input", return_value="n"):
            mod.setup_env()

        # Original content should be preserved
        assert env_file.read_text() == "EXISTING=value\n"


class TestSetupYoutubeOauth:
    """Tests for setup_youtube_oauth."""

    def test_warns_when_credentials_missing(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        mod = _get_setup_module()
        with patch("builtins.input", return_value=""):
            mod.setup_youtube_oauth()

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "youtube" in captured.out.lower()

    def test_confirms_when_credentials_exist(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "youtube_credentials.json").write_text("{}")

        mod = _get_setup_module()
        with patch("builtins.input", return_value=""):
            mod.setup_youtube_oauth()

        captured = capsys.readouterr()
        assert "found" in captured.out.lower()
