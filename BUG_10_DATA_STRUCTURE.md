# Bug #10: KeyError 'level' in Main Game Screen

## Problem
After creating a character successfully, the game crashed when trying to load the main game screen:
`KeyError: 'level'`

## Root Cause
**Location**: tui/main_screen.py:96

The character data structure returned by the database has changed. Previously, fields like `level`, `health`, `souls` were at the top level. Now they're nested:

**Old structure (expected by TUI):**
```python
{
    'name': 'Nix',
    'level': 1,
    'health': 100,
    'max_health': 100,
    'souls': 90,
    ...
}
```

**New structure (from database):**
```python
{
    'name': 'Nix',
    'progression': {'level': 1, 'experience': 0, 'souls': 90},
    'resources': {'health': 70, 'max_health': 70, 'stamina': 70, ...},
    ...
}
```

## Fix
Added compatibility code to handle both old and new data structures:

```python
# Handle both old and new data structures
level = char.get('level') or char.get('progression', {}).get('level', 1)
souls = char.get('souls') or char.get('progression', {}).get('souls', 0)
health = char.get('health') or char.get('resources', {}).get('health', 100)
max_health = char.get('max_health') or char.get('resources', {}).get('max_health', 100)
stamina = char.get('stamina') or char.get('resources', {}).get('stamina', 100)
max_stamina = char.get('max_stamina') or char.get('resources', {}).get('max_stamina', 100)
mana = char.get('mana') or char.get('resources', {}).get('mana', 50)
max_mana = char.get('max_mana') or char.get('resources', {}).get('max_mana', 50)
```

This approach:
- Tries the old structure first (backward compatible)
- Falls back to new nested structure
- Provides sensible defaults if neither exists

## Result
Main game screen now loads correctly with character stats displayed properly!

## Total Bugs Fixed: 10

1. Cryptography import
2. Unicode encoding
3. Import name mismatch
4. Missing logs directory
5. Textual widget mount error
6. Duplicate IDs (first attempt)
7. Duplicate IDs (final fix)
8. Freeze on name entry
9. Unexpected session keyword
10. **KeyError on nested data structure**

Game is fully functional from character creation to main game screen!
