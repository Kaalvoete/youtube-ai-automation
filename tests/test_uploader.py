"""Unit tests for scripts/uploader.py"""

import os
from unittest.mock import patch, MagicMock

import pytest

from scripts.uploader import YouTubeUploader


class TestYouTubeUploaderInit:
    """Tests for YouTubeUploader initialisation."""

    @patch("scripts.uploader.os.getenv", return_value="UC_TEST_CHANNEL")
    @patch.object(YouTubeUploader, "setup_client")
    def test_reads_channel_id_from_env(self, _mock_setup, _mock_env):
        uploader = YouTubeUploader.__new__(YouTubeUploader)
        uploader.channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
        uploader.setup_client = MagicMock()
        assert uploader.channel_id == "UC_TEST_CHANNEL"

    @patch("scripts.uploader.os.getenv", return_value=None)
    def test_setup_client_import_error(self, _mock_env):
        """When google libs are missing, youtube attr should be None."""
        with patch.dict("sys.modules", {
            "google.auth.transport.requests": None,
            "google.oauth2.service_account": None,
            "googleapiclient.discovery": None,
            "googleapiclient.http": None,
        }):
            uploader = YouTubeUploader()
            assert uploader.youtube is None


class TestUploadVideo:
    """Tests for upload_video."""

    def _make_uploader(self):
        with patch.object(YouTubeUploader, "__init__", lambda self: None):
            up = YouTubeUploader.__new__(YouTubeUploader)
            up.channel_id = "UC_TEST"
            up.youtube = None
            up.MediaFileUpload = None
            return up

    def test_returns_none_if_file_missing(self):
        up = self._make_uploader()
        up.youtube = MagicMock()
        result = up.upload_video("/nonexistent/video.mp4", {"title": "T"})
        assert result is None

    def test_returns_none_if_no_client(self, tmp_path):
        up = self._make_uploader()
        up.youtube = None
        video = tmp_path / "test.mp4"
        video.touch()
        result = up.upload_video(str(video), {"title": "T"})
        assert result is None

    def test_successful_upload(self, tmp_path):
        up = self._make_uploader()
        mock_yt = MagicMock()
        mock_request = MagicMock()
        mock_request.execute.return_value = {"id": "vid_123"}
        mock_yt.videos.return_value.insert.return_value = mock_request
        up.youtube = mock_yt
        up.MediaFileUpload = MagicMock()

        video = tmp_path / "test.mp4"
        video.touch()

        metadata = {
            "title": "Test Video",
            "description": "Desc",
            "tags": ["AI"],
            "category_id": "28",
        }
        result = up.upload_video(str(video), metadata)
        assert result == "vid_123"

    def test_upload_with_default_metadata(self, tmp_path):
        up = self._make_uploader()
        mock_yt = MagicMock()
        mock_request = MagicMock()
        mock_request.execute.return_value = {"id": "vid_456"}
        mock_yt.videos.return_value.insert.return_value = mock_request
        up.youtube = mock_yt
        up.MediaFileUpload = MagicMock()

        video = tmp_path / "vid.mp4"
        video.touch()
        result = up.upload_video(str(video), {})
        assert result == "vid_456"

    def test_upload_exception_returns_none(self, tmp_path):
        up = self._make_uploader()
        mock_yt = MagicMock()
        mock_yt.videos.return_value.insert.side_effect = Exception("quota")
        up.youtube = mock_yt
        up.MediaFileUpload = MagicMock()

        video = tmp_path / "err.mp4"
        video.touch()
        result = up.upload_video(str(video), {"title": "T"})
        assert result is None

    def test_made_for_kids_flag(self, tmp_path):
        up = self._make_uploader()
        mock_yt = MagicMock()
        mock_request = MagicMock()
        mock_request.execute.return_value = {"id": "kid_vid"}
        mock_yt.videos.return_value.insert.return_value = mock_request
        up.youtube = mock_yt
        up.MediaFileUpload = MagicMock()

        video = tmp_path / "kid.mp4"
        video.touch()
        result = up.upload_video(str(video), {"title": "T"}, made_for_kids=True)
        assert result == "kid_vid"


class TestScheduleUpload:
    """Tests for schedule_upload."""

    def _make_uploader(self):
        with patch.object(YouTubeUploader, "__init__", lambda self: None):
            up = YouTubeUploader.__new__(YouTubeUploader)
            up.channel_id = "UC_TEST"
            up.youtube = None
            up.MediaFileUpload = None
            return up

    def test_returns_none_if_no_client(self):
        up = self._make_uploader()
        result = up.schedule_upload("video.mp4", {}, "2026-01-01T09:00:00Z")
        assert result is None

    def test_successful_schedule(self, tmp_path):
        up = self._make_uploader()
        mock_yt = MagicMock()
        mock_request = MagicMock()
        mock_request.execute.return_value = {"id": "sched_789"}
        mock_yt.videos.return_value.insert.return_value = mock_request
        up.youtube = mock_yt
        up.MediaFileUpload = MagicMock()

        video = tmp_path / "sched.mp4"
        video.touch()
        result = up.schedule_upload(str(video), {"title": "Scheduled"}, "2026-01-01T09:00:00Z")
        assert result == "sched_789"

    def test_schedule_exception_returns_none(self, tmp_path):
        up = self._make_uploader()
        mock_yt = MagicMock()
        mock_yt.videos.return_value.insert.side_effect = Exception("fail")
        up.youtube = mock_yt
        up.MediaFileUpload = MagicMock()

        video = tmp_path / "fail.mp4"
        video.touch()
        result = up.schedule_upload(str(video), {}, "2026-01-01T09:00:00Z")
        assert result is None
