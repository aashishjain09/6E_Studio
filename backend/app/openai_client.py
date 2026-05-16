import os
from typing import Optional

from openai import OpenAI


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # Only instantiate the real client when a key is present.
        # This keeps the app runnable without secrets (stub mode).
        self._client: Optional[OpenAI] = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_text(self, prompt: str) -> str:
        if self._client is None:
            # Stub: return a clearly labelled placeholder so UI can render it.
            return f"[stub] Campaign copy for: {prompt[:120]}"

        response = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative studio assistant."},
                {
                    "role": "user",
                    "content": f"Generate campaign copy for the following brief: {prompt}",
                },
            ],
            max_tokens=300,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()

    def generate_image(self, prompt: str) -> Optional[str]:
        if self._client is None:
            # Stub: return a public placeholder image so the UI renders something.
            return "https://placehold.co/512x512/1a1a2e/ffffff?text=6E+Studio"

        response = self._client.images.generate(
            model="dall-e-3",          # dall-e-3 is the current default; swap to dall-e-2 for cheaper runs
            prompt=prompt,
            n=1,
            size="1024x1024",          # dall-e-3 minimum; use "512x512" only for dall-e-2
            response_format="url",
        )
        return response.data[0].url