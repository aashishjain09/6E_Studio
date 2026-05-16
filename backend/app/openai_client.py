import os
from typing import Optional

import openai

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            return f"[sample generated text] {prompt[:120]}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative studio assistant."},
                {"role": "user", "content": f"Generate a campaign copy for: {prompt}"},
            ],
            max_tokens=200,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()

    def generate_image(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return "https://via.placeholder.com/512x320.png?text=6E+Creative+Studio"

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
        )
        return response.data[0].url
