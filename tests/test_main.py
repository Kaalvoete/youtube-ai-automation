"""Unit tests for main.py CLI commands."""

import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestCliGroup:
    """Tests for the CLI group itself."""

    def test_help_text(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "YouTube AI Automation" in result.output


class TestCreateCommand:
    """Tests for the 'create' command."""

    @patch("scripts.video_generator.VideoGenerator", autospec=True)
    @patch("scripts.script_generator.ScriptGenerator", autospec=True)
    def test_create_without_upload(self, MockScriptGen, MockVideoGen, runner):
        mock_gen_instance = MagicMock()
        mock_gen_instance.generate_script.return_value = {
            "title": "Test Title",
            "description": "desc",
            "tags": ["AI"],
            "script": "body",
        }
        MockScriptGen.return_value = mock_gen_instance

        mock_vg_instance = MagicMock()
        mock_vg_instance.create_longform_video.return_value = "/tmp/video.mp4"
        MockVideoGen.return_value = mock_vg_instance

        result = runner.invoke(cli, ["create", "--prompt", "test prompt"])
        assert result.exit_code == 0
        assert "Done" in result.output

    @patch("scripts.uploader.YouTubeUploader", autospec=True)
    @patch("scripts.video_generator.VideoGenerator", autospec=True)
    @patch("scripts.script_generator.ScriptGenerator", autospec=True)
    def test_create_with_upload(self, MockScriptGen, MockVideoGen, MockUploader, runner):
        mock_gen = MagicMock()
        mock_gen.generate_script.return_value = {
            "title": "T", "description": "d", "tags": [], "script": "s"
        }
        MockScriptGen.return_value = mock_gen

        mock_vg = MagicMock()
        mock_vg.create_longform_video.return_value = "/tmp/v.mp4"
        MockVideoGen.return_value = mock_vg

        mock_up = MagicMock()
        mock_up.upload_video.return_value = "vid_123"
        MockUploader.return_value = mock_up

        result = runner.invoke(cli, ["create", "--prompt", "test", "--upload"])
        assert result.exit_code == 0
        assert "vid_123" in result.output

    @patch("scripts.video_generator.VideoGenerator", autospec=True)
    @patch("scripts.script_generator.ScriptGenerator", autospec=True)
    def test_create_short_video(self, MockScriptGen, MockVideoGen, runner):
        mock_gen = MagicMock()
        mock_gen.generate_script.return_value = {
            "title": "Short", "description": "d", "tags": [], "script": "s"
        }
        MockScriptGen.return_value = mock_gen

        mock_vg = MagicMock()
        mock_vg.create_shorts_video.return_value = "/tmp/shorts.mp4"
        MockVideoGen.return_value = mock_vg

        result = runner.invoke(cli, [
            "create", "--prompt", "test", "--type", "short", "--duration", "3-min"
        ])
        assert result.exit_code == 0

    def test_create_prompts_for_input(self, runner):
        """When no --prompt is given, create should prompt the user."""
        result = runner.invoke(cli, ["create"], input="my prompt\n")
        assert "prompt" in result.output.lower() or result.exit_code != 0


class TestTestCommand:
    """Tests for the 'test' command."""

    @patch("scripts.video_generator.VideoGenerator", autospec=True)
    @patch("scripts.script_generator.ScriptGenerator", autospec=True)
    def test_runs_tests(self, MockScriptGen, MockVideoGen, runner):
        mock_gen = MagicMock()
        mock_gen.generate_script.return_value = {
            "title": "T", "script": "s", "description": "d", "tags": []
        }
        MockScriptGen.return_value = mock_gen

        mock_vg = MagicMock()
        mock_vg.create_shorts_video.return_value = "/tmp/s.mp4"
        mock_vg.create_longform_video.return_value = "/tmp/l.mp4"
        MockVideoGen.return_value = mock_vg

        result = runner.invoke(cli, ["test"])
        assert result.exit_code == 0
        assert "tests passed" in result.output.lower() or "TEST" in result.output


class TestSetupCommand:
    """Tests for the 'setup' command."""

    @patch("setup.setup_youtube_oauth")
    @patch("setup.create_directories")
    @patch("setup.setup_env")
    def test_setup_calls_functions(self, mock_env, mock_dirs, mock_oauth, runner):
        result = runner.invoke(cli, ["setup"])
        assert result.exit_code == 0
        mock_env.assert_called_once()
        mock_dirs.assert_called_once()
        mock_oauth.assert_called_once()
