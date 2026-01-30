"""
Claude-powered DSS commentary rewriter.

Uses Claude Haiku 4.5 to assign Strong's numbers and generate
reverent trilingual commentaries for Dead Sea Scrolls variants.
"""

import json
import time
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    from anthropic import Anthropic
except ImportError as e:
    raise ImportError(
        "Commentary rewriter requires 'anthropic' package. Install with: pip install anthropic"
    ) from e

from .config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_API_VERSION,
    CLAUDE_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF_BASE,
    RATE_LIMIT_DELAY,
    TEMPERATURE,
    validate_anthropic_api_key,
)

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an assistant helping build reverent, distraction-free study notes for a Tanaj reading app called Davar (דבר).

Your task is to rewrite scholarly commentaries about textual variants found in Qumran scrolls (Dead Sea Scrolls) compared to other ancient witnesses.

Guidelines you MUST follow strictly:

• Tone: calm, gentle, almost meditative — like quietly explaining a verse to someone during personal study time.
• Replace technical terms with simple, respectful language:
  - 4QGenX, 4QSamX, etc. → "a Qumran scroll" or "one scroll from Qumran"
  - Masoretic / Mas → "the traditional Hebrew Tanaj text" or "the standard Hebrew text"
  - LXX → "the old Greek translation"
  - SP → "the Samaritan version"
  - homoeoteleuton → "a copying mistake caused by similar-looking phrases nearby"
  - variant spelling, scribal mistake/error → "a small spelling difference" or "a copying slip"
  - transmission → "while the text was being copied over time"
• Structure: Write 2–4 short connected sentences in flowing prose (no bullets, no labels):
  1. State which ancient copies / witnesses say what (group similar ones)
  2. Describe the actual difference in plain words
  3. Explain (briefly & respectfully) why the difference probably happened and whether it changes the overall meaning
• Keep reverence for the sacred text at all times. Never sound academic, dry or skeptical.
• Output ONLY valid JSON — no extra text, no explanations, no markdown.

Additionally, you MUST assign Strong's numbers to both the Masoretic and DSS Hebrew words:
• Use format: H#### (e.g., H1234)
• If a word has multiple Strong's numbers (e.g., prefixes + root), use comma-separated: H1234,H5678
• If you cannot determine a Strong's number, use empty string: ""
• Consider Hebrew prefixes (ו, ה, ל, מ, etc.) when analyzing words
• Base Strong's assignment on your knowledge of biblical Hebrew lexicon
"""


class DSSCommentaryRewriter:
    """Rewriter using Claude API for DSS commentaries."""

    def __init__(self):
        """Initialize the rewriter with API key."""
        if not validate_anthropic_api_key():
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables. "
                "Please set it in .env file or as an environment variable."
            )

        self.client = Anthropic(
            api_key=ANTHROPIC_API_KEY,
            timeout=CLAUDE_TIMEOUT,
        )
        self.model_name = CLAUDE_MODEL
        self._last_request_time = 0
        self._stats = {
            'total_batches': 0,
            'total_differences': 0,
            'successful': 0,
            'failed': 0,
        }

    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < RATE_LIMIT_DELAY:
            sleep_time = RATE_LIMIT_DELAY - time_since_last
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def _generate_prompt(self, differences: List[Dict]) -> str:
        """
        Generate prompt for batch commentary rewriting.
        
        Args:
            differences: List of difference dictionaries
            
        Returns:
            Formatted prompt string
        """
        input_array = []
        for diff in differences:
            input_array.append({
                "position": diff['position'],
                "masoretic_word": diff['masoretic_word'],
                "dss_word": diff['dss_word'],
                "commentary": diff['commentary'],
            })
        
        prompt = f"""Task: Enhance DSS variant commentaries with Strong's numbers and trilingual reverent explanations.

Input: A list of {len(differences)} textual differences between Dead Sea Scrolls and Masoretic text.

Output: Return the SAME array with these fields ADDED to each entry:
- "masoretic_strong": Strong's number(s) for masoretic_word (format: "H####" or "H####,H####", empty string "" if unknown)
- "dss_strong": Strong's number(s) for dss_word (format: "H####" or "H####,H####", empty string "" if unknown)
- "commentary_en": Rewritten English commentary following the guidelines
- "commentary_es": Spanish translation of the commentary
- "commentary_he": Hebrew translation of the commentary
- "original_commentary": Copy of the original commentary field (preserve as-is)

Input array:
{json.dumps(input_array, ensure_ascii=False, indent=2)}

Return ONLY a valid JSON array with the enhanced entries. No markdown, no code blocks, no explanations."""

        return prompt

    def _extract_json_array_robust(self, text: str) -> List:
        """Extract JSON array from text using robust bracket-matching algorithm."""
        def normalize_json_array(result: object) -> Optional[List]:
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                for key in ("data", "items", "results", "entries", "output", "response"):
                    value = result.get(key)
                    if isinstance(value, list):
                        return value
                if len(result) == 1:
                    only_value = next(iter(result.values()))
                    if isinstance(only_value, list):
                        return only_value
            return None

        def try_parse_fragment(fragment: str, source: str = "unknown") -> Optional[List]:
            try:
                parsed = json.loads(fragment)
                normalized = normalize_json_array(parsed)
                if normalized is not None:
                    logger.debug(f"Successfully parsed JSON from {source} (extracted {len(normalized)} items)")
                return normalized
            except json.JSONDecodeError as e:
                logger.debug(f"Parse failed from {source}: {e}")
                return None

        logger.debug(f"Starting JSON extraction from text of length {len(text)}")
        
        # Strip whitespace once at the start
        text = text.strip()
        
        # Direct parse attempt - most efficient if response is clean JSON
        result = try_parse_fragment(text, "direct")
        if result is not None:
            return result

        # Extract from markdown fenced code blocks (```json ... ``` or ``` ... ```)
        # This regex handles both ```json and ``` opening fences
        code_block_pattern = r'```(?:json)?\s*\n([\s\S]*?)\n```'
        code_matches = re.findall(code_block_pattern, text)
        for match in code_matches:
            fragment = match.strip()
            if fragment:
                logger.debug(f"Trying fenced code block: length={len(fragment)}")
                result = try_parse_fragment(fragment, "fenced block")
                if result is not None:
                    return result

        # Also try simpler fence pattern without newlines
        simple_fence_pattern = r'```(?:json)?([\s\S]*?)```'
        simple_matches = re.findall(simple_fence_pattern, text)
        for match in simple_matches:
            fragment = match.strip()
            if fragment:
                result = try_parse_fragment(fragment, "simple fenced block")
                if result is not None:
                    return result

        # Trim to first JSON structure (find the outermost [ or { and its closing pair)
        first_brace = text.find('{')
        first_bracket = text.find('[')
        if first_brace != -1 or first_bracket != -1:
            start_candidates = [pos for pos in (first_brace, first_bracket) if pos != -1]
            start_index = min(start_candidates) if start_candidates else -1
            last_brace = text.rfind('}')
            last_bracket = text.rfind(']')
            end_candidates = [pos for pos in (last_brace, last_bracket) if pos != -1]
            end_index = max(end_candidates) if end_candidates else -1
            if start_index != -1 and end_index != -1 and end_index > start_index:
                candidate = text[start_index:end_index + 1]
                logger.debug(f"Trimmed to JSON structure: length={len(candidate)}")
                result = try_parse_fragment(candidate, "trimmed")
                if result is not None:
                    return result

        # Use bracket matching fallback for complex nested structures
        try:
            arrays = self._find_largest_json_array(text)
            if arrays:
                logger.debug(f"Bracket matching found array with {len(arrays)} items")
                return arrays
        except Exception as e:
            logger.debug(f"Bracket matching failed: {e}")

        logger.error(f"All extraction methods failed. Text preview: {repr(text[:500])}...")
        logger.error(f"Text ends with: ...{repr(text[-200:])}")
        raise json.JSONDecodeError("No valid JSON array found", text, 0)

    def _find_largest_json_array(self, text: str) -> Optional[List]:
        """Find the largest valid JSON array using bracket matching."""
        candidates = []

        for i, char in enumerate(text):
            if char == '[':
                bracket_count = 1
                end_pos = i + 1

                while end_pos < len(text) and bracket_count > 0:
                    if text[end_pos] == '[':
                        bracket_count += 1
                    elif text[end_pos] == ']':
                        bracket_count -= 1
                    end_pos += 1

                if bracket_count == 0:
                    array_text = text[i:end_pos]
                    try:
                        result = json.loads(array_text)
                        if isinstance(result, list):
                            candidates.append(result)
                    except json.JSONDecodeError:
                        continue

        if candidates:
            return max(candidates, key=len)

        return None

    def rewrite_batch(
        self,
        differences: List[Dict],
        retry_count: int = 0,
        batch_index: Optional[int] = None
    ) -> List[Dict]:
        """
        Rewrite a batch of DSS commentaries with Strong's numbers.
        
        Args:
            differences: List of difference dictionaries
            retry_count: Current retry attempt
            batch_index: Optional batch number for logging
            
        Returns:
            List of enhanced difference dictionaries
            
        Raises:
            ValueError: If rewriting fails after max retries
        """
        if not differences:
            return []

        self._rate_limit()
        self._stats['total_batches'] += 1
        self._stats['total_differences'] += len(differences)

        response_text = None

        try:
            prompt = self._generate_prompt(differences)
            
            logger.info(f"Making API call to {self.model_name} with {len(differences)} differences")
            logger.debug(f"Prompt length: {len(prompt)} characters")

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=16384,  # Increased for trilingual output (~400 tokens per item)
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            logger.debug("API call completed")

            if not response.content or len(response.content) == 0:
                raise ValueError("Empty response from Claude API")

            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            if not response_text:
                raise ValueError("Could not extract text content from response")

            response_text = response_text.strip()
            logger.debug(f"Extracted response text: {len(response_text)} characters")

            enhanced = self._extract_json_array_robust(response_text)

            if not isinstance(enhanced, list):
                raise ValueError("Response is not a JSON array")

            if len(enhanced) != len(differences):
                logger.warning(
                    f"Count mismatch: expected {len(differences)}, got {len(enhanced)}"
                )

            for i, diff in enumerate(differences):
                if i < len(enhanced):
                    diff.update(enhanced[i])

            self._stats['successful'] += len(enhanced)
            logger.info(f"Successfully processed {len(enhanced)} differences")

            return differences

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            if response_text:
                logger.debug(f"Response text length: {len(response_text)} characters")
                # Save failed response to debug file
                debug_dir = Path(__file__).parent.parent.parent.parent / 'debug' / 'output'
                debug_dir.mkdir(parents=True, exist_ok=True)
                debug_file = debug_dir / f'failed_response_{int(time.time())}.txt'
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write("=== RAW RESPONSE TEXT ===\n\n")
                        f.write(response_text)
                        f.write("\n\n=== ERROR ===\n\n")
                        f.write(str(e))
                    logger.error(f"Saved failed response to {debug_file} for inspection")
                except Exception as save_error:
                    logger.debug(f"Could not save debug file: {save_error}")

            if retry_count < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_BASE ** retry_count
                logger.info(f"Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(wait_time)
                return self.rewrite_batch(differences, retry_count + 1, batch_index)
            else:
                if len(differences) > 1:
                    mid = len(differences) // 2
                    logger.warning(
                        f"Parsing failed after retries. Splitting batch of {len(differences)} into {mid} and {len(differences) - mid}."
                    )
                    first_half = self.rewrite_batch(differences[:mid], 0, batch_index)
                    second_half = self.rewrite_batch(differences[mid:], 0, batch_index)
                    return first_half + second_half
                self._stats['failed'] += len(differences)
                raise ValueError(f"Failed to parse response after {MAX_RETRIES} retries: {e}")

        except Exception as e:
            error_str = str(e)
            logger.error(f"Rewriting error: {error_str}")

            wait_time = None
            if "429" in error_str or "overloaded" in error_str.lower() or "rate" in error_str.lower():
                retry_match = re.search(r'retry.*?(\d+(?:\.\d+)?)', error_str, re.IGNORECASE)
                wait_time = float(retry_match.group(1)) if retry_match else 60.0
                logger.info(f"Rate limit detected. Waiting {wait_time:.1f} seconds...")

            if retry_count < MAX_RETRIES:
                if wait_time is None:
                    wait_time = RETRY_BACKOFF_BASE ** retry_count
                logger.info(f"Retrying in {wait_time:.1f} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(wait_time)
                return self.rewrite_batch(differences, retry_count + 1, batch_index)
            else:
                self._stats['failed'] += len(differences)
                raise ValueError(f"Rewriting failed after {MAX_RETRIES} retries: {e}")

    def get_stats(self) -> Dict:
        """Get processing statistics."""
        return self._stats.copy()