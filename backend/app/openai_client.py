# backend/app/openai_client.py
import base64
import os
from pathlib import Path
from typing import Optional
from uuid import uuid4

from openai import OpenAI

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "generated_images"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.text_model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
        self.image_model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
        self.image_size = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")
        self._client: Optional[OpenAI] = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_text(self, prompt: str) -> str:
        if self._client is None:
            return f"[stub] Campaign copy for: {prompt[:120]}"

        response = self._client.responses.create(
            model=self.text_model,
            instructions=(
                "You are a senior social media copywriter. "
                "Write concise, ready-to-post campaign text. "
                "Return only the final answer, no preamble."
            ),
            input=(
                "Create social content for this brief:\n"
                f"{prompt}\n\n"
                "Return a strong caption, CTA, and short hashtag set."
            ),
        )

        text = getattr(response, "output_text", "")
        return text.strip() if text else "No text was returned by the model."

    def generate_image(self, prompt: str) -> Optional[str]:
        if self._client is None:
            return None

        result = self._client.images.generate(
            model=self.image_model,
            prompt=prompt,
            n=1,
            size=self.image_size,
        )

        if not result.data or not getattr(result.data[0], "b64_json", None):
            return None

        image_bytes = base64.b64decode(result.data[0].b64_json)
        out_path = DATA_DIR / f"{uuid4().hex}.png"
        out_path.write_bytes(image_bytes)
        return str(out_path)