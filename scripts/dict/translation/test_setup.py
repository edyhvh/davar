#!/usr/bin/env python3
"""
Simple test script to validate translation module setup.

Tests configuration, imports, and basic functionality without making API calls.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from scripts.dict.translation import config
        print("✓ config module imported")
        
        from scripts.dict.translation import translator
        print("✓ translator module imported")
        
        from scripts.dict.translation import processor
        print("✓ processor module imported")
        
        from scripts.dict.translation import main
        print("✓ main module imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration."""
    print("\nTesting configuration...")
    try:
        from scripts.dict.translation.config import (
            validate_language,
            get_language_name,
            validate_api_key,
            SUPPORTED_LANGUAGES,
        )
        
        # Test language validation
        assert validate_language('es') == True
        assert validate_language('pt') == True
        assert validate_language('invalid') == False
        print("✓ Language validation works")
        
        # Test language name
        assert get_language_name('es') == 'Spanish'
        assert get_language_name('pt') == 'Portuguese'
        print("✓ Language name lookup works")
        
        # Test API key (may be False if not set)
        api_key_valid = validate_api_key()
        if api_key_valid:
            print("✓ API key is configured")
        else:
            print("⚠ API key not found (set GEMINI_API_KEY in .env)")
        
        print(f"✓ Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_processor_structure():
    """Test processor can be initialized (without API calls)."""
    print("\nTesting processor structure...")
    try:
        from scripts.dict.translation.processor import LexiconProcessor
        
        # This will fail if API key not set, which is expected
        try:
            processor = LexiconProcessor(target_lang='es', batch_size=10)
            print("✓ Processor initialized successfully")
            return True
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                print("⚠ Processor requires API key (expected)")
                print("  Set GEMINI_API_KEY in .env file to use translation")
                return True
            else:
                raise
    except Exception as e:
        print(f"✗ Processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Translation Module Setup Test")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Processor", test_processor_structure()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Module is ready to use.")
        print("\nNext steps:")
        print("1. Set GEMINI_API_KEY in .env file")
        print("2. Run: python -m scripts.dict.translation.main --strong-number H1 --dry-run")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())


