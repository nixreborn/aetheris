# Character System Quick Reference

## Quick Start

```python
from database import init_database
from database.models import RaceType, ClassType, FactionType
from characters import CharacterCreator, CharacterManager

# Initialize
init_database()
creator = CharacterCreator()
manager = CharacterManager()

# Create character
char = creator.create_character(
    name="Hero Name",
    race=RaceType.HUMAN,
    character_class=ClassType.WARRIOR,
    faction=FactionType.IRON_BROTHERHOOD
)
```

## Common Operations

### Character Creation
```python
# With rolled stats
char = creator.create_character(
    name="Name", race=RaceType.ELF,
    character_class=ClassType.SORCERER,
    faction=FactionType.AETHER_SEEKERS,
    stat_method="4d6_drop_lowest"  # or "3d6", "heroic"
)

# With custom stats (point-buy)
stats = {"strength": 10, "dexterity": 10, "constitution": 10,
         "intelligence": 15, "wisdom": 10, "charisma": 5}
char = creator.create_character(
    name="Name", race=RaceType.HUMAN,
    character_class=ClassType.WARRIOR,
    faction=FactionType.CRIMSON_COVENANT,
    stats=stats
)
```

### Load Character
```python
char = manager.load_character(character_id=1)
# or
char = manager.load_character(name="Hero Name")
```

### Update Resources
```python
# Damage
manager.update_health(char_id, -30)

# Heal
manager.update_health(char_id, 50)

# Use stamina
manager.update_stamina(char_id, -20)

# Use mana
manager.update_mana(char_id, -15)

# Rest
restored = manager.rest_character(char_id, full_rest=True)
```

### Inventory
```python
# Add item
item = manager.add_item_to_inventory(
    char_id, "Sword", "weapon",
    attack_bonus=10, value=100
)

# Equip item
manager.equip_item(char_id, item.id)

# Remove item
manager.remove_item_from_inventory(char_id, item.id, quantity=1)
```

### Experience & Leveling
```python
# Add XP
exp, leveled_up, level = manager.add_experience(char_id, 150)

if leveled_up:
    print(f"Level up to {level}!")
```

### Currency
```python
# Add souls
manager.add_souls(char_id, 100)

# Spend souls
manager.add_souls(char_id, -50)
```

### Memories
```python
# Add memory
manager.add_memory(
    char_id, "quest",
    "Quest Title", "Description",
    location_name="Location",
    souls_gained=50
)

# Get memories
memories = manager.get_character_memories(char_id, limit=10)
```

### Character Info
```python
# Full summary
summary = manager.get_character_summary(char_id)
print(summary['name'], summary['level'], summary['souls'])

# Derived stats
derived = manager.calculate_derived_stats(char)
print(f"AC: {derived['armor_class']}")
```

## Available Enums

### Races
- `RaceType.HUMAN`
- `RaceType.ELF`
- `RaceType.DWARF`
- `RaceType.TIEFLING`
- `RaceType.DRAGONBORN`
- `RaceType.UNDEAD`

### Classes
- `ClassType.WARRIOR`
- `ClassType.SORCERER`
- `ClassType.ROGUE`
- `ClassType.PALADIN`
- `ClassType.NECROMANCER`
- `ClassType.RANGER`

### Factions
- `FactionType.CRIMSON_COVENANT`
- `FactionType.AETHER_SEEKERS`
- `FactionType.IRON_BROTHERHOOD`
- `FactionType.MOONLIT_CIRCLE`
- `FactionType.SHADOWBORN`
- `FactionType.GOLDEN_ORDER`

## Character Stats

**Primary Attributes:**
- Strength (STR) - Physical power, melee damage
- Dexterity (DEX) - Agility, armor class, initiative
- Constitution (CON) - Health, stamina
- Intelligence (INT) - Magic power, mana
- Wisdom (WIS) - Perception, mana
- Charisma (CHA) - Social interactions, leadership

**Resources:**
- Health (HP) - Life points
- Stamina - Physical abilities
- Mana - Magical abilities
- Souls - Currency

## Error Handling
```python
from characters import CharacterCreationError, CharacterNotFoundError

try:
    char = creator.create_character(...)
except CharacterCreationError as e:
    print(f"Creation failed: {e}")

try:
    char = manager.load_character(char_id)
except CharacterNotFoundError as e:
    print(f"Not found: {e}")
```

## Level Requirements

| Level | XP Needed | Level | XP Needed |
|-------|-----------|-------|-----------|
| 2 | 100 | 11 | 5,500 |
| 3 | 300 | 12 | 6,600 |
| 4 | 600 | 13 | 7,800 |
| 5 | 1,000 | 14 | 9,100 |
| 6 | 1,500 | 15 | 10,500 |
| 7 | 2,100 | 20 | 19,000 |
| 8 | 2,800 | 25 | 30,000 |
| 9 | 3,600 | | |
| 10 | 4,500 | | |

## Tips

1. Always initialize database first: `init_database()`
2. Use `get_character_summary()` for complete character state
3. Memories auto-created for level ups, deaths, travel
4. Resources fully restored on level up
5. Equipment bonuses included in derived stats
6. Consumables stack automatically
7. Point-buy total must equal 60
8. Character names must be unique and 3-50 chars
