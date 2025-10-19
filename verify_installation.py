#!/usr/bin/env python3
"""
Quick verification script for Shards of Eternity installation.
"""
import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    
    tests = [
        ("Configuration", "from config import settings"),
        ("Database Models", "from database import models"),
        ("Character System", "from characters import character"),
        ("Combat System", "from combat import system"),
        ("World System", "from world import factions, shards, reality"),
        ("LLM Integration", "from llm import generator"),
        ("Network Protocol", "from network import protocol"),
        ("TUI Screens", "from tui import main_screen"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_cmd in tests:
        try:
            exec(import_cmd)
            print(f"  [OK] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def test_database():
    """Test database initialization."""
    print("\nTesting database initialization...")
    
    try:
        from database import init_database
        init_database()
        print("  [OK] Database initialization successful")
        return True
    except Exception as e:
        print(f"  [FAIL] Database initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Shards of Eternity - Installation Verification")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_imports())
    results.append(test_database())
    
    print("\n" + "=" * 60)
    if all(results):
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour installation is working correctly.")
        print("Run 'python main.py' to start the game!")
        return 0
    else:
        print("SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
