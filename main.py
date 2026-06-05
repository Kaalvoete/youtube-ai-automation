#!/usr/bin/env python3
"""
Main entry point for YouTube AI Automation system
"""

import click
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@click.group()
def cli():
    """YouTube AI Automation - Generate and upload AI videos daily"""
    pass

@cli.command()
@click.option('--prompt', '-p', help='Video prompt')
@click.option('--type', '-t', default='tutorial', help='Video type: tutorial, comparison, hack, etc')
@click.option('--duration', '-d', default='5-min', help='Video duration: 3-min, 5-min')
@click.option('--upload', is_flag=True, help='Upload to YouTube after creation')
def create(
    prompt: str,
    type: str,
    duration: str,
    upload: bool
):
    """Create a single video from a prompt"""
    
    if not prompt:
        prompt = click.prompt('Enter your video prompt')
    
    print(f"\nCreating video: {prompt}")
    print(f"Type: {type} | Duration: {duration}\n")
    
    try:
        from scripts.utils import create_video_pipeline

        result = create_video_pipeline(
            prompt=prompt,
            video_type=type,
            duration=duration,
            video_id="001",
            api_provider="anthropic",
            upload=upload,
        )

        if upload and result:
            print(f"Video uploaded! ID: {result}")
        elif result:
            print(f"Video created: {result}")
        
        print("\nDone!")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

@cli.command()
def schedule():
    """Start daily video generation and upload scheduler"""
    print("\nStarting daily scheduler...\n")
    
    try:
        from scripts.scheduler import VideoScheduler
        
        scheduler = VideoScheduler()
        scheduler.schedule_daily_uploads()
    
    except KeyboardInterrupt:
        print("\n\nScheduler stopped.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

@cli.command()
def setup():
    """Configure API credentials and settings"""
    print("\nRunning setup...\n")
    import setup
    setup.setup_env()
    setup.create_directories()
    setup.setup_youtube_oauth()
    print("\nSetup complete!")

@cli.command()
@click.option('--demo', is_flag=True, help='Generate demo content')
def test(demo: bool):
    """Test the system"""
    print("\nRunning tests...\n")
    
    from scripts.script_generator import ScriptGenerator
    from scripts.video_generator import VideoGenerator
    
    # Test script generation
    print("[TEST 1] Script Generation")
    generator = ScriptGenerator(api_provider="anthropic")
    script = generator.generate_script(
        "Use ChatGPT to automate email",
        "tutorial",
        "5-min"
    )
    print(f"Generated script with title: {script.get('title', 'N/A')}")
    
    # Test video generation
    print("\n[TEST 2] Video Generation")
    video_gen = VideoGenerator()
    shorts_file = video_gen.create_shorts_video(script, "test")
    longform_file = video_gen.create_longform_video(script, "test")
    print(f"Created Shorts: {shorts_file}")
    print(f"Created Long-form: {longform_file}")
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    cli()
