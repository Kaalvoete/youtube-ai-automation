# 🎬 Setup Guide - YouTube AI Automation

## Prerequisites
- Python 3.9 or higher
- FFmpeg installed
- Free API accounts (see below)

## Step 1: Install FFmpeg

### macOS
```bash
brew install ffmpeg
```

### Ubuntu/Debian
```bash
sudo apt-get install ffmpeg
```

### Windows
Download from https://ffmpeg.org/download.html or use:
```bash
choco install ffmpeg
```

## Step 2: Clone Repository & Setup Python

```bash
git clone https://github.com/Kaalvoete/youtube-ai-automation.git
cd youtube-ai-automation

python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

pip install -r requirements.txt
```

## Step 3: Get Free API Keys

### Option A: OpenAI (Recommended)
1. Go to https://platform.openai.com
2. Sign up/Login
3. Go to API keys section
4. Click "Create new secret key"
5. Copy your API key (you get $5 free credits)

### Option B: Cohere (Free Alternative)
1. Go to https://cohere.ai
2. Sign up
3. Copy your API key from dashboard

### ElevenLabs (Better Text-to-Speech)
1. Go to https://elevenlabs.io
2. Sign up
3. Get free credits (10,000 characters)
4. Copy API key from settings

## Step 4: YouTube API Setup

1. Go to https://console.cloud.google.com
2. Create a new project (or select existing)
3. Search for "YouTube Data API v3" and enable it
4. Go to Credentials (left menu)
5. Create OAuth 2.0 credentials:
   - Click "Create Credentials"
   - Choose "OAuth client ID"
   - Select "Desktop app"
   - Download the JSON file
6. Save the JSON file as `youtube_credentials.json` in your project root

## Step 5: Run Setup Wizard

```bash
python setup.py
```

This will:
- Create `.env` file with your API keys
- Create necessary directories
- Configure YouTube OAuth

## Step 6: Test the System

```bash
python main.py test
```

You should see:
```
[TEST 1] Script Generation
✅ Generated script...

[TEST 2] Video Generation  
✅ Created Shorts: output/shorts_test.mp4
✅ Created Long-form: output/longform_test.mp4

✅ All tests passed!
```

## Step 7: Create Your First Video

### Without uploading (test)
```bash
python main.py create --prompt "ChatGPT hack to save 5 hours"
```

### With upload to YouTube
```bash
python main.py create --prompt "ChatGPT hack to save 5 hours" --upload
```

## Step 8: Start Daily Automation

```bash
python main.py schedule
```

This will:
- Generate 2 videos per day (configurable)
- Upload at 9 AM UTC (configurable)
- Create both Shorts (60s) and Long-form (5 min) videos
- Repeat automatically forever

## Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt
```

### FFmpeg Not Found
Make sure FFmpeg is installed:
```bash
ffmpeg -version
```

If not found, reinstall it for your OS (see Step 1).

### API Key Errors
- Double-check `.env` file has correct keys
- Make sure you didn't accidentally copy extra spaces
- Check API keys are valid at their respective sites

### YouTube Upload Fails
- Verify YouTube API is enabled in Google Cloud Console
- Check `youtube_credentials.json` exists in root directory
- Make sure channel ID in `.env` is correct
- Try manually authenticating: `python -c "from google.oauth2.service_account import Credentials"`

### No Videos Generated
- Check that `config/prompts.txt` has content
- Verify OpenAI API key works
- Check logs in `logs/` directory
- Try running `python main.py test` first

## Configuration Files

### `.env`
Your API keys and settings (DO NOT commit to GitHub)

### `config/config.yml`
Video settings:
- Upload time (`time_of_day`)
- Videos per day (`videos_per_day`)
- Video length (`longform.length_seconds`)
- Niche and tone settings

### `config/prompts.txt`
Daily video prompts - edit to change content:
```
Tool Tutorial | ChatGPT hack to save time | 5-min
Life Hack | Use Zapier for automation | 5-min
```

## Customization

### Change Upload Time
Edit `.env`:
```
DILY_UPLOAD_TIME=14:00  # 2 PM instead of 9 AM
```

### Upload 3 Videos Per Day
Edit `.env`:
```
VIDEOS_PER_DAY=3
```

### Change Video Length
Edit `.env`:
```
VIDEO_LENGTH_LONG=600  # 10 minutes instead of 5
```

### Add Your Own Prompts
Edit `config/prompts.txt` and add new lines:
```
Tool Tutorial | Your awesome prompt | 5-min
```

## Free Tier Limits

With free APIs, you can:
- **OpenAI**: ~500-1000 video scripts/month ($5 free credits)
- **Cohere**: 5000 API calls/month (covers all video scripts)
- **ElevenLabs**: 10,000 characters/month (covers ~500 videos)
- **YouTube API**: 10,000 quota units/day (unlimited videos)

## Running 24/7

To run the scheduler 24/7:

### Option 1: Keep Terminal Open
Just leave the terminal running. The script will generate and upload videos automatically.

### Option 2: Use Screen (Linux/Mac)
```bash
screen -S youtube
python main.py schedule
# Press Ctrl+A then D to detach
# Type 'screen -r youtube' to reattach
```

### Option 3: Use Background Service
Create a systemd service or launchd daemon for your OS.

### Option 4: Cloud VPS
Run on a cheap VPS ($5-10/month) for 24/7 operation:
- DigitalOcean
- Linode
- AWS (free tier)
- Google Cloud (free tier)

## Next Steps

1. ✅ Customize prompts in `config/prompts.txt`
2. ✅ Adjust video settings in `config/config.yml`
3. ✅ Set your preferred schedule and frequency
4. ✅ Create channel branding (banner, profile pic)
5. ✅ Start generating content!

## Support

For issues:
1. Check this guide for troubleshooting
2. Review error logs in `logs/` directory
3. Check `.env` file configuration
4. Verify API keys are valid

---

**You're ready to start! Run:**
```bash
python main.py schedule
```

Happy automating! 🚀
