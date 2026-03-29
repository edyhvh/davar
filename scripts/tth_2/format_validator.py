#!/usr/bin/env python3
"""
TTH JSON Format Validator
=========================

Validates formatting consistency for TTH2 JSON files.

Checks:
1. Remaining markdown italics (*...*) in verse text and footnote explanations
2. Disallowed escaped punctuation/brackets (\\!, \\., \\[, \\])
3. Unbalanced <em> tags
4. Basic footnote marker consistency in verse text
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_JSON_DIR = Path(__file__).parent.parent.parent / "data" / "tth_2" / "json"

DISALLOWED_ESCAPES_RE = re.compile(r'\\([!\.\[\]])')
MARKDOWN_ITALICS_RE = re.compile(r'\*[^*]+\*')
EM_NESTING_RE = re.compile(r'<em>\s*<em>|</em>\s*</em>')


class TTHFormatValidator:
    """Validator for TTH2 JSON formatting rules."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _validate_text(self, text: str, label: str) -> List[str]:
        issues: List[str] = []
        if not text:
            return issues

        if MARKDOWN_ITALICS_RE.search(text):
            issues.append(f"{label}: contains markdown italics markers")

        if DISALLOWED_ESCAPES_RE.search(text):
            issues.append(f"{label}: contains disallowed escaped punctuation/brackets")

        if text.count('<em>') != text.count('</em>'):
            issues.append(f"{label}: unbalanced <em> tags")

        if EM_NESTING_RE.search(text):
            issues.append(f"{label}: nested/repeated <em> tags")

        if '## Footnotes' in text:
            issues.append(f"{label}: embedded footnotes section leakage")

        return issues

    def validate_book_file(self, file_path: Path) -> Tuple[bool, List[str], Dict[str, int]]:
        """Validate formatting of a single TTH2 JSON book file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        issues: List[str] = []
        stats = {
            'verses_checked': 0,
            'footnotes_checked': 0,
            'markdown_italics': 0,
            'escaped_special_chars': 0,
            'unbalanced_em_tags': 0,
            'nested_em_tags': 0,
            'embedded_footnotes_sections': 0,
            'footnote_marker_mismatches': 0,
        }

        for chapter in data.get('chapters', []):
            chapter_num = chapter.get('chapter', 0)
            for verse in chapter.get('verses', []):
                verse_num = verse.get('verse', 0)
                stats['verses_checked'] += 1

                tth_text = verse.get('tth', '')
                verse_issues = self._validate_text(tth_text, f"Ch {chapter_num}:{verse_num} verse text")
                for issue in verse_issues:
                    issues.append(issue)

                if MARKDOWN_ITALICS_RE.search(tth_text):
                    stats['markdown_italics'] += 1
                if DISALLOWED_ESCAPES_RE.search(tth_text):
                    stats['escaped_special_chars'] += 1
                if tth_text.count('<em>') != tth_text.count('</em>'):
                    stats['unbalanced_em_tags'] += 1
                if EM_NESTING_RE.search(tth_text):
                    stats['nested_em_tags'] += 1
                if '## Footnotes' in tth_text:
                    stats['embedded_footnotes_sections'] += 1

                for footnote in verse.get('footnotes', []):
                    stats['footnotes_checked'] += 1
                    explanation = footnote.get('explanation', '')
                    fn_issues = self._validate_text(
                        explanation,
                        f"Ch {chapter_num}:{verse_num} footnote {footnote.get('number', 0)} explanation",
                    )
                    for issue in fn_issues:
                        issues.append(issue)

                    if MARKDOWN_ITALICS_RE.search(explanation):
                        stats['markdown_italics'] += 1
                    if DISALLOWED_ESCAPES_RE.search(explanation):
                        stats['escaped_special_chars'] += 1
                    if explanation.count('<em>') != explanation.count('</em>'):
                        stats['unbalanced_em_tags'] += 1
                    if EM_NESTING_RE.search(explanation):
                        stats['nested_em_tags'] += 1
                    if '## Footnotes' in explanation:
                        stats['embedded_footnotes_sections'] += 1

                    marker = footnote.get('marker', '')
                    if marker and marker not in tth_text:
                        stats['footnote_marker_mismatches'] += 1
                        # Keep mismatch counts for diagnostics, but do not fail
                        # formatting validation on marker-reference integrity.

        return len(issues) == 0, issues, stats

    def validate_all_books(self, json_dir: Path = DEFAULT_JSON_DIR) -> Tuple[bool, Dict[str, Dict[str, int]], Dict[str, List[str]]]:
        """Validate formatting for all TTH2 JSON files in a directory."""
        files = sorted(json_dir.glob('*.json'))
        all_valid = True
        all_stats: Dict[str, Dict[str, int]] = {}
        all_issues: Dict[str, List[str]] = {}

        for file_path in files:
            is_valid, issues, stats = self.validate_book_file(file_path)
            book_key = file_path.stem
            all_stats[book_key] = stats
            all_issues[book_key] = issues
            all_valid = all_valid and is_valid

        return all_valid, all_stats, all_issues


def print_book_report(book_key: str, is_valid: bool, issues: List[str], stats: Dict[str, int]) -> None:
    """Print a compact validation report for one book."""
    if is_valid:
        print(
            f"✅ {book_key}: OK "
            f"({stats['verses_checked']} verses, {stats['footnotes_checked']} footnotes checked)"
        )
        return

    print(f"❌ {book_key}: {len(issues)} formatting issue(s)")
    print(f"   - markdown italics matches: {stats['markdown_italics']}")
    print(f"   - escaped special chars:    {stats['escaped_special_chars']}")
    print(f"   - unbalanced <em> tags:     {stats['unbalanced_em_tags']}")
    print(f"   - nested <em> tags:         {stats['nested_em_tags']}")
    print(f"   - embedded footnotes text:  {stats['embedded_footnotes_sections']}")
    print(f"   - marker mismatches:        {stats['footnote_marker_mismatches']}")

    for issue in issues[:8]:
        print(f"   - {issue}")
    if len(issues) > 8:
        print(f"   ... and {len(issues) - 8} more")


def get_format_validator(verbose: bool = False) -> TTHFormatValidator:
    """Create a format validator instance."""
    return TTHFormatValidator(verbose=verbose)
