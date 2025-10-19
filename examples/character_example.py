"""
Example usage of the Character Creation and Management system.

This script demonstrates how to:
1. Initialize the database
2. Create a new character
3. Manage character stats and inventory
4. Level up and track progression
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import init_database
from database.models import RaceType, ClassType, FactionType
from characters import CharacterCreator, CharacterManager


def main():
    """Run character system examples."""
    print("=" * 60)
    print("Shards of Eternity - Character System Example")
    print("=" * 60)

    # Initialize database
    print("\n1. Initializing database...")
    init_database()
    print("   Database initialized!")

    # Create a character creator
    creator = CharacterCreator()
    manager = CharacterManager()

    # Example 1: Create a character with rolled stats
    print("\n2. Creating a Warrior character...")
    try:
        warrior = creator.create_character(
            name="Thorgrim Ironheart",
            race=RaceType.DWARF,
            character_class=ClassType.WARRIOR,
            faction=FactionType.IRON_BROTHERHOOD,
            stat_method="heroic"  # Heroic rolling for better stats
        )
        print(f"   Created: {warrior.name}")
        print(f"   Race: {warrior.race.value}, Class: {warrior.character_class.value}")
        print(f"   Faction: {warrior.faction.value}")
        print(f"   Stats: STR={warrior.strength}, DEX={warrior.dexterity}, CON={warrior.constitution}")
        print(f"   Resources: HP={warrior.health}/{warrior.max_health}, "
              f"Stamina={warrior.stamina}/{warrior.max_stamina}, "
              f"Mana={warrior.mana}/{warrior.max_mana}")
        print(f"   Starting Souls: {warrior.souls}")

    except Exception as e:
        print(f"   Error creating character: {e}")
        return

    # Example 2: Create a character with point-buy
    print("\n3. Creating a Sorcerer with point-buy stats...")
    try:
        # Define custom stats (total must equal 60)
        custom_stats = {
            "strength": 8,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 16,
            "wisdom": 12,
            "charisma": 4
        }

        # Validate stats
        is_valid, error, _ = creator.point_buy_stats(custom_stats)
        if not is_valid:
            print(f"   Invalid stats: {error}")
        else:
            mage = creator.create_character(
                name="Elara Moonwhisper",
                race=RaceType.ELF,
                character_class=ClassType.SORCERER,
                faction=FactionType.AETHER_SEEKERS,
                stats=custom_stats
            )
            print(f"   Created: {mage.name}")
            print(f"   Race: {mage.race.value}, Class: {mage.character_class.value}")
            print(f"   Stats: INT={mage.intelligence}, WIS={mage.wisdom}, CON={mage.constitution}")

    except Exception as e:
        print(f"   Error creating character: {e}")

    # Example 3: Get character summary
    print("\n4. Getting character summary...")
    summary = manager.get_character_summary(warrior.id)
    print(f"   Character: {summary['name']}")
    print(f"   Level: {summary['level']} ({summary['experience']} XP)")
    print(f"   Next level in: {summary['next_level_xp']} XP")
    print(f"   Equipped items: {len(summary['equipped_items'])}")
    print(f"   Inventory value: {summary['total_inventory_value']} souls")

    # Show derived stats
    derived = summary['derived_stats']
    print(f"\n   Derived Stats:")
    print(f"   - Armor Class: {derived['armor_class']}")
    print(f"   - Attack Power: {derived['attack_power']}")
    print(f"   - Magic Power: {derived['magic_power']}")
    print(f"   - Initiative: {derived['initiative']}")

    # Example 4: Update character resources
    print("\n5. Testing resource updates...")
    print(f"   Taking 30 damage...")
    new_health = manager.update_health(warrior.id, -30)
    print(f"   New health: {new_health}")

    print(f"   Using 20 stamina...")
    new_stamina = manager.update_stamina(warrior.id, -20)
    print(f"   New stamina: {new_stamina}")

    # Example 5: Add items to inventory
    print("\n6. Adding items to inventory...")
    manager.add_item_to_inventory(
        warrior.id,
        item_name="Greater Health Potion",
        item_type="consumable",
        quantity=5,
        description="Restores 100 health points",
        value=50
    )
    print("   Added 5x Greater Health Potion")

    manager.add_item_to_inventory(
        warrior.id,
        item_name="Steel Greatsword",
        item_type="weapon",
        description="A massive two-handed sword",
        attack_bonus=20,
        value=150
    )
    print("   Added Steel Greatsword")

    # Example 6: Add experience and level up
    print("\n7. Adding experience...")
    exp_to_add = 150
    new_exp, leveled_up, new_level = manager.add_experience(warrior.id, exp_to_add)
    print(f"   Added {exp_to_add} XP. New total: {new_exp}")

    if leveled_up:
        print(f"   LEVEL UP! Now level {new_level}!")
        # Reload character to see updated stats
        updated_summary = manager.get_character_summary(warrior.id)
        print(f"   New max health: {updated_summary['resources']['health']}")
        print(f"   Updated stats:")
        for stat, value in updated_summary['stats'].items():
            print(f"     {stat.upper()}: {value}")

    # Example 7: Character memories
    print("\n8. Adding character memories...")
    manager.add_memory(
        warrior.id,
        memory_type="quest",
        title="The Lost Artifact",
        description="Discovered an ancient artifact in the ruins",
        location_name="Ancient Ruins",
        souls_gained=50,
        faction_impact=FactionType.IRON_BROTHERHOOD.value
    )
    print("   Added quest memory")

    memories = manager.get_character_memories(warrior.id, limit=5)
    print(f"   Recent memories ({len(memories)}):")
    for memory in memories:
        print(f"     - [{memory.memory_type}] {memory.title}")

    # Example 8: Rest character
    print("\n9. Resting character...")
    restored = manager.rest_character(warrior.id, full_rest=True)
    print(f"   Restored: {restored['health_restored']} HP, "
          f"{restored['stamina_restored']} stamina, "
          f"{restored['mana_restored']} mana")

    # Example 9: Add souls (currency)
    print("\n10. Managing currency...")
    print(f"   Current souls: {manager.load_character(warrior.id).souls}")
    new_souls = manager.add_souls(warrior.id, 100)
    print(f"   Added 100 souls. New total: {new_souls}")

    # Final summary
    print("\n" + "=" * 60)
    print("Character System Example Complete!")
    print("=" * 60)

    final_summary = manager.get_character_summary(warrior.id)
    print(f"\nFinal Character State:")
    print(f"  Name: {final_summary['name']}")
    print(f"  Level: {final_summary['level']}")
    print(f"  Resources: {final_summary['resources']['health']}, "
          f"{final_summary['resources']['stamina']}, "
          f"{final_summary['resources']['mana']}")
    print(f"  Souls: {final_summary['souls']}")
    print(f"  Inventory items: {len(final_summary['inventory_items'])}")
    print(f"  Location: {final_summary['location']}")


if __name__ == "__main__":
    main()
