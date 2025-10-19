# Combat System Quick Reference

## Quick Start

```python
from combat import CombatSystem, EnemyFactory, AttackType
from database import get_db_session

# Create enemy
enemy = EnemyFactory.create_enemy("hollow_soldier")

# Start combat
with get_db_session() as session:
    combat = CombatSystem(player, enemy, session=session)

    # Execute round
    result = combat.execute_round(AttackType.LIGHT_ATTACK)

    # Check if ended
    if result['combat_ended']:
        print(f"Won: {result['player_won']}")
```

## Attack Types & Costs

| Attack | Stamina | Speed | Damage | Special |
|--------|---------|-------|--------|---------|
| Light | 15 | 1.2x | 1.0x | Fast, reliable |
| Heavy | 35 | 0.7x | 2.2x | Can cause bleed |
| Dodge | 20 | 1.5x | - | Evade next attack |
| Block | 10 | 1.3x | - | -60% damage |
| Parry | 25 | 1.4x | - | Counter-attack |

## Status Effects

| Effect | Duration | Potency | Type |
|--------|----------|---------|------|
| Bleed | 3 rounds | 5 dmg/round | DoT |
| Poison | 5 rounds | 7 dmg/round | DoT |
| Burn | 3 rounds | 6 dmg/round | DoT |
| Frost | 2 rounds | -speed | Debuff |
| Stun | 1 round | Skip turn | Control |
| Weakness | 4 rounds | -25% attack | Debuff |
| Strength | 3 rounds | +25% attack | Buff |
| Defense | 3 rounds | +25% defense | Buff |
| Regen | 5 rounds | 8 heal/round | HoT |

## Enemy Quick Reference

### Basic (10-30 souls)
- **Hollow Soldier** (Lv1): Balanced, weak to fire/holy
- **Corrupt Wolf** (Lv2): Aggressive, fast, bleed bite
- **Skeleton** (Lv3): Defensive, poison immune

### Elite (50-150 souls)
- **Dark Knight** (Lv5): Tactical, dark resistant
- **Frost Mage** (Lv6): Ranged, frost abilities

### Bosses (500+ souls)
- **Corrupted Guardian** (Lv8): Tank, regen
- **Lord of Cinders** (Lv10): Fire, phases
- **Shard Guardian** (Lv12): Magic, summons

## Class Abilities Cheat Sheet

### Warrior (Stamina)
| Ability | Cost | CD | Effect |
|---------|------|-----|--------|
| Whirlwind | 40 | 3 | AOE 25 dmg |
| Shield Bash | 30 | 2 | 20 dmg + stun |
| Battle Cry | 25 | 4 | +STR buff |
| Execute | 50 | 5 | 60 dmg finisher |

### Sorcerer (Mana)
| Ability | Cost | CD | Effect |
|---------|------|-----|--------|
| Fireball | 30 | 1 | 35 dmg + burn |
| Ice Storm | 50 | 4 | AOE 25 + frost |
| Mana Shield | 40 | 3 | +DEF buff |
| Lightning | 35 | 2 | 45 dmg |
| Arcane Regen | 45 | 5 | Heal over time |

### Rogue (Stamina)
| Ability | Cost | CD | Effect |
|---------|------|-----|--------|
| Backstab | 35 | 3 | 40 dmg crit |
| Poison Blade | 25 | 4 | 15 dmg + poison |
| Shadow Step | 30 | 3 | Dodge buff |
| Fan Knives | 45 | 4 | AOE bleed |

### Paladin (Mana)
| Ability | Cost | CD | Effect |
|---------|------|-----|--------|
| Divine Smite | 35 | 2 | 40 holy dmg |
| Lay Hands | 40 | 4 | 50 heal |
| Holy Shield | 30 | 5 | +DEF buff |
| Judgement | 60 | 5 | AOE holy |

### Necromancer (Mana)
| Ability | Cost | CD | Effect |
|---------|------|-----|--------|
| Death Bolt | 30 | 1 | 35 dark dmg |
| Life Drain | 40 | 3 | 30 dmg + 20 heal |
| Curse Weak | 35 | 4 | -ATK debuff |
| Dark Ritual | 30 HP | 3 | HP → Mana |
| Plague Cloud | 55 | 5 | AOE poison |

### Ranger (Stamina/Mana)
| Ability | Cost | CD | Effect |
|---------|------|-----|--------|
| Precise Shot | 25 | 2 | 35 dmg high crit |
| Multi-Shot | 40 | 3 | AOE 20 dmg |
| Hunter Mark | 20 | 4 | +DMG to target |
| Nature Bless | 35m | 4 | 40 heal + regen |
| Explosive | 50 | 5 | AOE burn |

## Stat Calculations

```python
# Stat Modifier
modifier = (stat_value - 10) // 2

# Combat Stats
attack_power = 10 + STR_mod + weapon_bonus
defense = 10 + DEX_mod + armor_bonus
accuracy = 60 + (DEX_mod * 3) + (STR_mod * 2)
evasion = 10 + (DEX_mod * 4)
critical_chance = 0.05 + (DEX_mod * 0.01)
initiative = 10 + DEX_mod

# Damage Calculation
base_damage = attacker.attack_power
modified_damage = base_damage * attack_multiplier
if critical:
    modified_damage *= critical_damage
final_damage = max(1, modified_damage - (defender.defense * 0.5))
if blocking:
    final_damage *= 0.4
```

## AI Behaviors

| Behavior | Pattern |
|----------|---------|
| Aggressive | 60% heavy, 30% light, 10% block |
| Defensive | 50% block/parry, 30% light, 20% heavy |
| Balanced | Even mix of all actions |
| Tactical | Adapts to health states |
| Berserker | 80% heavy attacks |
| Coward | Defensive when <50% HP |

## Damage Types & Resistances

- **Physical** - Melee/ranged attacks
- **Fire** - Burn effects
- **Frost** - Slow effects
- **Lightning** - High damage
- **Poison** - DoT effects
- **Dark** - Necromantic
- **Holy** - Paladin abilities

Resistance values:
- 0.0 = Immune
- 0.5 = Resistant (-50%)
- 1.0 = Normal
- 1.5 = Vulnerable (+50%)
- 2.0 = Weak (+100%)

## Common Code Patterns

### Using Abilities
```python
from combat import AbilityManager

ability_mgr = AbilityManager(character)
success, msg, effect = ability_mgr.use_ability("Fireball")
if success:
    print(f"Damage: {effect.damage}")
ability_mgr.tick_cooldowns()  # Each round
```

### Creating Custom Enemy
```python
enemy = EnemyFactory.create_enemy(
    "dark_knight",
    level_override=10
)
```

### Checking Combat Results
```python
result = combat.execute_round(action)
if result['combat_ended']:
    if result['player_won']:
        souls = result['souls_gained']
        xp = result['xp_gained']
```

### Getting Available Actions
```python
actions = combat.get_available_actions()
for action in actions:
    if action['can_use']:
        print(f"{action['action']}: {action['description']}")
```

## Tips & Tricks

### Combat Strategy
1. **Stamina Management**: Save 20+ for dodge in emergencies
2. **Heavy vs Light**: Heavy attack when enemy has low stamina
3. **Parrying**: High risk/reward, best vs predictable enemies
4. **Status Effects**: Bleed stacks, poison for long fights

### Boss Fights
1. Learn patterns (AI behavior)
2. Watch for phase transitions
3. Save abilities for enrage phase
4. Keep stamina for dodges

### Class Synergies
- **Warrior**: Tank, use Battle Cry before Execute
- **Sorcerer**: Mana Shield → Lightning Bolt combo
- **Rogue**: Poison → Backstab while they're weak
- **Paladin**: Holy Shield → Divine Smite
- **Necromancer**: Life Drain for sustain
- **Ranger**: Hunter's Mark → Precise Shot

### Resource Management
- Light attacks for stamina efficiency
- Dodge/Block rotate to manage stamina
- Use abilities early (cooldowns!)
- Save healing for <30% HP

## Error Handling

```python
try:
    result = combat.execute_round(action)
except Exception as e:
    logger.error(f"Combat error: {e}")
    # Handle gracefully
```

## Performance Tips

1. Disable LLM for testing: `use_llm=False`
2. Batch enemy creation for encounters
3. Reuse database sessions
4. Cache ability lookups

## Common Issues

| Issue | Solution |
|-------|----------|
| Not enough stamina | Use lighter attacks or block |
| Abilities not working | Check cooldowns and resources |
| Damage too low | Upgrade equipment, use buffs |
| Enemy too hard | Check level scaling, use strategy |

## File Locations

```
combat/
├── system.py        # Core combat engine
├── enemies.py       # Enemy definitions
├── abilities.py     # Class abilities
├── __init__.py      # Module exports
├── README.md        # Full documentation
├── ARCHITECTURE.md  # System design
└── QUICK_REFERENCE.md  # This file

examples/
└── combat_example.py  # Usage examples
```

## Version Info

- **Version**: 1.0
- **Date**: January 18, 2025
- **Lines of Code**: 3,269
- **Dependencies**: SQLAlchemy, database models, LLM generator

---

For full documentation, see `combat/README.md`
