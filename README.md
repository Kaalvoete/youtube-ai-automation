# 🎬 AI YouTube Automation System

**Automated AI & Automation Hacks content generation and upload to YouTube**

Generate 2+ videos daily with zero manual editing. AI creates scripts, videos, and uploads automatically.

## ✨ Features

- ✅ **AI Script Generation** - Creates engaging, viral-worthy scripts
- ✅ **Automated Video Creation** - Generates Shorts (60s) + Long-form (3-5 min)
- ✅ **Auto-Upload to YouTube** - Directly uploads to your channel
- ✅ **Daily Scheduling** - Runs 24/7 completely automated
- ✅ **SEO Optimization** - Titles, descriptions, tags, thumbnails
- ✅ **Zero Manual Work** - Fully hands-off operation
- ✅ **100% Free** - All APIs have generous free tiers

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Kaalvoete/youtube-ai-automation.git
cd youtube-ai-automation

# 2. Setup (interactive configuration)
python setup.py

# 3. Test the system
python main.py test

# 4. Create your first video
python main.py create --prompt "ChatGPT hack to save 5 hours" --upload

# 5. Start daily automation
python main.py schedule
```

## 📊 What It Does

### Input
```
"ChatGPT hack to save 5 hours per week"
```

### Output (Automated)
1. **Script** - Engaging hook, main content, call-to-action
2. **Videos** - Shorts (60s) + Long-form (5 min)
3. **Metadata** - SEO title, description, tags
4. **Upload** - Posts to YouTube automatically
5. **Schedule** - Ready for next video

## 💻 System Requirements

- Python 3.9+
- FFmpeg (free, open-source)
- API Keys (all free tiers)

## 🔑 Free API Setup

### Required
- **OpenAI API** - Script generation ($5 free credits)
- **YouTube API** - Upload videos (free)
- **YouTube Channel** - Your channel to upload to

### Optional (Better quality)
- **ElevenLabs** - Realistic AI voices (10K chars free)
- **Cohere** - Alternative script generation (free tier)

See `SETUP.md` for detailed instructions.

## 📁 Project Structure

```
├── main.py                    # CLI entry point
├── setup.py                   # Configuration wizard
├── requirements.txt           # Python dependencies
├── .env.example              # API credentials template
├── SETUP.md                  # Full setup guide
│
├── scripts/
│   ├── script_generator.py    # AI script creation
│   ├── video_generator.py     # Video file generation
│   ├── uploader.py            # YouTube uploader
│   └── scheduler.py           # Daily automation
│
├── config/
│   ├── config.yml             # Settings (times, niche, etc)
│   └── prompts.txt            # Daily video prompts (20 ready-to-use)
│
└── output/                    # Generated videos (auto-created)
```

## 🎯 Commands

```bash
# Create a single video
python main.py create --prompt "Your prompt here" --upload

# Create without uploading (test)
python main.py create --prompt "Your prompt" 

# Start daily scheduler (runs 24/7)
python main.py schedule

# Run system tests
python main.py test

# Configure API keys and settings
python main.py setup
```

## 💰 Cost

**$0/month**

- OpenAI: $5 free credits (covers ~500 videos)
- YouTube API: Unlimited free
- ElevenLabs: 10,000 characters free (covers ~500 videos)
- FFmpeg: Open source
- Storage: Use free tier

## 📈 Daily Output

With default settings:
- **2 videos per day** (customizable)
- **Upload at 9 AM** (customizable)
- **Mix of Shorts + Long-form** (customizable)
- **20 pre-made prompts** included (easy to add more)

## 🔧 Customization

### Change Daily Prompts
Edit `config/prompts.txt`:
```
Tool Tutorial | Your prompt here | 5-min
Life Hack | Another prompt | 3-min-short
```

### Change Upload Time
Edit `config/config.yml`:
```yaml
upload:
  time_of_day: "14:00"  # 2 PM instead of 9 AM
  videos_per_day: 3     # Upload 3 instead of 2
```

### Change Video Length
Edit `.env`:
```
VIDEO_LENGTH_SHORTS=60
VIDEO_LENGTH_LONG=300  # Change to 600 for 10 mins
```

## 🐛 Troubleshooting

**API key error?**
- Run `python setup.py` again
- Check `.env` file has correct keys

**FFmpeg not found?**
- Install: `brew install ffmpeg` (Mac) or `sudo apt install ffmpeg` (Linux)

**YouTube upload fails?**
- Verify YouTube API is enabled
- Check `youtube_credentials.json` exists
- Confirm channel ID in `.env`

**Module not found?**
- Run `pip install -r requirements.txt`

## 📊 Getting Views Fast

1. **Trending Niche** - AI & Automation is hot in 2026
2. **Daily Uploads** - Algorithm loves consistency
3. **Shorts + Long-form** - YouTube recommends both
4. **SEO Optimized** - System auto-optimizes titles/tags
5. **Engaging Scripts** - AI creates viral-worthy content

## 👥 Support

For issues:
1. Check `SETUP.md` for detailed help
2. Review `config/config.yml` for all settings
3. See error logs in `logs/` directory

## 📝 License

MIT - Use freely, modify as needed

---

**Ready to start?** See `SETUP.md` for step-by-step instructions! 🚀
