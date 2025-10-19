"""
Example usage of the world systems for Shards of Eternity.
Demonstrates how to use FactionManager, ShardManager, and RealityManager.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from world import (
    FactionManager,
    ShardManager,
    RealityManager,
    FactionType
)


def demonstrate_faction_system():
    """Show how to use the faction system."""
    print("\n=== FACTION SYSTEM DEMO ===\n")

    fm = FactionManager()

    # Get information about a faction
    seekers = fm.get_faction(FactionType.SEEKERS)
    print(f"Faction: {seekers.name}")
    print(f"Description: {seekers.description}")
    print(f"Philosophy: {seekers.philosophy}")
    print(f"\nAbilities:")
    for ability in seekers.abilities:
        print(f"  - {ability.name}: {ability.effect}")

    print(f"\nVictory Condition: {seekers.victory_condition.name}")
    print(f"  {seekers.victory_condition.description}")

    # Check faction relationships
    print(f"\nRelationships:")
    for faction_type in FactionType:
        if faction_type != FactionType.SEEKERS:
            rel = fm.get_relationship(FactionType.SEEKERS, faction_type)
            print(f"  vs {faction_type.value}: {rel.value}")


def demonstrate_shard_system():
    """Show how to use the shard system."""
    print("\n\n=== SHARD SYSTEM DEMO ===\n")

    sm = ShardManager()

    # Get information about a shard
    phoenix_flame = sm.get_shard(1)
    print(f"Shard: {phoenix_flame.name}")
    print(f"Element: {phoenix_flame.element.value}")
    print(f"Description: {phoenix_flame.description}")
    print(f"Location: {phoenix_flame.location_name}")
    print(f"\nGuardian: {phoenix_flame.guardian.name} (Level {phoenix_flame.guardian.level})")
    print(f"HP: {phoenix_flame.guardian.health}")
    print(f"Abilities: {', '.join(phoenix_flame.guardian.abilities)}")

    print(f"\nPowers Granted:")
    for power in phoenix_flame.abilities_granted:
        print(f"  - {power}")

    # Simulate capturing shards
    print("\n\nCapturing shards for factions...")
    sm.capture_shard(1, faction_name="Seekers of Truth")
    sm.capture_shard(2, faction_name="Seekers of Truth")
    sm.capture_shard(3, faction_name="Reality Shapers")
    sm.capture_shard(4, faction_name="Reality Shapers")

    # Check distribution
    distribution = sm.get_shard_distribution()
    print("\nCurrent shard distribution:")
    for faction, count in distribution.items():
        print(f"  {faction}: {count} shards")

    # Check if anyone has won
    if sm.check_victory("Seekers of Truth"):
        print("\nSeekers of Truth have won!")
    else:
        seekers_count = sm.get_faction_shard_count("Seekers of Truth")
        print(f"\nSeekers need {12 - seekers_count} more shards to win")


def demonstrate_reality_system():
    """Show how to use the reality system."""
    print("\n\n=== REALITY SYSTEM DEMO ===\n")

    rm = RealityManager()

    # Check reality status
    status = rm.get_reality_status()
    print(f"Current Reality Cycle: {status['cycle']}")
    print(f"Reality State: {status['state']}")
    print(f"Stability: {status['stability']}%")

    # Degrade stability
    print("\nDegrading reality stability...")
    rm.degrade_stability(20)
    status = rm.get_reality_status()
    print(f"New Stability: {status['stability']}%")
    print(f"New State: {status['state']}")

    # Apply a transformation
    print("\nApplying reality transformation...")
    from world.reality import RealityTransformation, TransformationType

    transformation = RealityTransformation(
        transformation_type=TransformationType.ENEMY_MUTATION,
        name="Test Corruption",
        description="Enemies become stronger",
        effects={"enemy_power": 1.5}
    )
    rm.apply_transformation(transformation)

    status = rm.get_reality_status()
    print(f"Active transformations: {status['active_transformations']}")
    for trans in status['transformations']:
        print(f"  - {trans['name']}: {trans['description']}")


def demonstrate_aetherfall():
    """Show how Aetherfall works."""
    print("\n\n=== AETHERFALL DEMO ===\n")

    fm = FactionManager()
    sm = ShardManager()
    rm = RealityManager()

    # Simulate a faction winning
    print("Simulating Seekers of Truth winning all 12 shards...")
    for shard_id in range(1, 13):
        sm.capture_shard(shard_id, faction_name="Seekers of Truth")

    # Check if they've won
    if sm.check_victory("Seekers of Truth"):
        print("\nSeekers of Truth have won! Triggering Aetherfall...")

        # Get the winning faction's victory condition
        seekers = fm.get_faction(FactionType.SEEKERS)

        # Trigger Aetherfall
        event = rm.trigger_aetherfall(
            winning_faction="Seekers of Truth",
            faction_victory_condition={
                "reality_changes": seekers.victory_condition.reality_changes,
                "world_effects": seekers.victory_condition.world_effects
            }
        )

        print(f"\nAetherfall Event - Cycle {event.cycle_number}")
        print(f"Winner: {event.winning_faction}")
        print(f"Victory: {seekers.victory_condition.name}")
        print(f"\nWorld Effects:")
        for effect in event.transformations_applied:
            print(f"  - {effect}")

        # Check new reality state
        status = rm.get_reality_status()
        print(f"\nNew Reality State: {status['state']}")
        print(f"Active Transformations: {status['active_transformations']}")


if __name__ == "__main__":
    print("=" * 60)
    print("SHARDS OF ETERNITY - WORLD SYSTEMS DEMO")
    print("=" * 60)

    demonstrate_faction_system()
    demonstrate_shard_system()
    demonstrate_reality_system()
    demonstrate_aetherfall()

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
