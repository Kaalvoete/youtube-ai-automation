import os
import sys
import tempfile
import shutil

import pytest

# Ensure repo root is on sys.path so `scripts.*` imports work
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Provide a temporary output directory and clean up after."""
    out = tmp_path / "output"
    out.mkdir()
    return str(out)


@pytest.fixture
def sample_script():
    """A minimal script dict for video generation tests."""
    return {
        "title": "5 AI Hacks You Need",
        "hook": "Wait till the end, this will blow your mind.",
        "script": "Today I'm showing you five incredible AI hacks that save hours.",
        "description": "AI hacks for productivity. Subscribe!",
        "tags": ["AI", "automation", "hack"],
        "cta": "Subscribe!",
    }


@pytest.fixture
def prompts_file(tmp_path):
    """Create a temporary prompts.txt file."""
    pf = tmp_path / "prompts.txt"
    pf.write_text(
        "# comment line\n"
        "Tool Tutorial | Build a ChatGPT bot | 5-min\n"
        "Life Hack | Automate email with AI | 3-min-short\n"
    )
    return str(pf)
