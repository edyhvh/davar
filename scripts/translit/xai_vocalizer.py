"""
xAI-powered Hebrew vocalization for DSS phrases.

This module adds niqqud (vowel marks) to unpointed DSS words/phrases using
xAI Responses API, then caches results to minimize repeated API usage.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import httpx
from openai import OpenAI

from scripts.dict.utils import extract_json_array_robust

from .config import (
    DSS_VOCALIZATION_CACHE_PATH,
    DSS_XAI_MAX_CHARS_PER_REQUEST,
    XAI_API_KEY,
    XAI_BASE_URL,
    XAI_MAX_RETRIES,
    XAI_RATE_LIMIT_DELAY_SECONDS,
    XAI_RETRY_BACKOFF_BASE,
    XAI_TIMEOUT_SECONDS,
    XAI_VOCALIZATION_MODEL,
)

logger = logging.getLogger(__name__)


class XaiDssVocalizer:
    """Adds niqqud to DSS phrases with character-budget batching and local cache."""

    def __init__(
        self,
        max_chars_per_request: int | None = None,
        cache_path: Path = DSS_VOCALIZATION_CACHE_PATH,
    ) -> None:
        if not XAI_API_KEY:
            raise ValueError(
                "XAI_API_KEY is required for DSS vocalization. "
                "Set it in .env or environment variables."
            )

        self.client = OpenAI(
            api_key=XAI_API_KEY,
            base_url=XAI_BASE_URL,
            timeout=httpx.Timeout(XAI_TIMEOUT_SECONDS),
        )
        self.model_name = XAI_VOCALIZATION_MODEL
        self.max_chars_per_request = max(500, max_chars_per_request or DSS_XAI_MAX_CHARS_PER_REQUEST)
        self.cache_path = cache_path
        self.cache = self._load_cache()
        self._last_request_time = 0.0
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "api_calls": 0,
            "failed_batches": 0,
        }

    def _load_cache(self) -> Dict[str, str]:
        if not self.cache_path.exists():
            return {}

        try:
            with open(self.cache_path, "r", encoding="utf-8") as file_obj:
                payload = json.load(file_obj)
            if not isinstance(payload, dict):
                return {}
            return {
                str(key): str(value)
                for key, value in payload.items()
                if isinstance(key, str) and isinstance(value, str)
            }
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.warning("Failed to read vocalization cache %s: %s", self.cache_path, exc)
            return {}

    def save_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.cache_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as file_obj:
            json.dump(self.cache, file_obj, ensure_ascii=False, separators=(",", ":"))
        temp_path.replace(self.cache_path)

    def get_stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < XAI_RATE_LIMIT_DELAY_SECONDS:
            time.sleep(XAI_RATE_LIMIT_DELAY_SECONDS - elapsed)
        self._last_request_time = time.time()

    @staticmethod
    def _item_cost(text: str) -> int:
        # Conservative estimate to account for JSON framing and metadata fields.
        return len(text) + 64

    def _pack_batches(self, items: Iterable[Tuple[str, str]]) -> List[List[Tuple[str, str]]]:
        batches: List[List[Tuple[str, str]]] = []
        current: List[Tuple[str, str]] = []
        current_chars = 0

        for item_id, text in items:
            cost = self._item_cost(text)
            if cost > self.max_chars_per_request:
                if current:
                    batches.append(current)
                    current = []
                    current_chars = 0
                batches.append([(item_id, text)])
                continue

            if current_chars + cost > self.max_chars_per_request and current:
                batches.append(current)
                current = []
                current_chars = 0

            current.append((item_id, text))
            current_chars += cost

        if current:
            batches.append(current)

        return batches

    @staticmethod
    def _build_prompt(batch: List[Tuple[str, str]]) -> str:
        payload = [{"id": item_id, "text": text} for item_id, text in batch]
        return (
            "Add Hebrew niqqud (vowel points) to each Hebrew text value. "
            "Preserve consonants exactly and do not translate. "
            "Return ONLY a JSON array of objects with this schema: "
            "[{\"id\": string, \"vocalized_text\": string}].\n\n"
            f"Input:\n{json.dumps(payload, ensure_ascii=False)}"
        )

    @staticmethod
    def _extract_text_content(response: object) -> str:
        parts: List[str] = []
        output_items = getattr(response, "output", None) or []

        for output_item in output_items:
            content = getattr(output_item, "content", None) or []
            if isinstance(content, list):
                for content_item in content:
                    text_value = getattr(content_item, "text", None)
                    if isinstance(text_value, str) and text_value.strip():
                        parts.append(text_value)

        if not parts:
            fallback_text = getattr(response, "output_text", None)
            if isinstance(fallback_text, str) and fallback_text.strip():
                parts.append(fallback_text)

        if not parts:
            raise ValueError("xAI vocalization response did not contain text output")

        return "\n".join(parts)

    @staticmethod
    def _parse_batch_result(raw_text: str, expected_ids: List[str]) -> Dict[str, str]:
        parsed = extract_json_array_robust(raw_text)
        if not isinstance(parsed, list):
            raise ValueError("xAI response is not a JSON array")

        expected = set(expected_ids)
        result: Dict[str, str] = {}

        for item in parsed:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "")).strip()
            vocalized_text = str(item.get("vocalized_text", "")).strip()
            if item_id in expected and vocalized_text:
                result[item_id] = vocalized_text

        missing = [item_id for item_id in expected_ids if item_id not in result]
        if missing:
            raise ValueError(f"xAI response missing ids: {missing[:5]}")

        return result

    def _request_batch(self, batch: List[Tuple[str, str]], retry_count: int = 0) -> Dict[str, str]:
        try:
            self._rate_limit()
            self._stats["api_calls"] += 1
            prompt = self._build_prompt(batch)

            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {
                        "role": "system",
                        "content": "You are an expert Biblical Hebrew vocalization assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            raw_text = self._extract_text_content(response)
            return self._parse_batch_result(raw_text, [item_id for item_id, _ in batch])
        except Exception as exc:
            if retry_count >= XAI_MAX_RETRIES:
                raise ValueError(f"xAI vocalization failed after retries: {exc}") from exc

            self._stats["failed_batches"] += 1
            wait_seconds = XAI_RETRY_BACKOFF_BASE ** retry_count
            logger.warning(
                "xAI vocalization batch retry %s/%s in %ss: %s",
                retry_count + 1,
                XAI_MAX_RETRIES,
                wait_seconds,
                exc,
            )
            time.sleep(wait_seconds)
            return self._request_batch(batch, retry_count + 1)

    def _request_with_split_fallback(
        self,
        batch: List[Tuple[str, str]],
    ) -> Dict[str, str]:
        if not batch:
            return {}

        try:
            return self._request_batch(batch)
        except Exception as exc:
            if len(batch) == 1:
                item_id, original_text = batch[0]
                logger.warning(
                    "xAI vocalization failed for single item %s, using original text: %s",
                    item_id,
                    exc,
                )
                return {item_id: original_text}

            midpoint = len(batch) // 2
            left = self._request_with_split_fallback(batch[:midpoint])
            right = self._request_with_split_fallback(batch[midpoint:])
            merged = dict(left)
            merged.update(right)
            return merged

    def vocalize_phrases(self, phrases: List[str]) -> Dict[str, str]:
        if not phrases:
            return {}

        unique_phrases = list(dict.fromkeys(phrase for phrase in phrases if phrase and phrase.strip()))
        if not unique_phrases:
            return {}

        results: Dict[str, str] = {}
        pending: List[Tuple[str, str]] = []

        for index, phrase in enumerate(unique_phrases):
            cached = self.cache.get(phrase)
            if cached:
                self._stats["cache_hits"] += 1
                results[phrase] = cached
                continue

            self._stats["cache_misses"] += 1
            pending.append((f"p{index}", phrase))

        if not pending:
            return results

        id_to_phrase = {item_id: phrase for item_id, phrase in pending}
        batches = self._pack_batches(pending)

        for batch in batches:
            batch_results = self._request_with_split_fallback(batch)
            for item_id, vocalized_text in batch_results.items():
                phrase = id_to_phrase[item_id]
                results[phrase] = vocalized_text
                self.cache[phrase] = vocalized_text

        return results
