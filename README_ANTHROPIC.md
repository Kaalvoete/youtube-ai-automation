# Using Anthropic Claude for Free

This project now supports **Anthropic Claude** as the default AI provider. Claude has a free tier and is perfect for generating YouTube scripts without costs.

## Setup

### 1. Get an Anthropic API Key (Free)

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy it to your `.env` file:

```bash
ANTHROPIC_API_KEY=sk_ant_xxxxxxxxxxxxx
```

### 2. Install Dependencies

```bash
pip install anthropic
```

### 3. Run the System

The system now defaults to `anthropic`:

```bash
# Test with Claude
python main.py test

# Create a single video
python main.py create --prompt "ChatGPT automation hack"

# Start daily scheduler
python main.py schedule
```

## Why Claude?

✅ **Free tier available** - No credit card required initially  
✅ **High quality** - Claude 3.5 Sonnet is excellent for creative writing  
✅ **Fast responses** - Great for real-time video script generation  
✅ **No quota errors** - Free tier has fair usage limits  

## Free Tier Limits

- Generous free tier for development/testing
- If you exceed limits, you can upgrade to paid anytime
- Perfect for building and testing your automation system

## Switching Providers

If you want to use a different provider:

```python
# Use OpenAI instead
generator = ScriptGenerator(api_provider="openai")

# Or Cohere
generator = ScriptGenerator(api_provider="cohere")
```

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not found"**
- Make sure you've set `ANTHROPIC_API_KEY` in your `.env` file
- Reload your terminal after adding the key

**Error: "Install anthropic: pip install anthropic"**
- Run: `pip install anthropic`

**Error: UnicodeEncodeError with emojis**
- This has been fixed! The video generator now sanitizes emojis automatically.

## Next Steps

1. Get your free Anthropic API key at https://console.anthropic.com/
2. Add it to `.env`: `ANTHROPIC_API_KEY=your_key_here`
3. Install: `pip install anthropic`
4. Run: `python main.py test`
5. Create videos with no cost!
