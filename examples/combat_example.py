"""
Example usage of the Shards of Eternity combat system.

Demonstrates:
- Creating characters and enemies
- Initiating combat
- Using different attack types
- Using class abilities
- Processing combat rounds
- Handling combat results
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import init_database, get_db_session
from database.models import ClassType, RaceType, FactionType
from characters.character import CharacterCreator, CharacterManager
from combat import (
    CombatSystem,
    AttackType,
    EnemyFactory,
    EnemyType,
    AbilityManager
)


def create_test_character():
    """Create a test character for combat."""
    print("\n=== Creating Test Character ===")

    creator = CharacterCreator()

    # Create a warrior character
    character = creator.create_character(
        name="Test Warrior",
        race=RaceType.HUMAN,
        character_class=ClassType.WARRIOR,
        faction=FactionType.IRON_BROTHERHOOD,
        stat_method="heroic"
    )

    print(f"Created: {character.name}")
    print(f"  Level {character.level} {character.race.value} {character.character_class.value}")
    print(f"  HP: {character.health}/{character.max_health}")
    print(f"  Stamina: {character.stamina}/{character.max_stamina}")
    print(f"  Stats: STR {character.strength}, DEX {character.dexterity}, CON {character.constitution}")

    return character


def create_test_enemy(level: int = 1):
    """Create a test enemy."""
    print("\n=== Creating Enemy ===")

    with get_db_session() as session:
        # Create a basic enemy
        enemy = EnemyFactory.create_enemy("hollow_soldier", level_override=level, session=session)

        print(f"Created: {enemy.name}")
        print(f"  Level {enemy.level}")
        print(f"  HP: {enemy.health}/{enemy.max_health}")
        print(f"  Stamina: {enemy.stamina}/{enemy.max_stamina}")

        return enemy


def basic_combat_example():
    """Demonstrate basic combat mechanics."""
    print("\n" + "=" * 60)
    print("BASIC COMBAT EXAMPLE")
    print("=" * 60)

    # Create combatants
    player = create_test_character()
    enemy = create_test_enemy(level=1)

    with get_db_session() as session:
        # Initialize combat
        combat = CombatSystem(player, enemy, session=session, use_llm=False)

        print("\n=== Combat Started ===")
        print(f"{player.name} vs {enemy.name}")

        # Round 1: Light attack
        print("\n--- Round 1: Light Attack ---")
        result = combat.execute_round(AttackType.LIGHT_ATTACK)
        print_round_result(result)

        # Round 2: Heavy attack
        print("\n--- Round 2: Heavy Attack ---")
        result = combat.execute_round(AttackType.HEAVY_ATTACK)
        print_round_result(result)

        # Round 3: Block
        print("\n--- Round 3: Defensive Stance ---")
        result = combat.execute_round(AttackType.BLOCK)
        print_round_result(result)

        # Continue combat until one side wins
        round_num = 4
        while not result.get("combat_ended", False) and round_num < 20:
            print(f"\n--- Round {round_num}: Auto-combat ---")
            result = combat.execute_round(AttackType.LIGHT_ATTACK)
            print_round_result(result)
            round_num += 1

        # Print final results
        if result.get("combat_ended"):
            print("\n=== COMBAT ENDED ===")
            if result["player_won"]:
                print(f"Victory! Defeated {enemy.name}")
                print(f"  Souls gained: {result['souls_gained']}")
                print(f"  XP gained: {result['xp_gained']}")
            else:
                print("Defeat...")
            print(f"Combat lasted {result['rounds']} rounds")


def ability_combat_example():
    """Demonstrate combat with abilities."""
    print("\n" + "=" * 60)
    print("ABILITY COMBAT EXAMPLE")
    print("=" * 60)

    # Create a sorcerer character
    creator = CharacterCreator()
    sorcerer = creator.create_character(
        name="Test Sorcerer",
        race=RaceType.ELF,
        character_class=ClassType.SORCERER,
        faction=FactionType.AETHER_SEEKERS,
        stat_method="heroic"
    )

    print(f"\nCreated: {sorcerer.name}")
    print(f"  Mana: {sorcerer.mana}/{sorcerer.max_mana}")

    # Create ability manager
    ability_mgr = AbilityManager(sorcerer)

    print("\n=== Available Abilities ===")
    abilities = ability_mgr.get_available_abilities()
    for ability in abilities:
        print(f"\n{ability['name']}")
        print(f"  {ability['description']}")
        print(f"  Cost: {ability['resource_cost']} {ability['resource_type']}")
        print(f"  Cooldown: {ability['cooldown_remaining']}/{ability.get('cooldown', 0)} rounds")
        print(f"  Ready: {ability['can_use']}")

    # Use an ability
    print("\n=== Using Fireball ===")
    success, message, effect = ability_mgr.use_ability("Fireball")
    print(f"Result: {message}")
    if success and effect:
        print(f"  Damage: {effect.damage}")
        print(f"  Status: {effect.status_effect.value if effect.status_effect else 'None'}")

    # Show updated mana
    print(f"\nMana after ability: {sorcerer.mana}/{sorcerer.max_mana}")

    # Show cooldown
    print("\n=== Abilities After Use ===")
    abilities = ability_mgr.get_available_abilities()
    for ability in abilities:
        if ability['name'] == 'Fireball':
            print(f"{ability['name']}: Cooldown {ability['cooldown_remaining']} rounds")


def multi_enemy_combat_example():
    """Demonstrate combat against different enemy types."""
    print("\n" + "=" * 60)
    print("MULTI-ENEMY COMBAT EXAMPLE")
    print("=" * 60)

    player = create_test_character()

    enemy_types = ["hollow_soldier", "corrupt_wolf", "skeleton_warrior"]

    for enemy_type in enemy_types:
        print(f"\n{'=' * 40}")
        print(f"Fighting: {enemy_type}")
        print('=' * 40)

        with get_db_session() as session:
            enemy = EnemyFactory.create_enemy(enemy_type, session=session)
            combat = CombatSystem(player, enemy, session=session, use_llm=False)

            # Quick combat
            round_num = 1
            result = {}
            while round_num < 30:
                result = combat.execute_round(AttackType.LIGHT_ATTACK)

                if result.get("combat_ended"):
                    break
                round_num += 1

            if result.get("player_won"):
                print(f"\nVictory in {result['rounds']} rounds!")
                print(f"Souls: {result['souls_gained']}, XP: {result['xp_gained']}")
            else:
                print("\nDefeat!")
                break


def boss_combat_example():
    """Demonstrate boss combat."""
    print("\n" + "=" * 60)
    print("BOSS COMBAT EXAMPLE")
    print("=" * 60)

    # Create a high-level character
    creator = CharacterCreator()

    stats = {
        "strength": 18,
        "dexterity": 16,
        "constitution": 18,
        "intelligence": 12,
        "wisdom": 12,
        "charisma": 14
    }

    character = creator.create_character(
        name="Veteran Warrior",
        race=RaceType.DRAGONBORN,
        character_class=ClassType.WARRIOR,
        faction=FactionType.GOLDEN_ORDER,
        stats=stats
    )

    # Level up the character
    char_mgr = CharacterManager()
    char_mgr.add_experience(character.id, 5000)

    # Reload character
    character = char_mgr.load_character(character.id)

    print(f"\nPrepared for boss: {character.name}")
    print(f"  Level {character.level}")
    print(f"  HP: {character.health}/{character.max_health}")

    with get_db_session() as session:
        # Create a boss enemy
        boss = EnemyFactory.create_enemy("corrupted_guardian", session=session)

        print(f"\nBoss: {boss.name}")
        print(f"  Level {boss.level}")
        print(f"  HP: {boss.health}/{boss.max_health}")

        combat = CombatSystem(character, boss, session=session, use_llm=False)

        # Show available actions
        print("\n=== Available Combat Actions ===")
        actions = combat.get_available_actions()
        for action in actions:
            print(f"  {action['action']}: {action['description']} ({'Available' if action['can_use'] else 'Not enough stamina'})")

        # Boss combat with varied tactics
        print("\n=== Boss Fight Begins ===")
        round_num = 1
        result = {}

        tactics = [
            AttackType.HEAVY_ATTACK,
            AttackType.LIGHT_ATTACK,
            AttackType.LIGHT_ATTACK,
            AttackType.DODGE,
            AttackType.HEAVY_ATTACK,
            AttackType.BLOCK,
        ]

        tactic_index = 0

        while round_num < 50:
            action = tactics[tactic_index % len(tactics)]
            result = combat.execute_round(action)

            print(f"\nRound {result.get('round', round_num)}:")
            for action_desc in result.get('actions', []):
                print(f"  {action_desc}")

            print(f"  {result.get('player_status', '')}")
            print(f"  {result.get('enemy_status', '')}")

            if result.get("combat_ended"):
                break

            tactic_index += 1
            round_num += 1

        # Final results
        print("\n" + "=" * 60)
        if result.get("player_won"):
            print("BOSS DEFEATED!")
            print(f"  Rounds: {result['rounds']}")
            print(f"  Souls: {result['souls_gained']}")
            print(f"  XP: {result['xp_gained']}")
        else:
            print("DEFEATED BY BOSS")


def print_round_result(result: dict):
    """Print the results of a combat round."""
    if result.get("combat_ended"):
        return

    print(f"\nRound {result.get('round', '?')}:")
    for action in result.get('actions', []):
        print(f"  {action}")

    print(f"\n{result.get('player_status', '')}")
    print(f"{result.get('enemy_status', '')}")


def enemy_list_example():
    """Show all available enemies."""
    print("\n" + "=" * 60)
    print("ENEMY DATABASE")
    print("=" * 60)

    print("\n=== Basic Enemies ===")
    for enemy_name in EnemyFactory.list_enemies(EnemyType.BASIC):
        template = EnemyFactory.get_template(enemy_name)
        print(f"\n{template.name} (Level {template.level})")
        print(f"  Type: {template.enemy_type.value}")
        print(f"  Behavior: {template.behavior.value}")
        print(f"  HP: {template.base_health}, Stamina: {template.base_stamina}")
        print(f"  Stats: STR {template.base_strength}, DEX {template.base_dexterity}, CON {template.base_constitution}")

    print("\n=== Elite Enemies ===")
    for enemy_name in EnemyFactory.list_enemies(EnemyType.ELITE):
        template = EnemyFactory.get_template(enemy_name)
        print(f"\n{template.name} (Level {template.level})")
        print(f"  Type: {template.enemy_type.value}")
        print(f"  Special Abilities: {', '.join(template.special_abilities)}")

    print("\n=== Bosses ===")
    for enemy_name in EnemyFactory.list_enemies(EnemyType.BOSS):
        template = EnemyFactory.get_template(enemy_name)
        print(f"\n{template.name} (Level {template.level})")
        print(f"  Type: {template.enemy_type.value}")
        print(f"  Special Abilities: {', '.join(template.special_abilities)}")
        print(f"  Phases: {len(template.boss_phases)}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("SHARDS OF ETERNITY - COMBAT SYSTEM EXAMPLES")
    print("=" * 60)

    # Initialize database
    init_database()

    # Run examples
    try:
        # 1. Basic combat
        basic_combat_example()

        # 2. Abilities
        ability_combat_example()

        # 3. Enemy list
        enemy_list_example()

        # 4. Multi-enemy
        # multi_enemy_combat_example()  # Commented out to save time

        # 5. Boss fight
        # boss_combat_example()  # Commented out to save time

    except Exception as e:
        print(f"\nError during example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
