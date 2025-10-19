"""
Example usage of the LLM generator module.
Demonstrates how to use the LLM integration for various game scenarios.
"""
import asyncio
from llm.generator import get_llm_generator


async def main():
    """Run example LLM generation scenarios."""
    generator = get_llm_generator()

    print("=" * 60)
    print("LLM Generator Example Usage")
    print("=" * 60)

    # Test connection
    print("\n1. Testing LLM connection...")
    connected = await generator.test_connection()
    if connected:
        print("   ✓ Connection successful!")
    else:
        print("   ✗ Connection failed - will use fallback text")

    # Example 1: Location Description
    print("\n2. Generating location description...")
    location_desc = await generator.generate_location_description(
        location_name="The Shattered Cathedral",
        reality_type="corrupted",
        context={
            "description": "An ancient cathedral broken by the Aetherfall",
            "features": ["cracked spires", "void rifts", "echoing bells"],
            "corruption_level": "high"
        }
    )
    print(f"   Location: The Shattered Cathedral")
    print(f"   Description: {location_desc}")

    # Example 2: NPC Dialogue
    print("\n3. Generating NPC dialogue...")
    npc_dialogue = await generator.generate_npc_dialogue(
        npc_name="The Blind Seer",
        context="Player approaches seeking knowledge about the Shards",
        player_action="asks about the location of the nearest Shard",
        npc_background="An ancient oracle who has witnessed countless Aetherfalls"
    )
    print(f"   NPC: The Blind Seer")
    print(f"   Dialogue: {npc_dialogue}")

    # Example 3: Combat Description
    print("\n4. Generating combat description...")
    combat_desc = await generator.generate_combat_description(
        attacker="Corrupted Knight",
        defender="Player",
        action="overhead slash with greatsword",
        result="critical",
        damage=45,
        special_effects="void energy trails from the blade"
    )
    print(f"   Combat Action: Corrupted Knight attacks Player")
    print(f"   Description: {combat_desc}")

    # Example 4: Event Narrative
    print("\n5. Generating event narrative...")
    event_narrative = await generator.generate_event_narrative(
        event_type="shard_collected",
        context={
            "location": "The Abyssal Depths",
            "participants": ["Valeria the Brave", "her companions"],
            "details": {
                "shard_type": "Shard of Time",
                "number_collected": 7,
                "threshold": 12
            },
            "context": "The world trembles as another Shard is claimed"
        }
    )
    print(f"   Event: Shard Collected")
    print(f"   Narrative: {event_narrative}")

    # Example 5: Batch Generation
    print("\n6. Batch generating multiple descriptions...")
    requests = [
        {
            "type": "location",
            "location_name": "The Eternal Flame",
            "reality_type": "stable"
        },
        {
            "type": "location",
            "location_name": "The Twisted Woods",
            "reality_type": "fractured"
        },
        {
            "type": "combat",
            "attacker": "Player",
            "defender": "Shadow Beast",
            "action": "parry and riposte",
            "result": "hit",
            "damage": 23
        }
    ]

    results = await generator.generate_multiple_descriptions(requests)
    for i, result in enumerate(results):
        print(f"   Result {i+1}: {result}")

    # Show statistics
    print("\n7. Generator Statistics:")
    stats = generator.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("Example usage complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("\nNote: This example will use fallback text unless LLM is properly configured.")
    print("Configure LLM in .env file with appropriate API keys.\n")

    asyncio.run(main())
