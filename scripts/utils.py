#!/usr/bin/env python3
"""
Shared utilities for the YouTube AI Automation system.

Centralises resolution parsing, text wrapping, font loading,
centred-text drawing, video-metadata construction, YouTube request
body building, and the end-to-end video-creation pipeline so that
each concern lives in exactly one place.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Resolution helpers
# ---------------------------------------------------------------------------

_RESOLUTION_MAP = {
    "1080x1920": (1080, 1920),
    "1920x1080": (1920, 1080),
}


def parse_resolution(resolution: str) -> Tuple[int, int]:
    """Convert a ``'WxH'`` resolution string to an ``(width, height)`` tuple."""
    if resolution in _RESOLUTION_MAP:
        return _RESOLUTION_MAP[resolution]
    parts = resolution.split("x")
    return (int(parts[0]), int(parts[1]))


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(text: str, max_chars_per_line: int) -> List[str]:
    """Word-wrap *text* so that no line exceeds *max_chars_per_line*."""
    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []

    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > max_chars_per_line:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    lines.append(" ".join(current_line))
    return lines


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

_FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a TrueType font with a fallback to the PIL default."""
    path = _FONT_BOLD if bold else _FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except (IOError, OSError):
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    lines: List[str],
    font: ImageFont.FreeTypeFont,
    img_size: Tuple[int, int],
    y_spacing: int,
    fill: Tuple[int, ...],
) -> None:
    """Draw *lines* of text horizontally centred on the image."""
    y_offset = (img_size[1] - len(lines) * y_spacing) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img_size[0] - text_width) // 2
        draw.text((x, y_offset + i * y_spacing), line, fill=fill, font=font)


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def build_video_metadata(script: Dict, category_id: str = "28") -> Dict:
    """Build a video-metadata dict from an AI-generated *script* dict.

    Used by both the CLI ``create`` command and the daily scheduler so
    the metadata shape stays consistent.
    """
    return {
        "title": script.get("title", "AI Hack"),
        "description": script.get("description", ""),
        "tags": script.get("tags", []),
        "category_id": category_id,
    }


# ---------------------------------------------------------------------------
# YouTube request-body helpers
# ---------------------------------------------------------------------------

def build_youtube_request_body(
    metadata: Dict,
    visibility: str = "public",
    made_for_kids: bool = False,
    publish_at: Optional[str] = None,
) -> Dict:
    """Build the ``body`` dict expected by the YouTube ``videos().insert`` API.

    Consolidates the body-building logic previously duplicated in
    ``upload_video`` and ``schedule_upload``.
    """
    body: Dict = {
        "snippet": {
            "title": metadata.get("title", "New Video"),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "categoryId": metadata.get("category_id", "28"),
        },
        "status": {
            "privacyStatus": visibility,
            "madeForKids": made_for_kids,
        },
    }
    if publish_at is not None:
        body["status"]["publishAt"] = publish_at
    return body


# ---------------------------------------------------------------------------
# Video-creation pipeline
# ---------------------------------------------------------------------------

def create_video_pipeline(
    prompt: str,
    video_type: str,
    duration: str,
    video_id: str,
    api_provider: str = "anthropic",
    upload: bool = False,
    visibility: str = "public",
) -> Optional[str]:
    """Run the full script -> video -> (optional) upload pipeline.

    Returns the YouTube video ID on successful upload, the local video
    file path when *upload* is ``False``, or ``None`` on failure.

    This replaces the duplicated orchestration logic that previously
    lived in both ``main.py::create`` and ``scheduler.py::generate_and_upload_video``.
    """
    # Late imports to avoid circular dependencies and keep the module
    # importable even when heavy third-party packages are absent.
    from scripts.script_generator import ScriptGenerator
    from scripts.video_generator import VideoGenerator
    from scripts.uploader import YouTubeUploader

    # 1. Generate script
    print("[1/3] Generating script...")
    generator = ScriptGenerator(api_provider=api_provider)
    script = generator.generate_script(prompt, video_type, duration)
    print(f"Script created: {script.get('title', 'Untitled')}\n")

    # 2. Create video
    print("[2/3] Creating video...")
    video_gen = VideoGenerator()

    if "short" in video_type.lower() or "3-min" in duration:
        video_file = video_gen.create_shorts_video(script, video_id)
    else:
        video_file = video_gen.create_longform_video(script, video_id)

    print(f"Video created: {video_file}\n")

    # 3. Upload (optional)
    if upload:
        print("[3/3] Uploading to YouTube...")
        uploader = YouTubeUploader()
        metadata = build_video_metadata(script)
        yt_video_id = uploader.upload_video(video_file, metadata, visibility=visibility)
        if yt_video_id:
            print(f"Video uploaded! ID: {yt_video_id}")
        return yt_video_id

    return video_file
