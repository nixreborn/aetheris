# Combat System Documentation

## Overview

The Shards of Eternity combat system is a comprehensive, Souls-like turn-based combat engine featuring stamina management, status effects, enemy AI, and class-specific abilities.

## Architecture

### Core Components

1. **combat/system.py** - Main combat engine
2. **combat/enemies.py** - Enemy definitions and AI
3. **combat/abilities.py** - Class-specific abilities

## Combat System (system.py)

### Key Features

- **Stamina-based Combat**: All actions consume stamina
- **Attack Types**:
  - Light Attack (15 stamina) - Fast, reliable
  - Heavy Attack (35 stamina) - Powerful, slower, can cause bleed
  - Dodge (20 stamina) - Evade next attack
  - Block (10 stamina) - Reduce damage by 60%
  - Parry (25 stamina) - Counter-attack on success

### Combat Flow

```python
from combat import CombatSystem, AttackType
from database import get_db_session

# Initialize combat
with get_db_session() as session:
    combat = CombatSystem(player, enemy, session=session)

    # Execute rounds
    result = combat.execute_round(AttackType.LIGHT_ATTACK)

    # Check result
    if result['combat_ended']:
        if result['player_won']:
            print(f"Victory! Gained {result['souls_gained']} souls")
```

### Status Effects

- **BLEED** - Damage over time (3 rounds)
- **POISON** - Damage over time (5 rounds)
- **BURN** - Fire damage over time
- **FROST** - Slows enemy
- **STUN** - Skip next turn
- **WEAKNESS** - Reduce attack by 25%
- **STRENGTH_BUFF** - Increase attack by 25%
- **DEFENSE_BUFF** - Increase defense by 25%
- **REGENERATION** - Heal over time

### Combat Statistics

Calculated from character stats:

```python
combat_stats = {
    "attack_power": 10 + STR_mod + weapon_bonus,
    "defense": 10 + DEX_mod + armor_bonus,
    "accuracy": 60 + (DEX_mod * 3) + (STR_mod * 2),
    "evasion": 10 + (DEX_mod * 4),
    "critical_chance": 0.05 + (DEX_mod * 0.01),
    "critical_damage": 1.5 + (STR_mod * 0.1),
    "initiative": 10 + DEX_mod,
    "poise": 10 + CON_mod
}
```

### Damage Calculation

1. Base damage = attacker's attack_power
2. Apply attack multiplier (light: 1.0x, heavy: 2.2x)
3. Apply status modifiers (weakness, strength buff)
4. Roll for critical (damage * critical_damage)
5. Apply defender's defense mitigation
6. Apply blocking (60% reduction if blocking)

## Enemy System (enemies.py)

### Enemy Types

- **BASIC** - Standard enemies (10-30 souls)
- **ELITE** - Tougher foes (50-150 souls)
- **MINI_BOSS** - Challenge encounters (150-350 souls)
- **BOSS** - Major encounters (500-1500 souls)
- **WORLD_BOSS** - Epic battles (2000-6000 souls)

### AI Behaviors

- **AGGRESSIVE** - Prefers heavy attacks
- **DEFENSIVE** - Focuses on blocking/parrying
- **BALANCED** - Mix of all tactics
- **TACTICAL** - Adapts to situation
- **BERSERKER** - All-out offense
- **COWARD** - Defensive when hurt

### Creating Enemies

```python
from combat import EnemyFactory, EnemyType

# Create specific enemy
enemy = EnemyFactory.create_enemy("hollow_soldier", level_override=5)

# Create random enemy for player level
enemy = EnemyFactory.get_random_enemy_for_level(
    player_level=10,
    enemy_type=EnemyType.ELITE
)

# List all enemies
enemies = EnemyFactory.list_enemies(EnemyType.BOSS)
```

### Available Enemies

#### Basic Enemies
- **Hollow Soldier** (Lv1) - Balanced undead warrior
- **Corrupt Wolf** (Lv2) - Aggressive beast with bleed
- **Skeleton Warrior** (Lv3) - Defensive, poison immune

#### Elite Enemies
- **Dark Knight** (Lv5) - Heavily armored tactical fighter
- **Frost Mage** (Lv6) - Ranged caster with frost abilities

#### Mini-Bosses
- **Corrupted Guardian** (Lv8) - Tanky with regeneration

#### Bosses
- **Lord of Cinders** (Lv10) - Fire-based boss with phases
- **Crystal Shard Guardian** (Lv12) - Reality-warping boss

#### World Bosses
- **Aetherfall Titan** (Lv20) - Massive raid encounter

### Enemy Resistances

Enemies have resistance multipliers for damage types:
- 0.0 = Immune
- 0.5 = Resistant
- 1.0 = Normal
- 1.5+ = Vulnerable

### Loot System

```python
from combat import LootGenerator

template = EnemyFactory.get_template("dark_knight")
loot = LootGenerator.generate_loot(template)

print(f"Souls: {loot['souls']}")
print(f"Items: {loot['items']}")
```

## Ability System (abilities.py)

### Class Abilities

Each class has 4-5 unique abilities:

#### Warrior
- **Whirlwind Strike** - AOE attack (40 stamina, 3 round cooldown)
- **Shield Bash** - Stun attack (30 stamina, 2 round cooldown)
- **Battle Cry** - Strength buff (25 stamina, 4 round cooldown)
- **Execute** - High damage finisher (50 stamina, 5 round cooldown)

#### Sorcerer
- **Fireball** - Fire damage + burn (30 mana, 1 round cooldown)
- **Ice Storm** - AOE frost damage (50 mana, 4 round cooldown)
- **Mana Shield** - Defense buff (40 mana, 3 round cooldown)
- **Lightning Bolt** - High single target (35 mana, 2 round cooldown)
- **Arcane Regeneration** - Heal over time (45 mana, 5 round cooldown)

#### Rogue
- **Backstab** - Guaranteed critical (35 stamina, 3 round cooldown)
- **Poison Blade** - Poison damage (25 stamina, 4 round cooldown)
- **Shadow Step** - Evasion buff (30 stamina, 3 round cooldown)
- **Fan of Knives** - AOE bleed (45 stamina, 4 round cooldown)

#### Paladin
- **Divine Smite** - Holy damage (35 mana, 2 round cooldown)
- **Lay on Hands** - Self heal (40 mana, 4 round cooldown)
- **Holy Shield** - Defense buff (30 mana, 5 round cooldown)
- **Judgement** - AOE holy damage (60 mana, 5 round cooldown)

#### Necromancer
- **Death Bolt** - Dark damage (30 mana, 1 round cooldown)
- **Life Drain** - Damage + self heal (40 mana, 3 round cooldown)
- **Curse of Weakness** - Weaken enemy (35 mana, 4 round cooldown)
- **Dark Ritual** - Convert health to mana (30 health, 3 round cooldown)
- **Plague Cloud** - AOE poison (55 mana, 5 round cooldown)

#### Ranger
- **Precise Shot** - High crit chance (25 stamina, 2 round cooldown)
- **Multi-Shot** - AOE attack (40 stamina, 3 round cooldown)
- **Hunter's Mark** - Increase damage to target (20 stamina, 4 round cooldown)
- **Nature's Blessing** - Heal + regen (35 mana, 4 round cooldown)
- **Explosive Arrow** - AOE burn damage (50 stamina, 5 round cooldown)

### Using Abilities

```python
from combat import AbilityManager

# Create ability manager
ability_mgr = AbilityManager(character)

# List available abilities
abilities = ability_mgr.get_available_abilities()
for ability in abilities:
    if ability['can_use']:
        print(f"{ability['name']}: {ability['description']}")

# Use an ability
success, message, effect = ability_mgr.use_ability("Fireball", target=enemy)

if success:
    print(f"Damage: {effect.damage}")
    if effect.status_effect:
        print(f"Applied: {effect.status_effect.value}")

# Tick cooldowns each round
ability_mgr.tick_cooldowns()
```

### Ability Scaling

Abilities scale with character stats:

```python
# Fireball scales with Intelligence
base_damage = 35
int_modifier = (intelligence - 10) // 2
scaling_factor = 2.0

final_damage = base_damage * (1 + (int_modifier * scaling_factor * 0.1))
```

## Integration with Database

Combat logs events to the database:

```python
# Combat automatically logs:
- Combat victories/defeats (CharacterMemory)
- Souls gained
- Experience gained
- Health/stamina changes
- Items looted (future feature)
```

## Integration with LLM

Combat descriptions can be generated dynamically:

```python
# Enable LLM descriptions
combat = CombatSystem(player, enemy, session=session, use_llm=True)

# System will generate narrative descriptions like:
"The warrior's blade arcs through the air in a devastating overhead strike,
crashing into the hollow soldier's rusty armor with a thunderous CLANG!
The force of the blow sends the undead warrior stumbling backward, taking 45 damage!"
```

## Example Usage

See `examples/combat_example.py` for comprehensive examples:

```bash
python examples/combat_example.py
```

## Future Enhancements

- [ ] Multi-target abilities
- [ ] Combo system
- [ ] Weapon special abilities
- [ ] Environmental effects
- [ ] Multiplayer combat
- [ ] Advanced boss mechanics (phases, transformations)
- [ ] Elemental weakness system
- [ ] Equipment durability
- [ ] Combat replay system

## Performance Notes

- Combat rounds execute in <100ms without LLM
- LLM descriptions add 1-3s per description
- Database commits happen at combat end for efficiency
- Status effects processed in O(n) time

## Testing

Run combat tests:

```bash
pytest tests/test_combat.py -v
```

## API Reference

### CombatSystem

```python
class CombatSystem:
    def __init__(
        self,
        player: Character,
        enemy: Character,
        session: Optional[Session] = None,
        use_llm: bool = True
    )

    def execute_round(
        self,
        player_action: AttackType,
        player_target_ability: Optional[str] = None
    ) -> Dict[str, Any]

    def get_available_actions(
        self,
        is_player: bool = True
    ) -> List[Dict[str, Any]]
```

### EnemyFactory

```python
class EnemyFactory:
    @staticmethod
    def create_enemy(
        template_name: str,
        level_override: Optional[int] = None,
        session: Optional[Session] = None
    ) -> Character

    @staticmethod
    def get_random_enemy_for_level(
        player_level: int,
        enemy_type: Optional[EnemyType] = None,
        session: Optional[Session] = None
    ) -> Character
```

### AbilityManager

```python
class AbilityManager:
    def __init__(self, character: Character)

    def get_available_abilities(self) -> List[Dict[str, Any]]

    def use_ability(
        self,
        ability_name: str,
        target: Optional[Character] = None
    ) -> Tuple[bool, str, Optional[AbilityEffect]]

    def tick_cooldowns(self)
```

---

**Version**: 1.0
**Last Updated**: 2025-01-18
**Compatibility**: Shards of Eternity v0.1+
