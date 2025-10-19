"""
Standalone test for prompts module (no dependencies).
Tests prompt formatting and fallback text without requiring settings or API clients.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prompts import (
    format_location_prompt,
    format_npc_dialogue_prompt,
    format_combat_prompt,
    format_event_prompt,
    get_fallback_text,
    PromptType,
    SYSTEM_PROMPT_BASE,
    SYSTEM_PROMPT_LOCATION,
    SYSTEM_PROMPT_NPC,
    SYSTEM_PROMPT_COMBAT,
    SYSTEM_PROMPT_EVENT,
)


def test_system_prompts():
    """Test that all system prompts are defined."""
    print("Testing system prompts...")

    assert len(SYSTEM_PROMPT_BASE) > 0
    assert "Shards of Eternity" in SYSTEM_PROMPT_BASE
    assert "dark fantasy" in SYSTEM_PROMPT_BASE.lower()

    assert len(SYSTEM_PROMPT_LOCATION) > 0
    assert SYSTEM_PROMPT_BASE in SYSTEM_PROMPT_LOCATION

    assert len(SYSTEM_PROMPT_NPC) > 0
    assert SYSTEM_PROMPT_BASE in SYSTEM_PROMPT_NPC

    assert len(SYSTEM_PROMPT_COMBAT) > 0
    assert SYSTEM_PROMPT_BASE in SYSTEM_PROMPT_COMBAT

    assert len(SYSTEM_PROMPT_EVENT) > 0
    assert SYSTEM_PROMPT_BASE in SYSTEM_PROMPT_EVENT

    print("  [OK] All system prompts defined and valid")


def test_format_location_prompt():
    """Test location prompt formatting."""
    print("\nTesting location prompt formatting...")

    # Basic test
    prompts = format_location_prompt(
        "The Shattered Cathedral",
        "corrupted"
    )

    assert "system" in prompts
    assert "user" in prompts
    assert "The Shattered Cathedral" in prompts["user"]
    assert "corrupted" in prompts["user"]
    print("  [OK] Basic location prompt")

    # With context
    prompts_context = format_location_prompt(
        "The Eternal Flame",
        "stable",
        context={
            "description": "A sacred fire",
            "features": ["eternal flames", "ancient shrine"],
            "corruption_level": "low"
        }
    )

    assert "The Eternal Flame" in prompts_context["user"]
    assert "eternal flames" in prompts_context["user"]
    assert "ancient shrine" in prompts_context["user"]
    print("  [OK] Location prompt with context")


def test_format_npc_dialogue_prompt():
    """Test NPC dialogue prompt formatting."""
    print("\nTesting NPC dialogue prompt formatting...")

    prompts = format_npc_dialogue_prompt(
        "The Blind Seer",
        "Player seeks knowledge",
        "asks about the Shards",
        "Ancient oracle"
    )

    assert "system" in prompts
    assert "user" in prompts
    assert "The Blind Seer" in prompts["user"]
    assert "Ancient oracle" in prompts["user"]
    assert "asks about the Shards" in prompts["user"]
    print("  [OK] NPC dialogue prompt")


def test_format_combat_prompt():
    """Test combat prompt formatting."""
    print("\nTesting combat prompt formatting...")

    prompts = format_combat_prompt(
        "Corrupted Knight",
        "Player",
        "overhead slash",
        "critical",
        damage=45,
        special_effects="void energy"
    )

    assert "system" in prompts
    assert "user" in prompts
    assert "Corrupted Knight" in prompts["user"]
    assert "Player" in prompts["user"]
    assert "overhead slash" in prompts["user"]
    assert "critical" in prompts["user"]
    assert "45" in prompts["user"]
    assert "void energy" in prompts["user"]
    print("  [OK] Combat prompt with all parameters")

    # Minimal test
    prompts_minimal = format_combat_prompt(
        "Enemy",
        "Player",
        "strike",
        "hit"
    )
    assert "Enemy" in prompts_minimal["user"]
    print("  [OK] Combat prompt minimal")


def test_format_event_prompt():
    """Test event prompt formatting."""
    print("\nTesting event prompt formatting...")

    prompts = format_event_prompt(
        "shard_collected",
        {
            "location": "The Abyssal Depths",
            "participants": ["Valeria", "companions"],
            "details": {
                "shard_type": "Shard of Time",
                "count": 7
            },
            "context": "World trembles"
        }
    )

    assert "system" in prompts
    assert "user" in prompts
    assert "shard_collected" in prompts["user"]
    assert "The Abyssal Depths" in prompts["user"]
    assert "Valeria" in prompts["user"]
    assert "Shard of Time" in prompts["user"]
    print("  [OK] Event prompt")


def test_fallback_text():
    """Test fallback text generation."""
    print("\nTesting fallback text...")

    # Location fallbacks
    location_default = get_fallback_text(PromptType.LOCATION_DESCRIPTION)
    location_stable = get_fallback_text(PromptType.LOCATION_DESCRIPTION, "stable")
    location_fractured = get_fallback_text(PromptType.LOCATION_DESCRIPTION, "fractured")
    location_corrupted = get_fallback_text(PromptType.LOCATION_DESCRIPTION, "corrupted")

    assert location_default
    assert location_stable
    assert location_fractured
    assert location_corrupted
    assert location_stable != location_fractured
    print("  [OK] Location fallbacks")

    # NPC fallbacks
    npc1 = get_fallback_text(PromptType.NPC_DIALOGUE)
    npc2 = get_fallback_text(PromptType.NPC_DIALOGUE)
    assert npc1
    # Note: May be the same due to random choice, that's OK
    print("  [OK] NPC dialogue fallbacks")

    # Combat fallbacks
    combat_hit = get_fallback_text(PromptType.COMBAT_DESCRIPTION, "hit")
    combat_miss = get_fallback_text(PromptType.COMBAT_DESCRIPTION, "miss")
    combat_critical = get_fallback_text(PromptType.COMBAT_DESCRIPTION, "critical")
    combat_blocked = get_fallback_text(PromptType.COMBAT_DESCRIPTION, "blocked")

    assert combat_hit
    assert combat_miss
    assert combat_critical
    assert combat_blocked
    assert combat_hit != combat_miss
    print("  [OK] Combat fallbacks")

    # Event fallbacks
    event_shard = get_fallback_text(PromptType.EVENT_NARRATIVE, "shard_collected")
    event_aetherfall = get_fallback_text(PromptType.EVENT_NARRATIVE, "aetherfall")
    event_boss = get_fallback_text(PromptType.EVENT_NARRATIVE, "boss_defeated")
    event_default = get_fallback_text(PromptType.EVENT_NARRATIVE, "unknown_event")

    assert event_shard
    assert event_aetherfall
    assert event_boss
    assert event_default
    print("  [OK] Event fallbacks")


def main():
    """Run all tests."""
    print("=" * 60)
    print("LLM Prompts Module Tests")
    print("=" * 60)
    print()

    try:
        test_system_prompts()
        test_format_location_prompt()
        test_format_npc_dialogue_prompt()
        test_format_combat_prompt()
        test_format_event_prompt()
        test_fallback_text()

        print("\n" + "=" * 60)
        print("All tests passed! [OK]")
        print("=" * 60)

        # Show some example output
        print("\nExample fallback text:")
        print(f"  Location (stable): {get_fallback_text(PromptType.LOCATION_DESCRIPTION, 'stable')}")
        print(f"  Location (corrupted): {get_fallback_text(PromptType.LOCATION_DESCRIPTION, 'corrupted')}")
        print(f"  NPC dialogue: {get_fallback_text(PromptType.NPC_DIALOGUE)}")
        print(f"  Combat (critical): {get_fallback_text(PromptType.COMBAT_DESCRIPTION, 'critical')}")
        print(f"  Event (shard): {get_fallback_text(PromptType.EVENT_NARRATIVE, 'shard_collected')}")

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
