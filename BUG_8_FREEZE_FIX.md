# Bug #8: Game Freezes When Clicking Next After Name Entry

## Problem
Game freezes/hangs when user enters their name and clicks "Next" button in character creation.

## Root Causes (2 issues found)

### Issue 1: Infinite Loop in refresh_step_content()
**Location**: tui/character_screen.py:161

The while loop was causing an infinite loop:
```python
while True:
    children = content_container.query("*")
    if not children:
        break
    for child in children:
        child.remove()
```

The `child.remove()` doesn't take effect immediately in Textual's render cycle, so the query kept returning the same children, causing an infinite loop.

**Fix**: Collect all children first into a list, then remove them:
```python
children_to_remove = list(content_container.query("*"))
for child in children_to_remove:
    try:
        child.remove()
    except Exception:
        pass
```

### Issue 2: Name Input Not Saved
**Location**: tui/character_screen.py:556

When clicking "Next", the name from the Input field wasn't being saved to character_data before advancing to the next step.

**Fix**: Added code to capture the input value before advancing:
```python
if wizard.current_step == 1:
    # Get name from input
    try:
        name_input = wizard.query_one("#input-name", Input)
        wizard.character_data["name"] = name_input.value
    except Exception:
        pass
```

## Result
- No more freezing
- Name is properly saved
- Character creation flows smoothly through all steps

## Total Bugs Fixed: 8

1. Cryptography import
2. Unicode encoding  
3. Import name mismatch
4. Missing logs directory
5. Textual widget mount error
6. Duplicate IDs (first attempt)
7. Duplicate IDs (final fix - no IDs)
8. Freeze on name entry + infinite loop

Game is now fully functional!
