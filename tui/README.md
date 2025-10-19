# Shards of Eternity - Text-based User Interface (TUI)

A comprehensive terminal-based user interface for Shards of Eternity, built with the [Textual](https://textual.textualize.io/) framework.

## Features

### 1. Main Game Screen (`main_screen.py`)

The primary interface for gameplay with:

- **Header Panel**: Player stats with health, stamina, and mana bars
- **Left Panel**: Party members list with their status
- **Center Panel**: Main action area for exploration, combat, and dialogue
- **Right Panel**: Inventory and equipment management
- **Bottom Panel**: Dialogue log and command input
- **Navigation Menu**: Quick access to Travel, Inventory, Character, Party, Settings

**Key Bindings:**
- `t` - Travel/World Map
- `i` - Inventory
- `c` - Character Sheet
- `p` - Party Management
- `s` - Settings
- `q` - Quit Game

### 2. Character Screen (`character_screen.py`)

#### Character Creation Wizard
Step-by-step character creation process:

1. **Name Selection**: Enter your character's name (3-50 characters)
2. **Race Selection**: Choose from 6 races (Human, Elf, Dwarf, Tiefling, Dragonborn, Undead)
3. **Class Selection**: Choose from 6 classes (Warrior, Sorcerer, Rogue, Paladin, Necromancer, Ranger)
4. **Faction Selection**: Join one of 6 factions competing for the Crystal Shards
5. **Stat Allocation**: Distribute 60 points across 6 attributes (STR, DEX, CON, INT, WIS, CHA)
6. **Summary & Confirmation**: Review your choices before creating

#### Character Sheet Display
Detailed view of your character:

- **Header**: Name, level, race, class, faction, experience, souls
- **Attributes**: All 6 stats with modifiers displayed
- **Resources**: Health, stamina, and mana bars
- **Equipment**: Currently equipped weapons and armor
- **Derived Stats**: Armor class, initiative, attack/magic power, equipment bonuses

**Key Bindings:**
- `escape` - Return to previous screen

### 3. Combat Screen (`combat_screen.py`)

Turn-based combat interface featuring:

- **Enemy Display**: Shows each enemy with health bars and status effects
- **Player Status**: Your health, stamina, mana, and combat stats
- **Action Menu**:
  - **Attack**: Basic melee/ranged attack
  - **Abilities**: Special powers (stamina/mana cost)
  - **Items**: Use consumables (potions, scrolls)
  - **Dodge**: Prepare to evade incoming attacks
  - **Block**: Raise guard to reduce damage
  - **Flee**: Attempt to escape combat (50% success)
- **Combat Log**: Scrolling log of all combat actions and results
- **Turn Indicator**: Shows whose turn it is (player or enemy)

**Key Bindings:**
- `1` - Quick Attack
- `2` - Quick Ability
- `3` - Quick Item
- `d` - Dodge
- `b` - Block
- `f` / `escape` - Flee

**Combat Flow:**
1. Player selects an action
2. Action is executed with visual feedback
3. Enemy turn begins automatically
4. Combat continues until victory, defeat, or successful flee

### 4. World Screen (`world_screen.py`)

World exploration and travel interface:

- **Location Cards**: Detailed cards for each location showing:
  - Name and type (town, wilderness, dungeon, faction HQ)
  - Danger level (1-10)
  - Description and lore
  - Controlling faction (if any)
  - Safe zone status
  - Connected locations
  - Travel button (if not current location)

- **Crystal Shards Panel**:
  - Total shards (12)
  - Claimed vs unclaimed count
  - Faction distribution of captured shards

- **Reality State Panel**:
  - Current reality type (affects world behavior)
  - Reality stability meter (0-100%)
  - Aetherfall counter

- **Nearby Players Panel**:
  - Lists other players in the same location
  - Shows their level, race, class, and faction

- **World Map** (toggle view):
  - ASCII-art representation of the world
  - Shows major locations and your position

**Key Bindings:**
- `escape` - Return to previous screen
- `m` - Toggle between list and map view
- `s` - Focus on Shard information
- `r` - Focus on Reality state
- `p` - Focus on nearby Players

**Locations Include:**
- **Starting Town**: Safe zone for new players
- **Dark Forest**: Mid-danger wilderness area
- **Mountain Pass**: Treacherous high-altitude path
- **Cursed Ruins**: High-danger dungeon
- **Ember Volcano**: Shard guardian location (Phoenix Flame)
- **Celestial Cathedral**: Faction headquarters (Golden Order)

## Installation

1. Install Textual:
```bash
pip install textual
```

2. Install Rich (required by Textual):
```bash
pip install rich
```

## Usage

### Running the Demo Application

To see all TUI screens in action:

```bash
python -m tui.example_app
```

This launches a menu where you can navigate to any screen:
- Main Game Screen
- Character Creation
- Character Sheet
- Combat Screen
- World & Travel

### Integrating TUI into Your Game

```python
from textual.app import App
from tui import MainGameScreen, CharacterCreationScreen, CombatScreen, WorldScreen

class MyGameApp(App):
    def on_mount(self):
        # Start with character creation
        self.push_screen(CharacterCreationScreen(on_complete=self.start_game))

    def start_game(self, character_data):
        # Character created, show main screen
        self.push_screen(MainGameScreen(character_data))
```

### Using Individual Screens

#### Main Game Screen
```python
character_data = {
    "name": "Hero",
    "level": 5,
    "race": "Human",
    "class": "Warrior",
    "faction": "Crimson Covenant",
    "health": 100,
    "max_health": 120,
    "stamina": 100,
    "max_stamina": 120,
    "mana": 50,
    "max_mana": 50,
    "souls": 500
}

screen = MainGameScreen(character_data)
```

#### Character Creation
```python
def on_complete(character_data):
    print(f"Created: {character_data['name']}")

screen = CharacterCreationScreen(on_complete=on_complete)
```

#### Combat Screen
```python
character_data = {...}  # Your character stats

enemies = [
    {
        "name": "Goblin",
        "level": 3,
        "type": "Humanoid",
        "health": 30,
        "max_health": 30,
        "status_effects": []
    }
]

def on_combat_end(result):
    if result["player_victory"]:
        print("You won!")

screen = CombatScreen(character_data, enemies, on_combat_end)
```

#### World Screen
```python
def on_travel(location_name):
    print(f"Traveling to {location_name}")

screen = WorldScreen(
    current_location="Starting Town",
    on_travel=on_travel
)
```

## Customization

### Styling

Each screen has CSS styling defined in `DEFAULT_CSS` class attributes. You can override these:

```python
class CustomMainScreen(MainGameScreen):
    CSS = """
    PlayerStatsPanel {
        border: solid red;
        background: darkblue;
    }
    """
```

### Adding New Actions

Extend the action panels by adding buttons and handlers:

```python
class CustomActionPanel(ActionPanel):
    def compose(self):
        yield from super().compose()
        yield Button("Custom Action", id="custom-action")

    def on_button_pressed(self, event):
        if event.button.id == "custom-action":
            # Handle custom action
            pass
```

## Architecture

### Component Hierarchy

```
MainGameScreen
├── Header (Textual built-in)
├── PlayerStatsPanel
│   └── StatBar (x3: Health, Stamina, Mana)
├── Main Container (Horizontal)
│   ├── PartyPanel
│   ├── ActionPanel
│   └── InventoryPanel
├── DialoguePanel
│   ├── RichLog (combat/dialogue log)
│   └── Input (command input)
└── Footer (Textual built-in)
```

### Data Flow

1. **Screen Creation**: Pass data via constructor
2. **User Interaction**: Buttons, inputs trigger events
3. **Event Handlers**: `on_button_pressed`, `on_input_submitted`
4. **State Updates**: Update internal state and refresh widgets
5. **Callbacks**: Optional callbacks for parent app integration

## Best Practices

1. **Always provide character data**: Screens expect proper data structure
2. **Use callbacks**: For integration with game logic
3. **Handle screen stacking**: Use `push_screen()` and `pop_screen()`
4. **Update displays**: Call `update_*` methods when data changes
5. **Test with sample data**: Use the example_app.py as reference

## Dependencies

- **Textual**: Terminal UI framework
- **Rich**: Text formatting and display (required by Textual)
- **Python 3.8+**: Required for type hints and modern syntax

## Future Enhancements

Planned improvements:
- [ ] Drag-and-drop inventory management
- [ ] Animated combat sequences
- [ ] Real-time multiplayer chat
- [ ] Mini-map overlay
- [ ] Keybind customization screen
- [ ] Sound effects via terminal bell
- [ ] Achievement/quest tracker panel
- [ ] Faction reputation meters
- [ ] Skill tree visualization

## Contributing

When adding new TUI components:

1. Create widget in appropriate screen file
2. Add CSS styling in `DEFAULT_CSS`
3. Implement event handlers
4. Update `__init__.py` exports
5. Add example to `example_app.py`
6. Document in this README

## License

Part of the Shards of Eternity project.
