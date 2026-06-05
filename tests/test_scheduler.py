"""Unit tests for scripts/scheduler.py"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from scripts.scheduler import VideoScheduler


class TestVideoSchedulerInit:
    """Tests for VideoScheduler initialisation."""

    @patch.dict(os.environ, {"DAILY_UPLOAD_TIME": "14:00", "VIDEOS_PER_DAY": "3"})
    def test_reads_env_vars(self):
        sched = VideoScheduler()
        assert sched.upload_time == "14:00"
        assert sched.videos_per_day == 3

    @patch.dict(os.environ, {}, clear=True)
    def test_defaults(self):
        sched = VideoScheduler()
        assert sched.upload_time == "09:00"
        assert sched.videos_per_day == 2
        assert sched.current_prompt_index == 0


class TestGetNextPrompt:
    """Tests for _get_next_prompt."""

    def test_reads_prompts_from_file(self, prompts_file):
        sched = VideoScheduler()
        sched.prompt_file = prompts_file

        prompt, vtype, duration = sched._get_next_prompt()
        assert prompt == "Build a ChatGPT bot"
        assert vtype == "tool tutorial"
        assert duration == "5-min"

    def test_cycles_through_prompts(self, prompts_file):
        sched = VideoScheduler()
        sched.prompt_file = prompts_file

        first = sched._get_next_prompt()
        second = sched._get_next_prompt()
        assert first[0] != second[0]  # different prompts

    def test_wraps_around(self, prompts_file):
        sched = VideoScheduler()
        sched.prompt_file = prompts_file

        sched._get_next_prompt()
        sched._get_next_prompt()
        third = sched._get_next_prompt()
        # Should wrap back to first prompt
        assert third[0] == "Build a ChatGPT bot"

    def test_skips_comments_and_blank_lines(self, tmp_path):
        pf = tmp_path / "prompts.txt"
        pf.write_text("# comment\n\nHack | AI trick | 3-min\n")
        sched = VideoScheduler()
        sched.prompt_file = str(pf)

        prompt, vtype, duration = sched._get_next_prompt()
        assert prompt == "AI trick"
        assert vtype == "hack"

    def test_empty_file_returns_default(self, tmp_path):
        pf = tmp_path / "prompts.txt"
        pf.write_text("# only comments\n")
        sched = VideoScheduler()
        sched.prompt_file = str(pf)

        prompt, vtype, duration = sched._get_next_prompt()
        assert prompt == "AI Automation Hack"
        assert vtype == "tutorial"

    def test_missing_file_returns_default(self):
        sched = VideoScheduler()
        sched.prompt_file = "/nonexistent/prompts.txt"

        prompt, vtype, duration = sched._get_next_prompt()
        assert prompt == "AI Automation Hack"

    def test_single_column_prompt(self, tmp_path):
        pf = tmp_path / "prompts.txt"
        pf.write_text("SinglePrompt\n")
        sched = VideoScheduler()
        sched.prompt_file = str(pf)

        prompt, vtype, duration = sched._get_next_prompt()
        assert vtype == "singleprompt"


class TestLogUpload:
    """Tests for _log_upload."""

    def test_creates_log_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        sched = VideoScheduler()

        sched._log_upload("Test prompt", "vid_123", "/path/to/video.mp4")

        log_path = tmp_path / "logs" / "upload_log.txt"
        assert log_path.exists()
        content = log_path.read_text()
        assert "Test prompt" in content
        assert "vid_123" in content

    def test_appends_to_existing_log(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        sched = VideoScheduler()

        sched._log_upload("First", "id1", "/v1.mp4")
        sched._log_upload("Second", "id2", "/v2.mp4")

        log_path = tmp_path / "logs" / "upload_log.txt"
        content = log_path.read_text()
        assert "First" in content
        assert "Second" in content
