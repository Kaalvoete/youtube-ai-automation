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
    """🎬 YouTube AI Automation - Generate and upload AI videos daily"""
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
    
    print(f"\n🎬 Creating video: {prompt}")
    print(f"Type: {type} | Duration: {duration}\n")
    
    try:
        from scripts.script_generator import ScriptGenerator
        from scripts.video_generator import VideoGenerator
        from scripts.uploader import YouTubeUploader
        
        # Generate script
        print("[1/3] Generating script...")
        generator = ScriptGenerator(api_provider="openai")
        script = generator.generate_script(prompt, type, duration)
        print(f"✅ Script created: {script.get('title', 'Untitled')}\n")
        
        # Create video
        print("[2/3] Creating video...")
        video_gen = VideoGenerator()
        
        if "short" in type.lower() or "3-min" in duration:
            video_file = video_gen.create_shorts_video(script, "001")
        else:
            video_file = video_gen.create_longform_video(script, "001")
        
        print(f"✅ Video created: {video_file}\n")
        
        # Upload if requested
        if upload:
            print("[3/3] Uploading to YouTube...")
            uploader = YouTubeUploader()
            
            metadata = {
                "title": script.get("title", "AI Hack"),
                "description": script.get("description", ""),
                "tags": script.get("tags", []),
                "category_id": "28"
            }
            
            video_id = uploader.upload_video(video_file, metadata, visibility="public")
            print(f"✅ Video uploaded! ID: {video_id}")
        
        print("\n🚀 Done!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

@cli.command()
def schedule():
    """Start daily video generation and upload scheduler"""
    print("\n🎬 Starting daily scheduler...\n")
    
    try:
        from scripts.scheduler import VideoScheduler
        
        scheduler = VideoScheduler()
        scheduler.schedule_daily_uploads()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

@cli.command()
def setup():
    """Configure API credentials and settings"""
    print("\n🔧 Running setup...\n")
    import setup
    setup.setup_env()
    setup.create_directories()
    setup.setup_youtube_oauth()
    print("\n✅ Setup complete!")

@cli.command()
@click.option('--demo', is_flag=True, help='Generate demo content')
def test(demo: bool):
    """Test the system"""
    print("\n🧪 Running tests...\n")
    
    from scripts.script_generator import ScriptGenerator
    from scripts.video_generator import VideoGenerator
    
    # Test script generation
    print("[TEST 1] Script Generation")
    generator = ScriptGenerator(api_provider="openai")
    script = generator.generate_script(
        "Use ChatGPT to automate email",
        "tutorial",
        "5-min"
    )
    print(f"✅ Generated script with title: {script.get('title', 'N/A')}")
    
    # Test video generation
    print("\n[TEST 2] Video Generation")
    video_gen = VideoGenerator()
    shorts_file = video_gen.create_shorts_video(script, "test")
    longform_file = video_gen.create_longform_video(script, "test")
    print(f"✅ Created Shorts: {shorts_file}")
    print(f"✅ Created Long-form: {longform_file}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    cli()
