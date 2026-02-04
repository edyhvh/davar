#!/usr/bin/env python3
"""Re-translate the 10 definitions that got empty strings during batch translation."""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.dict.translation.translator import GrokTranslator


def fix_empty_translations():
    """Re-translate definitions that have empty Spanish translations."""
    
    print('🔧 Fixing empty Spanish translations...\n')
    
    # Load the list of empty translations
    empty_list_path = Path('data/dict/empty_translations.json')
    if not empty_list_path.exists():
        print('❌ No empty_translations.json found. Run check_empty_translations.py first.')
        return
    
    with open(empty_list_path) as f:
        empty_data = json.load(f)
    
    empty_words = empty_data.get('words', [])
    
    if not empty_words:
        print('✅ No empty translations to fix!')
        return
    
    print(f'📋 Found {len(empty_words)} definitions to re-translate\n')
    
    # Load words.json
    words_path = Path('data/dict/lexicon/words.json')
    with open(words_path) as f:
        words = json.load(f)
    
    # Initialize translator
    translator = GrokTranslator()
    
    # Collect texts to translate
    to_translate = []
    for strong, idx, text_en in empty_words:
        to_translate.append(text_en)
        print(f'   {strong} def[{idx}]: "{text_en[:60]}"')
    
    print(f'\n🌐 Translating {len(to_translate)} definitions to Spanish...')
    
    # Translate all at once (small batch)
    translations = translator.translate_batch(to_translate, 'es')
    
    print(f'✅ Received {len(translations)} translations\n')
    
    # Update words.json
    updated_count = 0
    for i, (strong, idx, text_en) in enumerate(empty_words):
        if i < len(translations) and translations[i]:
            words[strong]['definitions'][idx]['text_es'] = translations[i]
            print(f'   ✓ {strong} def[{idx}]: "{translations[i]}"')
            updated_count += 1
        else:
            print(f'   ✗ {strong} def[{idx}]: Still empty!')
    
    # Save updated words.json
    with open(words_path, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 Updated {updated_count}/{len(empty_words)} translations')
    print(f'📁 Saved to: {words_path}')
    
    # Clean up empty_translations.json
    if updated_count == len(empty_words):
        empty_list_path.unlink()
        print(f'🗑️  Removed: {empty_list_path}')
        print('\n✅ All empty translations fixed!')
    else:
        print(f'\n⚠️  {len(empty_words) - updated_count} translations still empty')


if __name__ == '__main__':
    fix_empty_translations()
