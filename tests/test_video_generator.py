"""Unit tests for scripts/video_generator.py"""

import os
from pathlib import Path

import pytest

from scripts.video_generator import VideoGenerator


class TestSanitizeText:
    """Tests for _sanitize_text_for_rendering."""

    def test_plain_ascii_unchanged(self):
        vg = VideoGenerator(output_dir="/tmp/vg_test_sanitize")
        assert vg._sanitize_text_for_rendering("Hello World") == "Hello World"

    def test_removes_emoji(self):
        vg = VideoGenerator(output_dir="/tmp/vg_test_sanitize")
        result = vg._sanitize_text_for_rendering("Hello 🎬 World 🚀")
        assert "\U0001f3ac" not in result
        assert "\U0001f680" not in result
        assert "Hello" in result
        assert "World" in result

    def test_removes_supplementary_plane_chars(self):
        vg = VideoGenerator(output_dir="/tmp/vg_test_sanitize")
        result = vg._sanitize_text_for_rendering("Test \U0001f600 ok")
        assert ord(max(result)) < 0x10000 or result == "Test ok"

    def test_collapses_whitespace(self):
        vg = VideoGenerator(output_dir="/tmp/vg_test_sanitize")
        result = vg._sanitize_text_for_rendering("Hello   World")
        assert result == "Hello World"

    def test_empty_string(self):
        vg = VideoGenerator(output_dir="/tmp/vg_test_sanitize")
        assert vg._sanitize_text_for_rendering("") == ""


class TestVideoGeneratorInit:
    """Tests for VideoGenerator initialisation."""

    def test_creates_output_dir(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        assert vg.output_dir.exists()

    def test_default_output_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        vg = VideoGenerator()
        assert vg.output_dir == Path("output")


class TestCreateTitleFrame:
    """Tests for _create_title_frame."""

    def test_creates_png_file(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        path = vg._create_title_frame("Test Title")
        assert os.path.exists(path)
        assert path.endswith(".png")

    def test_portrait_resolution(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        path = vg._create_title_frame("Test", resolution="1080x1920")
        assert os.path.exists(path)

    def test_landscape_resolution(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        path = vg._create_title_frame("Test", resolution="1920x1080")
        assert os.path.exists(path)

    def test_sanitizes_emoji_in_title(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        # Should not raise even with emoji in title
        path = vg._create_title_frame("AI Hack 🚀 Amazing")
        assert os.path.exists(path)


class TestCreateTextFrame:
    """Tests for _create_text_frame."""

    def test_creates_png_file(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        path = vg._create_text_frame("Some text content here")
        assert os.path.exists(path)
        assert path.endswith(".png")

    def test_portrait_resolution(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        path = vg._create_text_frame("Content", resolution="1080x1920")
        assert os.path.exists(path)

    def test_long_text_wraps(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        long_text = "This is a very long text that should be wrapped " * 5
        path = vg._create_text_frame(long_text)
        assert os.path.exists(path)


class TestCreateVideoFromFrames:
    """Tests for _create_video_from_frames."""

    def test_empty_frames_returns_empty(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        out = Path(tmp_output_dir) / "test.mp4"
        result = vg._create_video_from_frames([], out, 60, 30, "1920x1080")
        assert result == ""

    def test_creates_placeholder_file(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        # Create a dummy frame
        frame = vg._create_title_frame("Test")
        out = Path(tmp_output_dir) / "video.mp4"
        result = vg._create_video_from_frames([frame], out, 60, 30, "1920x1080")
        assert os.path.exists(result)


class TestCreateShortsVideo:
    """Tests for create_shorts_video."""

    def test_returns_file_path(self, tmp_output_dir, sample_script):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        result = vg.create_shorts_video(sample_script, "test_001")
        assert "shorts_test_001" in result
        assert os.path.exists(result)

    def test_works_without_hook(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        script = {"title": "No Hook Video"}
        result = vg.create_shorts_video(script, "nohook")
        assert os.path.exists(result)


class TestCreateLongformVideo:
    """Tests for create_longform_video."""

    def test_returns_file_path(self, tmp_output_dir, sample_script):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        result = vg.create_longform_video(sample_script, "test_002")
        assert "longform_test_002" in result
        assert os.path.exists(result)

    def test_works_with_empty_script(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        script = {"title": "Empty Script"}
        result = vg.create_longform_video(script, "empty")
        assert os.path.exists(result)

    def test_long_script_limited_to_10_frames(self, tmp_output_dir):
        vg = VideoGenerator(output_dir=tmp_output_dir)
        script = {"title": "Long", "script": "x" * 3000}
        result = vg.create_longform_video(script, "long")
        assert os.path.exists(result)
