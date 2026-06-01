#!/usr/bin/env python3
"""
AI Script Generator - Creates engaging scripts for YouTube videos
Uses OpenAI API, Anthropic Claude, Cohere, or free alternatives
"""

import os
import json
from typing import Dict, Tuple
from dotenv import load_dotenv

load_dotenv()

class ScriptGenerator:
    """
    Generates engaging YouTube scripts for AI & Automation content
    Supports: OpenAI, Anthropic Claude, Cohere
    """
    
    def __init__(self, api_provider: str = "anthropic"):
        self.api_provider = api_provider
        self.setup_client()
    
    def setup_client(self):
        """Initialize API client"""
        if self.api_provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
            except ImportError:
                print("Install openai: pip install openai")
                self.client = None
        
        elif self.api_provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            except ImportError:
                print("Install anthropic: pip install anthropic")
                self.client = None
        
        elif self.api_provider == "cohere":
            try:
                import cohere
                self.client = cohere.Client(os.getenv("COHERE_API_KEY"))
            except ImportError:
                print("Install cohere: pip install cohere")
                self.client = None
    
    def generate_script(self, prompt: str, video_type: str, duration: str = "3-5") -> Dict:
        """
        Generate a YouTube script from a prompt
        
        Args:
            prompt: User prompt (e.g., "ChatGPT hack to save 5 hours")
            video_type: Type of video ("short", "long", "tutorial", "comparison")
            duration: Video duration ("3-5" or "5-10")
        
        Returns:
            Dict with script, title, description, tags
        """
        
        system_prompt = f"""You are a YouTube content creator specializing in AI & Automation hacks.
Create engaging, viral-worthy scripts that keep viewers glued to the screen.
The script should be for a {video_type} video lasting {duration} minutes.

Format your response as JSON with:
- title: Catchy YouTube title (under 60 chars, include emojis)
- hook: First 10 seconds to grab attention (50-100 words)
- script: Full script with natural pauses and emphasis markers
- description: YouTube description (150+ chars)
- tags: List of 10 relevant tags
- cta: Call-to-action (subscribe, like, etc.)

Make it conversational, use numbers and emojis in title, and include a twist or surprise."""
        
        user_message = f"Create a YouTube video script about: {prompt}"
        
        try:
            if self.api_provider == "anthropic" and self.client:
                response = self.client.messages.create(
                    model="claude-opus-latest",
                    max_tokens=1500,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                script_text = response.content[0].text
            
            elif self.api_provider == "openai" and self.client:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                script_text = response.choices[0].message.content
            
            elif self.api_provider == "cohere" and self.client:
                response = self.client.generate(
                    prompt=f"{system_prompt}\n{user_message}",
                    max_tokens=1500,
                    temperature=0.7
                )
                script_text = response.generations[0].text
            
            else:
                # Fallback to local template if API not available
                return self._generate_template(prompt, video_type, duration)
            
            # Parse JSON response
            script_data = self._parse_script_response(script_text)
            return script_data
        
        except Exception as e:
            print(f"Error generating script: {e}")
            return self._generate_template(prompt, video_type, duration)
    
    def _parse_script_response(self, response_text: str) -> Dict:
        """Parse JSON from API response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback template
        return {
            "title": "AI Hack You Didn't Know About",
            "script": response_text,
            "description": "Check out this AI hack! Subscribe for more AI & automation tips.",
            "tags": ["AI", "automation", "tutorial", "hack", "productivity"]
        }
    
    def _generate_template(self, prompt: str, video_type: str, duration: str) -> Dict:
        """Generate a template script when API is unavailable"""
        return {
            "title": f"{prompt[:50]}... (WORKS!)",
            "hook": "Wait till the end - this is going to blow your mind...",
            "script": f"""Hey everyone! Today I'm showing you {prompt}.
            
[INTRO - 5 seconds]
Most people don't know this, but you can use AI to dramatically save time.

[MAIN CONTENT - {duration} minutes]
Here's how it works:
1. First step
2. Second step  
3. Third step

[RESULTS]
As you can see, this is incredible.

[CTA - 10 seconds]
If you found this helpful, smash that like button and subscribe for more hacks!
""",
            "description": f"Learn about {prompt}. Free tools and hacks for AI automation. Subscribe for daily content!",
            "tags": ["AI", "automation", "tutorial", "hack", "productivity", "tools", "chatgpt"],
            "cta": "Subscribe for more AI hacks!"
        }


if __name__ == "__main__":
    # Test the script generator
    generator = ScriptGenerator(api_provider="anthropic")
    
    script = generator.generate_script(
        prompt="ChatGPT hack to save 5 hours per week",
        video_type="tutorial",
        duration="5-min"
    )
    
    print(json.dumps(script, indent=2))
