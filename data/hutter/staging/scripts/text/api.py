"""Claude API client with retry logic and error handling."""

import os
import io
import time
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PIL import Image

logger = logging.getLogger(__name__)

# Maximum image size in bytes (5MB for base64)
MAX_IMAGE_SIZE_BYTES = 3.75 * 1024 * 1024

# Lazy import for anthropic
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None


class ClaudeClient:
    """Claude API client with retry logic and error handling."""

    AVAILABLE_MODELS = [
        'claude-sonnet-4-5',
        'claude-opus-4-5',
        'claude-opus-4',
        'claude-sonnet-4',
        'claude-3-5-sonnet-latest',
    ]

    MODEL_ALIASES = {
        'sonnet-4.5': 'claude-sonnet-4-5',
        'sonnet-4-5': 'claude-sonnet-4-5',
        'opus-4.5': 'claude-opus-4-5',
        'opus-4-5': 'claude-opus-4-5',
        'opus-4': 'claude-opus-4',
        'opus': 'claude-opus-4-5',
        'sonnet-4': 'claude-sonnet-4',
        'sonnet': 'claude-sonnet-4-5',
    }

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model_name: Model to use (defaults to sonnet-4.5)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )

        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it as environment variable.\n"
                "Get your API key from: https://console.anthropic.com/settings/keys"
            )

        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)
        self.model_name = self.MODEL_ALIASES.get(model_name, model_name) if model_name else self.AVAILABLE_MODELS[0]
        logger.info(f"Claude client initialized with model: {self.model_name}")

    def transcribe_image(self, image_path: Path, prompt: str) -> Dict[str, Any]:
        """
        Send image to Claude API for transcription.

        Args:
            image_path: Path to image file
            prompt: Prompt text

        Returns:
            Dictionary with 'text' and 'usage' keys
        """
        def _call_api():
            image_data, media_type = self._encode_image(image_path)

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": prompt}
                    ],
                }],
            )

            text = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, 'text'):
                        text += block.text

            usage = {
                'prompt_tokens': response.usage.input_tokens if response.usage else 0,
                'completion_tokens': response.usage.output_tokens if response.usage else 0,
                'total_tokens': (
                    (response.usage.input_tokens if response.usage else 0) +
                    (response.usage.output_tokens if response.usage else 0)
                )
            }

            return {'text': text, 'usage': usage}

        return self._retry_with_backoff(_call_api)

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image as base64 with automatic compression if needed."""
        file_size = image_path.stat().st_size
        ext = image_path.suffix.lower()

        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        original_media_type = media_types.get(ext, 'image/png')

        if file_size < MAX_IMAGE_SIZE_BYTES:
            with open(image_path, 'rb') as f:
                return base64.standard_b64encode(f.read()).decode('utf-8'), original_media_type

        logger.info(f"Compressing {image_path.name} ({file_size / 1024 / 1024:.2f}MB)...")
        img = Image.open(image_path)

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        for quality in [95, 90, 85, 80, 75, 70, 60, 50]:
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            if buffer.tell() < MAX_IMAGE_SIZE_BYTES:
                logger.info(f"Compressed to {buffer.tell() / 1024 / 1024:.2f}MB (quality={quality})")
                buffer.seek(0)
                return base64.standard_b64encode(buffer.read()).decode('utf-8'), 'image/jpeg'

        # Resize if still too large
        width, height = img.size
        for scale in [0.9, 0.8, 0.7, 0.6, 0.5]:
            new_w, new_h = int(width * scale), int(height * scale)
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            resized.save(buffer, format='JPEG', quality=85, optimize=True)
            if buffer.tell() < MAX_IMAGE_SIZE_BYTES:
                logger.info(f"Resized to {new_w}x{new_h}")
                buffer.seek(0)
                return base64.standard_b64encode(buffer.read()).decode('utf-8'), 'image/jpeg'

        raise ValueError(f"Cannot compress image {image_path.name} to under 5MB")

    def _retry_with_backoff(self, func, max_retries: int = 5) -> Any:
        """Execute function with exponential backoff retry."""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                error_code = self._get_error_code(e)

                if error_code in [400, 401, 404]:
                    logger.error(f"Non-retryable error ({error_code}): {e}")
                    raise

                wait_time = min(2 ** attempt, 60)

                if error_code == 429:
                    retry_after = self._get_retry_after(e)
                    wait_time = retry_after if retry_after else wait_time

                logger.warning(f"Error (attempt {attempt + 1}/{max_retries}): {e}. Waiting {wait_time}s...")
                time.sleep(wait_time)

        logger.error(f"Failed after {max_retries} attempts: {last_exception}")
        raise last_exception

    def _get_error_code(self, error: Exception) -> Optional[int]:
        """Extract HTTP error code from exception."""
        if hasattr(error, 'status_code'):
            return error.status_code
        if hasattr(error, 'code'):
            return error.code

        error_str = str(error).lower()
        patterns = [
            ('404', 404), ('not found', 404), ('429', 429), ('rate limit', 429),
            ('401', 401), ('unauthorized', 401), ('400', 400), ('bad request', 400),
            ('500', 500), ('502', 502), ('503', 503), ('529', 529)
        ]
        for pattern, code in patterns:
            if pattern in error_str:
                return code
        return None

    def _get_retry_after(self, error: Exception) -> Optional[int]:
        """Extract Retry-After header value."""
        if hasattr(error, 'response') and hasattr(error.response, 'headers'):
            retry_after = error.response.headers.get('Retry-After')
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass
        return None

    @staticmethod
    def estimate_cost() -> float:
        """Estimated cost per image (~$0.01)."""
        return 0.01

