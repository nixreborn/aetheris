"""
Integration tests for the LLM module.
Tests fallback functionality without requiring API keys.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.generator import LLMGenerator, get_llm_generator
from llm.prompts import get_fallback_text, PromptType


def test_fallback_text():
    """Test fallback text generation."""
    print("Testing fallback text...")

    # Test location fallbacks
    location_default = get_fallback_text(PromptType.LOCATION_DESCRIPTION)
    location_stable = get_fallback_text(PromptType.LOCATION_DESCRIPTION, "stable")
    location_fractured = get_fallback_text(PromptType.LOCATION_DESCRIPTION, "fractured")
    location_corrupted = get_fallback_text(PromptType.LOCATION_DESCRIPTION, "corrupted")

    assert location_default
    assert location_stable
    assert location_fractured
    assert location_corrupted
    assert location_stable != location_fractured
    print("  ✓ Location fallbacks working")

    # Test NPC fallbacks
    npc_dialogue = get_fallback_text(PromptType.NPC_DIALOGUE)
    assert npc_dialogue
    print("  ✓ NPC dialogue fallbacks working")

    # Test combat fallbacks
    combat_hit = get_fallback_text(PromptType.COMBAT_DESCRIPTION, "hit")
    combat_miss = get_fallback_text(PromptType.COMBAT_DESCRIPTION, "miss")
    combat_critical = get_fallback_text(PromptType.COMBAT_DESCRIPTION, "critical")
    assert combat_hit
    assert combat_miss
    assert combat_critical
    assert combat_hit != combat_miss
    print("  ✓ Combat fallbacks working")

    # Test event fallbacks
    event_shard = get_fallback_text(PromptType.EVENT_NARRATIVE, "shard_collected")
    event_aetherfall = get_fallback_text(PromptType.EVENT_NARRATIVE, "aetherfall")
    assert event_shard
    assert event_aetherfall
    print("  ✓ Event fallbacks working")

    print("All fallback tests passed!\n")


async def test_generator_with_disabled_llm():
    """Test generator with LLM disabled (uses fallbacks)."""
    print("Testing LLMGenerator with LLM disabled...")

    generator = LLMGenerator()
    generator.set_enabled(False)  # Disable LLM to force fallbacks

    # Test location description
    location_desc = await generator.generate_location_description(
        "The Shattered Cathedral",
        "corrupted"
    )
    assert location_desc
    assert len(location_desc) > 0
    print(f"  ✓ Location: {location_desc[:50]}...")

    # Test NPC dialogue
    npc_dialogue = await generator.generate_npc_dialogue(
        "The Blind Seer",
        "Player seeks knowledge",
        "asks about the Shards"
    )
    assert npc_dialogue
    print(f"  ✓ NPC: {npc_dialogue[:50]}...")

    # Test combat description
    combat_desc = await generator.generate_combat_description(
        "Player",
        "Enemy",
        "slash",
        "critical",
        45
    )
    assert combat_desc
    print(f"  ✓ Combat: {combat_desc[:50]}...")

    # Test event narrative
    event_narrative = await generator.generate_event_narrative(
        "shard_collected",
        {"location": "Test", "participants": ["Player"]}
    )
    assert event_narrative
    print(f"  ✓ Event: {event_narrative[:50]}...")

    print("All generator tests passed!\n")


async def test_batch_generation():
    """Test batch generation with disabled LLM."""
    print("Testing batch generation...")

    generator = LLMGenerator()
    generator.set_enabled(False)

    requests = [
        {
            "type": "location",
            "location_name": "Area 1",
            "reality_type": "stable"
        },
        {
            "type": "location",
            "location_name": "Area 2",
            "reality_type": "fractured"
        },
        {
            "type": "combat",
            "attacker": "Player",
            "defender": "Enemy",
            "action": "strike",
            "result": "hit"
        }
    ]

    results = await generator.generate_multiple_descriptions(requests)

    assert len(results) == len(requests)
    assert all(result for result in results)
    print(f"  ✓ Generated {len(results)} descriptions")
    print("Batch generation tests passed!\n")


def test_generator_stats():
    """Test stats tracking."""
    print("Testing stats tracking...")

    generator = get_llm_generator()
    stats = generator.get_stats()

    assert "enabled" in stats
    assert "provider" in stats
    assert "model" in stats
    assert "request_count" in stats
    assert "cache_size" in stats

    print(f"  ✓ Stats: {stats}")
    print("Stats tests passed!\n")


def test_cache_management():
    """Test cache operations."""
    print("Testing cache management...")

    generator = get_llm_generator()

    # Clear cache
    generator.clear_cache()
    stats = generator.get_stats()
    assert stats["cache_size"] == 0
    print("  ✓ Cache cleared")

    # Test cache key creation
    key = generator._make_cache_key("test", "value", 123)
    assert key == "test|value|123"
    print("  ✓ Cache key creation works")

    print("Cache tests passed!\n")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("LLM Integration Tests")
    print("=" * 60)
    print()

    try:
        # Test fallback text
        test_fallback_text()

        # Test generator with disabled LLM
        await test_generator_with_disabled_llm()

        # Test batch generation
        await test_batch_generation()

        # Test stats
        test_generator_stats()

        # Test cache
        test_cache_management()

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
