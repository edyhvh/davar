"""
Grok API translator module.

Handles batch translation of English definitions to target languages using
xAI's Grok API (grok-3-mini model).
"""

import json
import time
import logging
import re
from typing import Dict, List, Optional

try:
    import httpx
    from openai import OpenAI
except ImportError as e:
    raise ImportError(
        "Grok translator requires 'openai' package. Install with: pip install openai"
    ) from e

from .config import (
    XAI_API_KEY,
    GROK_MODEL,
    GROK_BASE_URL,
    GROK_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF_BASE,
    RATE_LIMIT_DELAY,
    get_language_name,
    validate_grok_api_key,
)

logger = logging.getLogger(__name__)


class GrokTranslator:
    """Translator using xAI Grok API."""

    def __init__(self):
        """
        Initialize the translator with API key.
        """
        if not validate_grok_api_key():
            raise ValueError(
                "XAI_API_KEY not found in environment variables. "
                "Please set it in .env file or as an environment variable."
            )

        # Initialize OpenAI client with Grok base URL
        self.client = OpenAI(
            api_key=XAI_API_KEY,
            base_url=GROK_BASE_URL,
            timeout=httpx.Timeout(GROK_TIMEOUT),
        )
        self.model_name = GROK_MODEL
        self._last_request_time = 0
        self._mismatch_stats = {
            'total_batches': 0,
            'mismatched_batches': 0,
            'total_padding': 0,
            'total_truncation': 0,
            'mismatch_patterns': {}
        }
    
    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < RATE_LIMIT_DELAY:
            sleep_time = RATE_LIMIT_DELAY - time_since_last
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def _generate_prompt(self, texts: List[str], target_lang: str) -> str:
        """
        Generate translation prompt for batch translation.
        
        Args:
            texts: List of English definition texts to translate
            target_lang: Target language code (e.g., 'es', 'pt')
            
        Returns:
            Formatted prompt string
        """
        lang_name = get_language_name(target_lang) or target_lang
        
        prompt = f"""Translate these Hebrew dictionary definitions from English to {lang_name}.
Maintain technical accuracy and preserve biblical terminology.

Return ONLY a valid JSON array with the translations in the same order as the input.
Do not include any explanations, comments, or additional text - just the JSON array.

Input definitions:
"""
        for i, text in enumerate(texts, 1):
            prompt += f"{i}. {text}\n"
        
        prompt += "\nReturn the translations as a JSON array:"

        return prompt

    def _extract_json_array_robust(self, text: str) -> List:
        """
        Extract JSON array from text using robust bracket-matching algorithm.

        This method tries multiple strategies in order:
        1. Direct JSON parsing
        2. Extract from markdown code blocks
        3. Find the largest valid JSON array using bracket matching
        4. Fallback to improved regex patterns

        Args:
            text: Text that may contain a JSON array

        Returns:
            List of extracted translations

        Raises:
            json.JSONDecodeError: If no valid JSON array can be found
        """
        # Strategy 1: Try direct JSON parsing
        try:
            result = json.loads(text)
            if isinstance(result, list):
                logger.debug("Successfully parsed JSON directly")
                return result
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code blocks
        import re
        markdown_patterns = [
            r'```json\s*(\[.*?\])\s*```',  # ```json [content] ```
            r'```\s*(\[.*?\])\s*```',  # ``` [content] ```
        ]

        for pattern in markdown_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    result = json.loads(match)
                    if isinstance(result, list):
                        logger.debug("Successfully extracted JSON from markdown code block")
                        return result
                except json.JSONDecodeError:
                    continue

        # Strategy 3: Find the largest valid JSON array using bracket matching
        try:
            result = self._find_largest_json_array(text)
            if result:
                logger.debug("Successfully extracted JSON using bracket matching")
                return result
        except Exception as e:
            logger.debug(f"Bracket matching failed: {e}")

        # Strategy 4: Fallback to improved regex patterns
        regex_patterns = [
            r'\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]',  # Improved nested bracket regex
            r'\[([^\]]*)\]',  # Simple bracket regex as fallback
        ]

        for pattern in regex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    # Ensure the match starts with '['
                    if not match.strip().startswith('['):
                        match = f'[{match}]'
                    result = json.loads(match)
                    if isinstance(result, list):
                        logger.debug("Successfully extracted JSON using improved regex")
                        return result
                except json.JSONDecodeError:
                    continue

        # If all strategies fail, raise an error
        logger.error(f"Could not extract valid JSON array from text: {repr(text[:200])}...")
        raise json.JSONDecodeError("No valid JSON array found", text, 0)

    def _find_largest_json_array(self, text: str) -> Optional[List]:
        """
        Find the largest valid JSON array in text using bracket matching.

        Args:
            text: Text to search for JSON arrays

        Returns:
            The largest valid JSON array found, or None if none found
        """
        candidates = []

        # Find all potential array starts
        for i, char in enumerate(text):
            if char == '[':
                # Try to find the matching closing bracket
                bracket_count = 1
                end_pos = i + 1

                while end_pos < len(text) and bracket_count > 0:
                    if text[end_pos] == '[':
                        bracket_count += 1
                    elif text[end_pos] == ']':
                        bracket_count -= 1
                    end_pos += 1

                if bracket_count == 0:  # Found matching brackets
                    array_text = text[i:end_pos]
                    try:
                        result = json.loads(array_text)
                        if isinstance(result, list):
                            candidates.append(result)
                    except json.JSONDecodeError:
                        continue

        # Return the largest array found
        if candidates:
            return max(candidates, key=len)

        return None

    def get_mismatch_stats(self) -> Dict:
        """
        Get mismatch statistics for reporting.

        Returns:
            Dictionary with mismatch statistics
        """
        return self._mismatch_stats.copy()

    def translate_batch(
        self,
        texts: List[str],
        target_lang: str,
        retry_count: int = 0,
        keys: Optional[List[str]] = None,
        batch_index: Optional[int] = None
    ) -> List[str]:
        """
        Translate a batch of English texts to target language.

        Args:
            texts: List of English definition texts to translate
            target_lang: Target language code (e.g., 'es', 'pt')
            retry_count: Current retry attempt (for internal use)
            keys: Optional list of keys (not used for Grok, kept for compatibility)

        Returns:
            List of translated texts in the same order as input

        Raises:
            ValueError: If translation fails after max retries
        """
        if not texts:
            return []

        # Grok doesn't have a separate batch API like Gemini
        # Process synchronously
        return self._translate_batch_sync(texts, target_lang, retry_count)

    def _translate_batch_sync(
        self,
        texts: List[str],
        target_lang: str,
        retry_count: int = 0
    ) -> List[str]:
        """
        Synchronous batch translation using Grok API.

        Args:
            texts: List of English definition texts to translate
            target_lang: Target language code (e.g., 'es', 'pt')
            retry_count: Current retry attempt

        Returns:
            List of translated texts in the same order as input
        """
        if not texts:
            return []

        self._rate_limit()
        
        response_text = None
        
        try:
            prompt = self._generate_prompt(texts, target_lang)
            
            # Grok API uses /v1/responses endpoint with input array format
            logger.debug(f"Making API call to Grok with model: {self.model_name}")
            logger.debug(f"Prompt length: {len(prompt)} characters")

            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {
                        "role": "system",
                        "content": "You are a helpful translator specializing in biblical Hebrew dictionary definitions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            logger.debug(f"API call completed successfully")

            # Debug the response structure
            logger.debug(f"Response object: {response}")
            logger.debug(f"Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")

            # Check if response has the expected structure
            if not hasattr(response, 'output'):
                logger.error(f"Response missing 'output' attribute: {response}")
                raise ValueError("Invalid response structure from Grok API")

            if response.output is None:
                logger.error("Response.output is None")
                raise ValueError("Response output is None")

            if len(response.output) == 0:
                logger.error("Response.output is empty")
                raise ValueError("Response output is empty")

            output_item = response.output[0]
            logger.debug(f"Output item: {output_item}")
            logger.debug(f"Output item dir: {[attr for attr in dir(output_item) if not attr.startswith('_')]}")

            # Try different ways to access content
            content = None
            if hasattr(output_item, 'content') and output_item.content is not None:
                content_obj = output_item.content
                logger.debug(f"content_obj type: {type(content_obj)}, attrs: {[attr for attr in dir(content_obj) if not attr.startswith('_')]}")

                # Handle case where content is a list of ResponseOutputText objects
                if isinstance(content_obj, list) and len(content_obj) > 0:
                    # Take the first item and extract its text
                    first_item = content_obj[0]
                    if hasattr(first_item, 'text'):
                        content = first_item.text
                    elif hasattr(first_item, 'value'):
                        content = first_item.value
                    elif hasattr(first_item, 'content'):
                        content = first_item.content
                    elif hasattr(first_item, 'data'):
                        content = first_item.data
                    else:
                        content = str(first_item)
                # Handle single ResponseOutputText object
                elif hasattr(content_obj, 'text'):
                    content = content_obj.text
                elif hasattr(content_obj, 'value'):
                    content = content_obj.value
                elif hasattr(content_obj, 'content'):
                    content = content_obj.content
                elif hasattr(content_obj, 'data'):
                    content = content_obj.data
                else:
                    # Try calling the object as a string or accessing its content directly
                    try:
                        content = str(content_obj)
                    except:
                        content = repr(content_obj)
                logger.debug(f"Found content via .content: {repr(content)}")
            elif hasattr(output_item, 'text') and output_item.text is not None:
                content_obj = output_item.text
                logger.debug(f"text_obj type: {type(content_obj)}, attrs: {[attr for attr in dir(content_obj) if not attr.startswith('_')]}")

                # Handle case where text is a list of ResponseOutputText objects
                if isinstance(content_obj, list) and len(content_obj) > 0:
                    # Take the first item and extract its text
                    first_item = content_obj[0]
                    if hasattr(first_item, 'text'):
                        content = first_item.text
                    elif hasattr(first_item, 'value'):
                        content = first_item.value
                    elif hasattr(first_item, 'content'):
                        content = first_item.content
                    elif hasattr(first_item, 'data'):
                        content = first_item.data
                    else:
                        content = str(first_item)
                # Handle single ResponseOutputText object
                elif hasattr(content_obj, 'text'):
                    content = content_obj.text
                elif hasattr(content_obj, 'value'):
                    content = content_obj.value
                elif hasattr(content_obj, 'content'):
                    content = content_obj.content
                elif hasattr(content_obj, 'data'):
                    content = content_obj.data
                else:
                    # Try calling the object as a string or accessing its content directly
                    try:
                        content = str(content_obj)
                    except:
                        content = repr(content_obj)
                logger.debug(f"Found content via .text: {repr(content)}")
            else:
                logger.debug(f"Output item has no direct content, checking summary: {output_item}")

                # Grok sometimes returns reasoning with summary containing the final answer
                if hasattr(output_item, 'summary') and output_item.summary:
                    logger.debug(f"Found summary in output item: {len(output_item.summary)} items")

                    # Look for summary items that might contain JSON
                    for summary_item in output_item.summary:
                        if hasattr(summary_item, 'text'):
                            summary_text_obj = summary_item.text

                            # Handle case where summary text is a list of ResponseOutputText objects
                            if isinstance(summary_text_obj, list) and len(summary_text_obj) > 0:
                                # Take the first item and extract its text
                                first_item = summary_text_obj[0]
                                if hasattr(first_item, 'text'):
                                    summary_text = first_item.text
                                elif hasattr(first_item, 'value'):
                                    summary_text = first_item.value
                                elif hasattr(first_item, 'content'):
                                    summary_text = first_item.content
                                elif hasattr(first_item, 'data'):
                                    summary_text = first_item.data
                                else:
                                    summary_text = str(first_item)
                            # Handle single ResponseOutputText object
                            elif hasattr(summary_text_obj, 'text'):
                                summary_text = summary_text_obj.text
                            elif hasattr(summary_text_obj, 'value'):
                                summary_text = summary_text_obj.value
                            elif hasattr(summary_text_obj, 'content'):
                                summary_text = summary_text_obj.content
                            elif hasattr(summary_text_obj, 'data'):
                                summary_text = summary_text_obj.data
                            else:
                                summary_text = str(summary_text_obj)
                            logger.debug(f"Checking summary text: {summary_text[:200]}...")

                            # Look for JSON array patterns in the summary
                            import re
                            # Look for patterns like ["word"], ["translated"], etc.
                            json_matches = re.findall(r'\["[^"]+"\]', summary_text)
                            logger.debug(f"Found {len(json_matches)} potential JSON arrays in summary")

                            for potential_json in json_matches:
                                logger.debug(f"Testing potential JSON: {potential_json}")
                                try:
                                    # Try to parse it as JSON
                                    parsed = json.loads(potential_json)
                                    if isinstance(parsed, list) and len(parsed) > 0:
                                        content = potential_json
                                        logger.debug(f"Successfully extracted JSON from summary: {content}")
                                        break
                                except json.JSONDecodeError:
                                    logger.debug(f"Could not parse as JSON: {potential_json}")
                                    continue

                            # If no clean JSON found, try broader patterns
                            if not content:
                                # Look for any bracketed content that might contain the answer
                                broad_matches = re.findall(r'\[([^\]]+)\]', summary_text)
                                for match in broad_matches:
                                    # Clean up the match and try to make it valid JSON
                                    cleaned = match.strip()
                                    if ',' in cleaned:
                                        # Multiple items
                                        items = [item.strip().strip('"').strip("'") for item in cleaned.split(',')]
                                        potential_json = json.dumps(items)
                                    else:
                                        # Single item
                                        item = cleaned.strip('"').strip("'")
                                        potential_json = json.dumps([item])

                                    logger.debug(f"Trying cleaned JSON: {potential_json}")
                                    try:
                                        parsed = json.loads(potential_json)
                                        if isinstance(parsed, list) and len(parsed) > 0:
                                            content = potential_json
                                            logger.debug(f"Successfully extracted cleaned JSON: {content}")
                                            break
                                    except json.JSONDecodeError:
                                        continue

                # Try other attributes
                for attr in ['message', 'response', 'result', 'answer']:
                    if hasattr(output_item, attr):
                        possible_content = getattr(output_item, attr)
                        if possible_content is not None:
                            logger.debug(f"Found possible content via .{attr}: {possible_content}")
                            content = possible_content
                            break

            if content is None:
                logger.error(f"Could not extract content from response. Output item: {output_item}")
                logger.error(f"Available attributes: {[attr for attr in dir(output_item) if not attr.startswith('_')]}")
                raise ValueError("Could not extract content from Grok API response")

            # Ensure content is a string before calling strip()
            if isinstance(content, list):
                # If content is already a list, it might be the parsed translations
                translations = content
            else:
                response_text = str(content).strip()
                logger.debug(f"Extracted response text: {repr(response_text)}")

                # Use robust JSON extraction with bracket matching
                translations = self._extract_json_array_robust(response_text)
                logger.debug(f"Successfully extracted JSON array: {len(translations) if isinstance(translations, list) else 'not a list'} items")

            if not isinstance(translations, list):
                raise ValueError("Response is not a JSON array")
            
            # Track batch statistics
            self._mismatch_stats['total_batches'] += 1

            if len(translations) != len(texts):
                self._mismatch_stats['mismatched_batches'] += 1

                # Calculate mismatch details
                expected_count = len(texts)
                actual_count = len(translations)
                mismatch_diff = actual_count - expected_count

                # Track padding/truncation
                if mismatch_diff > 0:
                    self._mismatch_stats['total_truncation'] += mismatch_diff
                elif mismatch_diff < 0:
                    self._mismatch_stats['total_padding'] += abs(mismatch_diff)

                # Track mismatch patterns
                pattern_key = f"{expected_count}->{actual_count}"
                self._mismatch_stats['mismatch_patterns'][pattern_key] = \
                    self._mismatch_stats['mismatch_patterns'].get(pattern_key, 0) + 1

                # Enhanced logging with batch details
                log_msg = f"Translation count mismatch in batch {batch_index or 'unknown'}: expected {expected_count}, got {actual_count}"

                if batch_index is not None:
                    log_msg += f" (batch {batch_index})"

                # Log sample texts for debugging (first 3)
                sample_count = min(3, len(texts), len(translations))
                if sample_count > 0:
                    log_msg += f"\nSample translations (first {sample_count}):"
                    for i in range(sample_count):
                        original = texts[i][:50] + "..." if len(texts[i]) > 50 else texts[i]
                        translated = translations[i][:50] + "..." if i < len(translations) and len(translations[i]) > 50 else translations[i] if i < len(translations) else "[MISSING]"
                        log_msg += f"\n  {i+1}. '{original}' -> '{translated}'"

                # Log action taken
                if mismatch_diff > 0:
                    log_msg += f"\nAction: Truncated {mismatch_diff} extra translations"
                elif mismatch_diff < 0:
                    log_msg += f"\nAction: Padded with {abs(mismatch_diff)} empty strings"

                logger.warning(log_msg)
            
            # Ensure we have the same number of translations as inputs
            # Pad with empty strings if needed
            while len(translations) < len(texts):
                translations.append("")
            
            return translations[:len(texts)]
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            if response_text:
                logger.debug(f"Response text: {response_text[:500]}")
            
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_BASE ** retry_count
                logger.info(f"Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(wait_time)
                return self.translate_batch(texts, target_lang, retry_count + 1)
            else:
                raise ValueError(
                    f"Failed to parse translation response after {MAX_RETRIES} retries: {e}"
                )
        
        except Exception as e:
            error_str = str(e)
            logger.error(f"Translation error: {error_str}")
            
            # Check if it's a quota/rate limit error (429)
            wait_time = None
            
            # Try to extract retry_delay from error message
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                # Look for retry delay in error message
                retry_match = re.search(r'retry.*?(\d+(?:\.\d+)?)', error_str, re.IGNORECASE)
                if retry_match:
                    wait_time = float(retry_match.group(1))
                    logger.info(f"Rate limit detected. Waiting {wait_time:.1f} seconds as suggested by API...")
                else:
                    # Default wait time for rate limits
                    wait_time = 60.0
                    logger.info(f"Rate limit detected. Waiting {wait_time:.1f} seconds...")
            
            if retry_count < MAX_RETRIES:
                if wait_time is None:
                    wait_time = RETRY_BACKOFF_BASE ** retry_count
                logger.info(f"Retrying in {wait_time:.1f} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(wait_time)
                return self._translate_batch_sync(texts, target_lang, retry_count + 1)
            else:
                raise ValueError(
                    f"Translation failed after {MAX_RETRIES} retries: {e}"
                )

