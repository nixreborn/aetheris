# Character System Documentation

## Overview

The character system provides comprehensive character creation and management functionality for Shards of Eternity. It includes two main classes:

- **CharacterCreator**: Handles character creation, validation, and stat generation
- **CharacterManager**: Manages character operations, progression, and inventory

## Features

### CharacterCreator

#### Character Creation
- Multiple stat rolling methods (3d6, 4d6 drop lowest, heroic)
- Point-buy system with validation
- Racial stat modifiers
- Class-based starting resources (health, stamina, mana)
- Class-specific starting equipment
- Automatic memory logging

#### Name Validation
- Length requirements (3-50 characters)
- Character restrictions (letters, spaces, hyphens, apostrophes)
- Uniqueness checking

### CharacterManager

#### Resource Management
- Update health, stamina, and mana
- Automatic death detection
- Rest system (full or partial)

#### Progression System
- Experience tracking
- Automatic level-up with stat increases
- Class-based stat growth
- Resource scaling per level

#### Inventory Management
- Add/remove items
- Item stacking for consumables
- Equipment system (weapons, armor)
- Item properties (attack/defense/magic bonuses)

#### Character Memories
- Event logging system
- Quest tracking
- Combat records
- Travel history
- Automatic important event recording

#### Derived Stats
- Stat modifiers (D&D-style)
- Armor class calculation
- Attack and magic power
- Initiative bonus
- Equipment bonuses

## Usage Examples

### Creating a Character

```python
from database import init_database
from database.models import RaceType, ClassType, FactionType
from characters import CharacterCreator

# Initialize database
init_database()

# Create character creator
creator = CharacterCreator()

# Create a character with rolled stats
character = creator.create_character(
    name="Thorgrim Ironheart",
    race=RaceType.DWARF,
    character_class=ClassType.WARRIOR,
    faction=FactionType.IRON_BROTHERHOOD,
    stat_method="4d6_drop_lowest"
)

print(f"Created {character.name}, Level {character.level}")
```

### Using Point-Buy Stats

```python
# Define custom stats (must total 60 points)
stats = {
    "strength": 8,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 16,
    "wisdom": 12,
    "charisma": 4
}

# Validate stats
is_valid, error, _ = creator.point_buy_stats(stats)
if is_valid:
    character = creator.create_character(
        name="Elara Moonwhisper",
        race=RaceType.ELF,
        character_class=ClassType.SORCERER,
        faction=FactionType.AETHER_SEEKERS,
        stats=stats
    )
```

### Managing Character Resources

```python
from characters import CharacterManager

manager = CharacterManager()

# Update health (damage)
new_health = manager.update_health(character.id, -30)

# Update stamina (use ability)
new_stamina = manager.update_stamina(character.id, -20)

# Update mana (cast spell)
new_mana = manager.update_mana(character.id, -15)

# Rest to recover
restored = manager.rest_character(character.id, full_rest=True)
print(f"Restored {restored['health_restored']} HP")
```

### Adding Experience and Leveling

```python
# Add experience
exp, leveled_up, new_level = manager.add_experience(character.id, 150)

if leveled_up:
    print(f"Level up! Now level {new_level}")
    # Character stats automatically increased
    # Resources fully restored on level up
```

### Inventory Management

```python
# Add an item
item = manager.add_item_to_inventory(
    character.id,
    item_name="Steel Greatsword",
    item_type="weapon",
    description="A massive two-handed sword",
    attack_bonus=20,
    value=150
)

# Add consumables (will stack if same type)
manager.add_item_to_inventory(
    character.id,
    item_name="Health Potion",
    item_type="consumable",
    quantity=5,
    value=20
)

# Equip an item
manager.equip_item(character.id, item.id)

# Remove an item
manager.remove_item_from_inventory(character.id, item.id, quantity=1)
```

### Character Memories

```python
# Add a memory
memory = manager.add_memory(
    character.id,
    memory_type="quest",
    title="The Lost Artifact",
    description="Discovered an ancient artifact in the ruins",
    location_name="Ancient Ruins",
    souls_gained=100,
    faction_impact="Iron Brotherhood"
)

# Get character memories
memories = manager.get_character_memories(character.id, limit=10)
for memory in memories:
    print(f"[{memory.memory_type}] {memory.title}: {memory.description}")

# Filter by type
combat_memories = manager.get_character_memories(
    character.id,
    memory_type="combat",
    limit=5
)
```

### Getting Character Summary

```python
# Get complete character information
summary = manager.get_character_summary(character.id)

print(f"Name: {summary['name']}")
print(f"Level: {summary['level']} ({summary['experience']} XP)")
print(f"Race: {summary['race']}, Class: {summary['class']}")
print(f"Faction: {summary['faction']}")
print(f"Stats: {summary['stats']}")
print(f"Resources: {summary['resources']}")
print(f"Souls: {summary['souls']}")
print(f"Derived Stats: {summary['derived_stats']}")
print(f"Equipped Items: {summary['equipped_items']}")
print(f"Inventory: {summary['inventory_items']}")
```

### Currency Management

```python
# Add souls (currency)
new_total = manager.add_souls(character.id, 100)
print(f"New soul total: {new_total}")

# Spend souls (negative amount)
manager.add_souls(character.id, -50)
```

### Location Management

```python
# Move character to new location
success = manager.change_location(character.id, location_id=5)
if success:
    print("Character moved successfully")
    # Automatically creates a travel memory
```

## Stat Rolling Methods

### 3d6 (Standard)
- Roll 3 six-sided dice for each stat
- Average stats, realistic difficulty

### 4d6 Drop Lowest (Recommended)
- Roll 4 six-sided dice, drop the lowest
- Higher average stats, more heroic characters

### Heroic
- Roll 4d6 drop lowest, but reroll any 1s as 2s
- Very high stats, for epic campaigns

## Racial Stat Modifiers

| Race | Modifiers |
|------|-----------|
| Human | +1 to all stats |
| Elf | +2 DEX, +1 INT, +1 WIS |
| Dwarf | +2 CON, +1 STR, +1 WIS |
| Tiefling | +1 INT, +2 CHA |
| Dragonborn | +2 STR, +1 CHA |
| Undead | +2 INT, -1 CON, -1 CHA |

## Class Starting Resources

| Class | Base HP | Base Stamina | Base Mana |
|-------|---------|--------------|-----------|
| Warrior | 120 | 120 | 50 |
| Sorcerer | 70 | 70 | 150 |
| Rogue | 90 | 130 | 60 |
| Paladin | 110 | 100 | 90 |
| Necromancer | 80 | 80 | 140 |
| Ranger | 95 | 110 | 80 |

Resources are modified by relevant stats (CON, INT, WIS).

## Level Progression

### Experience Requirements

| Level | Experience Required |
|-------|-------------------|
| 1 | 0 |
| 2 | 100 |
| 3 | 300 |
| 4 | 600 |
| 5 | 1,000 |
| 10 | 4,500 |
| 15 | 10,500 |
| 20 | 19,000 |
| 25 | 30,000 |

### Per-Level Gains
- Base health: +10 per level
- Base stamina: +8 per level
- Base mana: +12 per level
- Class-specific stat increases
- Full resource restoration on level up

## Error Handling

The system raises specific exceptions:

- **CharacterCreationError**: Failed to create character
  - Invalid name
  - Database errors
  - Constraint violations

- **CharacterNotFoundError**: Character not found in database
  - Invalid ID
  - Character was deleted

Example:
```python
from characters import CharacterCreationError, CharacterNotFoundError

try:
    character = creator.create_character(
        name="A",  # Too short!
        race=RaceType.HUMAN,
        character_class=ClassType.WARRIOR,
        faction=FactionType.CRIMSON_COVENANT
    )
except CharacterCreationError as e:
    print(f"Failed to create character: {e}")

try:
    character = manager.load_character(character_id=9999)
except CharacterNotFoundError as e:
    print(f"Character not found: {e}")
```

## Database Schema

The system uses SQLAlchemy ORM with the following models:

- **Character**: Main character data (stats, resources, progression)
- **InventoryItem**: Character inventory and equipment
- **CharacterMemory**: Event and decision log
- **Location**: World locations

See `database/models.py` for complete schema details.

## Best Practices

1. **Always initialize the database** before creating characters
2. **Use context managers** for database sessions (handled automatically)
3. **Validate character names** before creation
4. **Log important events** using the memory system
5. **Use character summary** for complete character state
6. **Handle exceptions** appropriately in your game logic

## Advanced Features

### Derived Stats Calculation

The system automatically calculates:
- Stat modifiers using D&D formula: `(stat - 10) / 2`
- Armor class: `10 + DEX modifier + equipment bonuses`
- Attack power: `STR modifier + weapon bonuses`
- Magic power: `INT modifier + magic item bonuses`
- Initiative: `DEX modifier`

### Starting Equipment by Class

Each class receives appropriate starting gear:
- **Warrior**: Sword, armor, health potions
- **Sorcerer**: Staff, robes, mana potions
- **Rogue**: Dagger, light armor, lockpicks
- **Paladin**: Blessed mace, chainmail, holy water
- **Necromancer**: Bone staff, dark robes, soul gem
- **Ranger**: Bow, leather armor, arrows

### Memory System

Memories track:
- Character creation
- Level ups
- Quest completion
- Combat encounters
- Travel between locations
- Deaths
- Custom events

Each memory includes:
- Type (quest, combat, dialogue, etc.)
- Title and description
- Location
- NPCs involved
- Faction impact
- Souls gained/lost
- Reputation changes
- Timestamp

## Performance Considerations

- Database sessions use context managers for automatic cleanup
- Inventory items stack to reduce database rows
- Character summaries include all data in single query
- Memories can be filtered and limited for performance

## Future Enhancements

Potential additions:
- Character skills and abilities system
- Quest tracking and completion
- Faction reputation system
- Character relationships
- Achievement system
- Character customization (appearance, background)
- Party system integration
- PvP combat tracking

## Example Script

See `examples/character_example.py` for a complete working example demonstrating all features.

Run with:
```bash
python examples/character_example.py
```
