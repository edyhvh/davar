#!/usr/bin/env python3
"""
TTH JSON Post-Processor
=======================

Post-processes TTH2 JSON files to:
1. Convert markdown italics (*word*) to HTML <em> tags
2. Fix broken italic patterns from DOCX conversion
3. Remove escaped parentheses and other artifacts
4. Clean soft hyphens

For use with React Native apps using react-native-render-html.

Author: Davar Project
"""

import json
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Default paths
DEFAULT_JSON_DIR = Path(__file__).parent.parent.parent / \
    "data" / "tth_2" / "json"

# Singleton instances
_postprocessor_instances = {}


def get_postprocessor(verbose: bool = False):
    """Get the singleton TTHJsonPostProcessor instance."""
    key = str(verbose)
    if key not in _postprocessor_instances:
        _postprocessor_instances[key] = TTHJsonPostProcessor(verbose=verbose)
    return _postprocessor_instances[key]


class TTHJsonPostProcessor:
    """
    Post-processes TTH2 JSON files to convert markdown to HTML
    and fix formatting issues.
    """

    BLOCKED_SUBTITLE_PHRASES = (
        'el que podía',
        'serán los de',
        'fiesta de las',
        'no la verán',
        'para que esté',
        'de la casa',
    )

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.stats = {
            'soft_hyphens': 0,
            'underscore_artifacts': 0,
            'escaped_parens': 0,
            'escaped_special_chars': 0,
            'embedded_footnotes_removed': 0,
            'broken_italics': 0,
            'italics_converted': 0,
            'em_spacing_fixed': 0,
            'subtitle_segments_extracted': 0,
            'subtitle_verses_created': 0,
            'subtitle_segments_skipped_wordcount': 0,
            'subtitle_segments_skipped_lowercase': 0,
            'subtitle_segments_skipped_phrase': 0,
            'subtitle_invalid_removed': 0,
            'verses_processed': 0,
            'files_processed': 0,
        }

    def starts_with_lowercase_latin(self, content: str) -> bool:
        """Return True when the first Latin letter in content is lowercase."""
        first_letter = re.search(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]', content)
        if not first_letter:
            return False
        letter = first_letter.group(0)
        return letter.isalpha() and letter == letter.lower() and letter != letter.upper()

    def starts_with_blocked_subtitle_phrase(self, content: str) -> bool:
        """Return True when content starts with a known in-verse phrase."""
        normalized = content.strip().lower()
        return any(normalized.startswith(phrase) for phrase in self.BLOCKED_SUBTITLE_PHRASES)

    def is_valid_subtitle(self, content: str) -> bool:
        """Keep only clear heading-like subtitles and drop known false positives."""
        cleaned = content.strip()
        if not cleaned:
            return False
        if self.starts_with_lowercase_latin(cleaned):
            return False
        if self.starts_with_blocked_subtitle_phrase(cleaned):
            return False
        return True

    def count_words(self, text: str) -> int:
        """Count words in a subtitle candidate, trimming edge punctuation."""
        if not text:
            return 0

        tokens = re.split(r'\s+', text.strip())
        cleaned_tokens = []
        strip_chars = '.,;:!?"' + "'" + '“”‘’()[]{}'
        for token in tokens:
            cleaned = token.strip(strip_chars)
            if cleaned:
                cleaned_tokens.append(cleaned)

        return len(cleaned_tokens)

    def extract_subtitle_from_italics(self, text: str) -> Tuple[str, str, int]:
        """
        Extract trailing italicized heading-like segments into subtitle.

        This is intentionally conservative: only trailing <em>...</em> spans are
        considered to avoid moving in-verse explanatory italics.

        Returns:
            Tuple of (updated_text, subtitle, extracted_segment_count)
        """
        if not text:
            return text, '', 0

        result = text.rstrip()
        subtitle_parts: List[str] = []
        extracted_segments = 0

        while True:
            match = re.search(
                r'^(.*?)(?:\s*)<em>([^<]+)</em>\s*$', result, flags=re.DOTALL)
            if not match:
                break

            prefix = match.group(1).rstrip()
            content = match.group(2).strip()
            word_count = self.count_words(content)

            if word_count < 3:
                self.stats['subtitle_segments_skipped_wordcount'] += 1
                break

            if self.starts_with_lowercase_latin(content):
                self.stats['subtitle_segments_skipped_lowercase'] += 1
                break

            if self.starts_with_blocked_subtitle_phrase(content):
                self.stats['subtitle_segments_skipped_phrase'] += 1
                break

            subtitle_parts.insert(0, content)
            result = prefix
            extracted_segments += 1

        if extracted_segments == 0:
            return text, '', 0

        result = re.sub(r'\s{2,}', ' ', result)
        result = re.sub(r'\s+([,.;:!?])', r'\1', result)
        result = result.strip()

        subtitle = ' '.join(subtitle_parts).strip()
        return result, subtitle, extracted_segments

    def remove_soft_hyphens(self, text: str) -> str:
        """
        Remove soft hyphen characters (U+00AD).
        These are invisible word-break hints from DOCX conversion.
        """
        count = text.count('\u00AD')
        self.stats['soft_hyphens'] += count
        return text.replace('\u00AD', '')

    def fix_underscore_artifacts(self, text: str) -> str:
        """
        Remove underscore artifacts like __* *__ patterns.
        These are conversion errors from DOCX.
        """
        # Pattern: __* *__ or similar combinations
        patterns = [
            (r'__\*\s*\*__', ' '),           # __* *__ → space
            (r'\*__\*\s*\*__', '*'),          # *__* *__ → single asterisk
            (r'__\*\s*\*', ' '),              # __* * → space
            (r'\*\s*\*__', ' '),              # * *__ → space
        ]

        result = text
        for pattern, replacement in patterns:
            matches = len(re.findall(pattern, result))
            self.stats['underscore_artifacts'] += matches
            result = re.sub(pattern, replacement, result)

        return result

    def fix_empty_italic_gaps(self, text: str) -> str:
        """
        Remove artifact markers like '* *' that appear as spacing placeholders
        between words and footnote markers after conversion.
        """
        matches = re.findall(r'\*\s+\*', text)
        self.stats['broken_italics'] += len(matches)
        return re.sub(r'\*\s+\*', ' ', text)

    def fix_escaped_parentheses(self, text: str) -> str:
        """
        Convert escaped parentheses \\( and \\) to regular ( and ).
        These appear in literal/alternative notes like (Lit.: ...) or (O, ...).
        """
        # Count before fixing
        count = text.count('\\(') + text.count('\\)')
        self.stats['escaped_parens'] += count

        # Replace escaped parens with regular ones
        result = text.replace('\\(', '(').replace('\\)', ')')
        return result

    def fix_escaped_special_chars(self, text: str) -> str:
        """
        Remove unnecessary escaping for punctuation/brackets that should render
        as literal characters in TTH JSON text.

        Examples:
        - \\! -> !
        - \\. -> .
        - \\[ -> [
        - \\] -> ]
        """
        pattern = r'\\([!\.\[\]\*])'
        matches = re.findall(pattern, text)
        self.stats['escaped_special_chars'] += len(matches)
        return re.sub(pattern, r'\1', text)

    def normalize_double_asterisk_markup(self, text: str) -> str:
        """
        Remove leftover markdown bold wrappers (**...**) while preserving content.
        This prevents malformed sequences from interacting with italic conversion.
        """
        result = text
        matches = re.findall(r'\*\*([^*]+?)\*\*', result)
        self.stats['broken_italics'] += len(matches)
        return re.sub(r'\*\*([^*]+?)\*\*', r' \1 ', result)

    def normalize_broken_italics(self, text: str) -> str:
        """
        Fix broken italic patterns before converting to <em>.

        Patterns to fix:
        - *word * (space before closing) → *word*
        - * word* (space after opening) → *word*
        - word* *next (split markers) → word *next* or context-dependent
        """
        result = text

        # Pattern 1: *word * → *word* (trailing space inside)
        # Match: asterisk, word chars, space, asterisk, then non-asterisk or end
        pattern1 = r'\*([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF][A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF\-\']*)\s+\*(?=[^*]|$)'
        matches1 = len(re.findall(pattern1, result))
        self.stats['broken_italics'] += matches1
        result = re.sub(pattern1, r'*\1* ', result)

        # Pattern 2: * word* → *word* (leading space inside)
        # Match: space or start of text, asterisk, space(s), word, asterisk
        # Use simpler pattern without variable-width lookbehind
        pattern2 = r'(\s)\*\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF][A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF\-\']*)\*'
        matches2 = len(re.findall(pattern2, result))
        self.stats['broken_italics'] += matches2
        result = re.sub(pattern2, r'\1*\2*', result)

        # Also handle at start of string
        pattern2b = r'^\*\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF][A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF\-\']*)\*'
        matches2b = len(re.findall(pattern2b, result))
        self.stats['broken_italics'] += matches2b
        result = re.sub(pattern2b, r'*\1*', result)

        # Pattern 3: word* *next → handle split markers
        # This is trickier - often means the second word should be italic
        # Example: "bien* *todas" → "bien *todas*" (assuming todas should be italic)
        pattern3 = r'([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF]+)\*\s+\*([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF])'
        matches3 = len(re.findall(pattern3, result))
        self.stats['broken_italics'] += matches3
        # Keep the first word normal, make the second italic
        result = re.sub(pattern3, r'\1 *\2', result)

        # Pattern 4: punctuation* *word (comma, period before split)
        # Example: "eso,* *pobres" → "eso, *pobres*"
        pattern4 = r'([,\.;:])\*\s+\*([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF])'
        matches4 = len(re.findall(pattern4, result))
        self.stats['broken_italics'] += matches4
        result = re.sub(pattern4, r'\1 *\2', result)

        # Clean up any double spaces introduced
        result = re.sub(r'  +', ' ', result)

        return result

    def convert_italics_to_em(self, text: str) -> str:
        """
        Convert markdown italics *word* to HTML <em>word</em>.

        Handles:
        - Single words: *word* → <em>word</em>
        - Multi-word: *word1 word2* → <em>word1 word2</em>
        - Nested punctuation: *word,* → <em>word,</em>
        """
        # Pattern for italic content between asterisks
        # Match: * followed by content (not starting with space), followed by *
        # Content can include: letters, numbers, spaces, punctuation, Hebrew chars
        pattern = r'\*([^*]+?)\*'

        def replace_italic(match):
            content = match.group(1).strip()
            if content:  # Don't convert empty italics
                self.stats['italics_converted'] += 1
                return f'<em>{content}</em>'
            return match.group(0)

        result = re.sub(pattern, replace_italic, text)
        return result

    def convert_single_word_italics(self, text: str) -> str:
        """
        Convert single-word italics *word* to <em>word</em> first.
        This handles cases like escribírte*las* correctly.
        """
        # Match *word* where word is a single word (no spaces)
        # This catches: *word*, *word*, *word*,  etc.
        pattern = r'\*([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF][A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF\-\']*)\*'

        def replace_single(match):
            word = match.group(1)
            self.stats['italics_converted'] += 1
            return f'<em>{word}</em>'

        return re.sub(pattern, replace_single, text)

    def fix_orphan_asterisks(self, text: str) -> str:
        """
        Fix orphan asterisks that remain after single-word conversion.
        Patterns like: word* *next → word next (remove orphan markers)
        """
        result = text

        # Pattern: word* *word (orphan close then orphan open)
        # These are markers that didn't have matching pairs
        pattern1 = r'([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF,\.;:]+)\*\s+\*([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF])'
        matches1 = len(re.findall(pattern1, result))
        self.stats['broken_italics'] += matches1
        result = re.sub(pattern1, r'\1 \2', result)

        # Pattern: remaining orphan asterisks at word boundaries
        # *word (orphan open) - if word is followed by non-asterisk
        pattern2 = r'(?<![A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF])\*([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF][A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF\-\'\s,\.;:]*?)(?=\s|$|[,\.;:\"\'])'
        # This is tricky - we need to be careful not to remove legitimate patterns

        # For now, just clean up the common case: word* at end or before space
        # Only if not followed by matching close

        return result

    def strip_asterisks_around_em(self, text: str) -> str:
        """
        Remove leftover markdown asterisks wrapping or touching existing <em>
        tags, e.g. *<em>...</em>* -> <em>...</em>.
        """
        result = text

        # Full wrapper around one or more <em>...</em> segments.
        result = re.sub(r'\*(\s*(?:<em>[^<]*</em>\s*)+)\*', r'\1', result)

        # Partial wrappers touching opening/closing <em> tags.
        result = re.sub(r'\*(?=\s*<em>)', '', result)
        result = re.sub(r'(?<=</em>)\*', '', result)

        return result

    def remove_orphan_asterisks(self, text: str) -> str:
        """
        Remove leftover orphan markdown asterisks after conversion.
        By this stage paired italics should already be converted to <em> tags,
        so remaining stars are usually conversion artifacts.
        """
        result = text

        # Orphan star before punctuation/space/end.
        result = re.sub(r'(?<=\S)\*(?=\s|$|[\.,;:!?])', '', result)

        # Orphan star after whitespace or at string start before plain text.
        # Use a captured prefix instead of variable-width look-behind for
        # Python regex compatibility.
        result = re.sub(r'(^|\s)\*(?=\S)', r'\1', result)

        return result

    def fix_em_spacing(self, text: str) -> str:
        """
        Ensure proper spacing around <em> tags.

        This handles cases where <em> tags are joined to adjacent words
        without proper spacing, like "escribírte<em>las</em>" → "escribírte <em>las</em>"

        Rules:
        - Add space before <em> if preceded by letter/Hebrew without space
        - Add space after </em> if followed by letter/Hebrew without space
        - Don't add space if already there or followed by punctuation
        """
        result = text

        # Count fixes for statistics
        fixes_before = result.count('<em>') + result.count('</em>')

        # Pattern 1: Add space before <em> if preceded by word character without space
        # Match: word character immediately followed by <em>
        pattern1 = r'([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF])(<em>)'
        result = re.sub(pattern1, r'\1 \2', result)

        # Pattern 2: Add space after </em> if followed by word character without space
        # Match: </em> immediately followed by word character (but not punctuation)
        pattern2 = r'(</em>)([A-Za-zÁÉÍÓÚáéíóúñÑ\u0590-\u05FF])'
        result = re.sub(pattern2, r'\1 \2', result)

        # Count fixes made
        fixes_after = result.count('<em>') + result.count('</em>')
        self.stats['em_spacing_fixed'] += (fixes_after - fixes_before)

        # Clean up any double spaces that might have been created
        result = re.sub(r'  +', ' ', result)

        return result

    def flatten_nested_em_tags(self, text: str) -> str:
        """Flatten accidental nested <em> tags into a single emphasis span."""
        result = text
        nested_pattern = re.compile(r'<em>([^<]*)<em>([^<]*)</em>([^<]*)</em>')
        while nested_pattern.search(result):
            result = nested_pattern.sub(r'<em>\1\2\3</em>', result)
        return result

    def strip_embedded_footnotes_section(self, text: str) -> str:
        """
        Remove leaked markdown footnotes sections accidentally appended to verse
        text during conversion (e.g., "## Footnotes ...").
        """
        marker = '## Footnotes'
        idx = text.find(marker)
        if idx == -1:
            return text

        # If the marker is wrapped by runaway emphasis tags, trim from the
        # nearest doubled <em> start right before the marker.
        cut_idx = idx
        runaway_em_idx = text.rfind('<em><em>', 0, idx)
        if runaway_em_idx != -1 and (idx - runaway_em_idx) < 200:
            cut_idx = runaway_em_idx

        self.stats['embedded_footnotes_removed'] += 1
        return text[:cut_idx].rstrip()

    def strip_inline_footnote_blob(self, text: str) -> str:
        """
        Remove leaked inline numbered footnote apparatus from verse text.

        Corrupted verses can contain long sequences like:
        "... 1. ¹: ... 2. ²: ..."

        This trims from the first apparatus marker when the verse is abnormally
        long, keeping normal verse content intact.
        """
        if not text:
            return text

        if len(text) < 500:
            return text

        marker_match = re.search(r'\s\d+\.\s+[⁰¹²³⁴⁵⁶⁷⁸⁹]+:', text)
        if not marker_match:
            return text

        # Require repeated inline markers to avoid clipping legitimate numbering.
        marker_count = len(re.findall(r'\s\d+\.\s+[⁰¹²³⁴⁵⁶⁷⁸⁹]+:', text))
        if marker_count < 2:
            return text

        self.stats['embedded_footnotes_removed'] += 1
        return text[:marker_match.start()].rstrip()

    def rebalance_em_tags(self, text: str) -> str:
        """Drop dangling <em> or </em> tags left by malformed source markup."""
        result = text
        while result.count('<em>') > result.count('</em>'):
            pos = result.rfind('<em>')
            if pos == -1:
                break
            result = result[:pos] + result[pos + 4:]

        while result.count('</em>') > result.count('<em>'):
            pos = result.find('</em>')
            if pos == -1:
                break
            result = result[:pos] + result[pos + 5:]

        return result

    def process_text(self, text: str) -> str:
        """
        Apply all processing steps to a text string.
        Order matters!
        """
        if not text or not text.strip():
            return text

        result = text

        # Step 1: Remove soft hyphens (clean raw text first)
        result = self.remove_soft_hyphens(result)

        # Step 2: Fix underscore artifacts
        result = self.fix_underscore_artifacts(result)

        # Step 3: Remove empty markdown spacer artifacts (* *)
        result = self.fix_empty_italic_gaps(result)

        # Step 4: Fix escaped parentheses
        result = self.fix_escaped_parentheses(result)

        # Step 5: Remove unnecessary escaped punctuation/brackets
        result = self.fix_escaped_special_chars(result)

        # Step 6: Normalize leftover markdown bold wrappers
        result = self.normalize_double_asterisk_markup(result)

        # Step 7: Convert single-word italics FIRST (*word* → <em>word</em>)
        # This handles cases like escribírte*las* correctly
        result = self.convert_single_word_italics(result)

        # Step 8: Fix orphan asterisks (word* *next patterns)
        result = self.fix_orphan_asterisks(result)

        # Step 9: Strip stray asterisks around existing <em> tags
        result = self.strip_asterisks_around_em(result)

        # Step 10: Normalize any remaining broken italic patterns
        result = self.normalize_broken_italics(result)

        # Step 11: Convert any remaining *...* to <em>...</em>
        result = self.convert_italics_to_em(result)

        # Step 12: Remove orphan markdown stars left after conversion
        result = self.remove_orphan_asterisks(result)

        # Step 13: Fix spacing around <em> tags
        result = self.fix_em_spacing(result)

        # Step 14: Flatten accidental nested <em> tags
        result = self.flatten_nested_em_tags(result)

        # Step 15: Clean up any remaining issues
        result = re.sub(r'  +', ' ', result)  # Double spaces
        result = result.strip()

        return result

    def process_verse(self, verse: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single verse entry."""
        self.stats['verses_processed'] += 1

        existing_subtitle = verse.get('subtitle', '').strip()
        if existing_subtitle and not self.is_valid_subtitle(existing_subtitle):
            del verse['subtitle']
            self.stats['subtitle_invalid_removed'] += 1

        # Process the main TTH text
        if 'tth' in verse and verse['tth']:
            verse['tth'] = self.process_text(verse['tth'])
            verse['tth'] = self.strip_inline_footnote_blob(verse['tth'])
            verse['tth'] = self.strip_embedded_footnotes_section(verse['tth'])
            verse['tth'] = self.rebalance_em_tags(verse['tth'])
            verse['tth'], extracted_subtitle, extracted_count = self.extract_subtitle_from_italics(
                verse['tth'])

            if extracted_count > 0 and extracted_subtitle:
                self.stats['subtitle_segments_extracted'] += extracted_count
                self.stats['subtitle_verses_created'] += 1

                existing_subtitle = verse.get('subtitle', '').strip()
                if existing_subtitle and self.is_valid_subtitle(existing_subtitle):
                    verse['subtitle'] = f"{existing_subtitle} {extracted_subtitle}".strip(
                    )
                else:
                    verse['subtitle'] = extracted_subtitle

        # Process footnote explanations (they may contain italics too)
        if 'footnotes' in verse:
            for footnote in verse['footnotes']:
                if 'explanation' in footnote and footnote['explanation']:
                    footnote['explanation'] = self.process_text(
                        footnote['explanation'])
                    footnote['explanation'] = self.rebalance_em_tags(
                        footnote['explanation'])

        return verse

    def process_json_file(self, file_path: Path, dry_run: bool = False, backup: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        Process a single JSON file.

        Args:
            file_path: Path to the JSON file
            dry_run: If True, don't write changes
            backup: If True, create backup before modifying

        Returns:
            Tuple of (success, stats_for_this_file)
        """
        try:
            # Load the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Track stats for this file
            file_stats_before = dict(self.stats)

            # Process all verses in all chapters
            if 'chapters' in data:
                for chapter in data['chapters']:
                    if 'verses' in chapter:
                        for i, verse in enumerate(chapter['verses']):
                            chapter['verses'][i] = self.process_verse(verse)

            # Calculate changes for this file
            file_stats = {
                key: self.stats[key] - file_stats_before[key]
                for key in self.stats
            }

            self.stats['files_processed'] += 1

            if not dry_run:
                # Create backup if requested
                if backup:
                    backup_path = file_path.with_suffix('.json.bak')
                    shutil.copy2(file_path, backup_path)

                # Write the modified JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            return True, file_stats

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False, {}

    def process_all_files(self, json_dir: Path, dry_run: bool = False, backup: bool = False) -> bool:
        """
        Process all JSON files in the directory.
        """
        json_files = sorted(json_dir.glob('*.json'))

        if not json_files:
            print(f"No JSON files found in {json_dir}")
            return False

        print(
            f"{'[DRY RUN] ' if dry_run else ''}Processing {len(json_files)} JSON files...")
        print("=" * 60)

        for file_path in json_files:
            book_name = file_path.stem
            success, file_stats = self.process_json_file(
                file_path, dry_run, backup)

            if success:
                changes = sum(v for k, v in file_stats.items() if k !=
                              'verses_processed' and k != 'files_processed')
                if changes > 0 or self.verbose:
                    print(
                        f"  ✓ {book_name}: {file_stats['verses_processed']} verses, {changes} fixes")
            else:
                print(f"  ✗ {book_name}: FAILED")

        print("=" * 60)
        self.print_summary(dry_run)

        return True

    def print_summary(self, dry_run: bool = False):
        """Print processing summary."""
        prefix = "[DRY RUN] " if dry_run else ""
        print(f"\n{prefix}Processing Summary:")
        print(f"  Files processed:      {self.stats['files_processed']}")
        print(f"  Verses processed:     {self.stats['verses_processed']}")
        print(f"  Soft hyphens removed: {self.stats['soft_hyphens']}")
        print(f"  Escaped parens fixed: {self.stats['escaped_parens']}")
        print(f"  Escaped chars fixed:  {self.stats['escaped_special_chars']}")
        print(
            f"  Footnote leaks fixed: {self.stats['embedded_footnotes_removed']}")
        print(f"  Broken italics fixed: {self.stats['broken_italics']}")
        print(f"  Italics → <em>:       {self.stats['italics_converted']}")
        print(f"  <em> spacing fixed:   {self.stats['em_spacing_fixed']}")
        print(
            f"  Subtitle segments:    {self.stats['subtitle_segments_extracted']}")
        print(
            f"  Subtitle verses:      {self.stats['subtitle_verses_created']}")
        print(
            f"  Subtitle skip (<3w):  {self.stats['subtitle_segments_skipped_wordcount']}")
        print(
            f"  Subtitle skip (lc):   {self.stats['subtitle_segments_skipped_lowercase']}")
        print(
            f"  Subtitle skip (phr):  {self.stats['subtitle_segments_skipped_phrase']}")
        print(
            f"  Invalid subtitles:    {self.stats['subtitle_invalid_removed']}")
        print(f"  Underscore artifacts: {self.stats['underscore_artifacts']}")


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Post-process TTH2 JSON files to convert italics to <em> tags'
    )
    parser.add_argument(
        'target',
        help='Book name (e.g., "lukas") or "all" for all books'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without modifying files'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create .bak backup files before modifying'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output for all files'
    )
    parser.add_argument(
        '--json-dir',
        type=Path,
        default=DEFAULT_JSON_DIR,
        help=f'Path to JSON directory (default: {DEFAULT_JSON_DIR})'
    )

    args = parser.parse_args()

    processor = TTHJsonPostProcessor(verbose=args.verbose)

    if args.target.lower() == 'all':
        success = processor.process_all_files(
            args.json_dir,
            dry_run=args.dry_run,
            backup=args.backup
        )
    else:
        # Process single book
        file_path = args.json_dir / f"{args.target}.json"
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

        print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing {args.target}...")
        success, file_stats = processor.process_json_file(
            file_path,
            dry_run=args.dry_run,
            backup=args.backup
        )
        processor.print_summary(args.dry_run)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
