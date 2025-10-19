# Shards of Eternity - Quick Start Guide

## Getting Started in 5 Minutes

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py --help
```

### 2. First Run (Offline Mode)

```bash
# Start the game
python main.py
```

On first run, the game will:
- Create the database (`shards_of_eternity.db`)
- Seed 12 Crystal Shards
- Create initial locations (The Nexus, faction HQs, dungeons)
- Populate sample NPCs
- Initialize world state

### 3. Create Your Character

When the character selection screen appears:

1. Press `n` or click "New Character"
2. Follow the character creation wizard:
   - **Step 1**: Enter your character name
   - **Step 2**: Choose your race (affects stats)
   - **Step 3**: Select your class (determines abilities)
   - **Step 4**: Pick your faction (shapes your story)
   - **Step 5**: Allocate stats (60 points total)
   - **Step 6**: Confirm and create!

### 4. Explore the World

Once in-game, you'll see:
- **Top**: Your character stats (health, stamina, mana, souls)
- **Left**: Party members
- **Center**: Main action panel
- **Right**: Inventory and equipment
- **Bottom**: Dialogue log and input

#### Key Controls

- `t` - Travel to different locations
- `i` - View inventory
- `c` - Character sheet
- `p` - Party management
- `q` - Quit game
- `Ctrl+S` - Manual save
- Type commands in the input box at bottom

## Example Play Session

```
1. Start game: python main.py
2. Create character "Aldric" - Human Warrior - Crimson Covenant
3. Start in "The Nexus" (safe zone)
4. Press 't' to travel → Select "Ember Volcano"
5. Press "Explore" to search for the Phoenix Flame shard
6. Engage in combat with Fire Elementals
7. Find and battle Ignarok the Eternal (Guardian Boss)
8. Defeat guardian and claim the Phoenix Flame shard
9. Return to faction HQ to report success
```

## Command-Line Options

```bash
# Default: Offline single-player mode
python main.py

# Reset database (WARNING: Deletes all data!)
python main.py --reset-db

# Character creation wizard only
python main.py --create-character

# Run master server for multiplayer
python main.py --server

# Connect as multiplayer client
python main.py --client
```

## Understanding the Game

### The Crystal Shards

There are 12 legendary Crystal Shards:
1. Phoenix Flame (Fire)
2. Ocean's Tear (Water)
3. Mountain's Core (Earth)
4. Tempest Crown (Air)
5. Dawn's Radiance (Light)
6. Void Heart (Darkness)
7. Null Sphere (Void)
8. Hourglass Eternal (Time)
9. Infinity Prism (Space)
10. Genesis Seed (Life)
11. Reaper's Eye (Death)
12. Entropy Engine (Chaos)

Each shard:
- Is guarded by a level 50+ boss
- Grants powerful abilities to its owner
- Contributes to faction domination
- Affects world reality when controlled

### Factions

Choose one of six factions:

1. **Crimson Covenant** - Blood magic, primal power, life drain
2. **Aether Seekers** - Arcane knowledge, spell mastery, teleportation
3. **Iron Brotherhood** - Technology, mechanical might, automation
4. **Moonlit Circle** - Balance, twilight magic, shapeshifting
5. **Shadowborn** - Stealth, assassination, shadow manipulation
6. **Golden Order** - Divine power, healing, holy magic

### Combat Basics

Combat is turn-based with stamina management:

- **Light Attack** (15 stamina): Fast, accurate, low damage
- **Heavy Attack** (35 stamina): Slow, powerful, can be parried
- **Dodge** (20 stamina): Avoid enemy attacks
- **Block** (10 stamina): Reduce incoming damage
- **Parry** (25 stamina): Perfect timing = counter-attack
- **Abilities** (varies): Class and shard-specific powers

### Character Stats

- **STR** (Strength): Physical damage, carrying capacity
- **DEX** (Dexterity): Accuracy, evasion, initiative
- **CON** (Constitution): Health, stamina, survival
- **INT** (Intelligence): Magic power, spell slots
- **WIS** (Wisdom): Perception, willpower, mana
- **CHA** (Charisma): Persuasion, party buffs, prices

### Progression

- Kill enemies → Gain Souls + Experience
- Level up → Increase stats + Unlock abilities
- Find equipment → Improve attack/defense/magic
- Claim shards → Gain unique powers
- Join party → Complete harder content

## Tips for New Players

1. **Start in The Nexus**: It's a safe zone with NPCs and shops
2. **Don't rush bosses**: Level up in easier areas first
3. **Manage stamina**: Running out in combat = death
4. **Save often**: Press `Ctrl+S` or autosave every 5 minutes
5. **Join a faction**: Benefits and story progression
6. **Party up**: Some bosses require multiple players
7. **Explore everything**: Hidden items and secrets everywhere
8. **Read the lore**: NPCs have interesting stories and quests

## Troubleshooting

### Database Issues

```bash
# If database is corrupted
python main.py --reset-db

# Note: This deletes all characters and progress!
```

### Missing Dependencies

```bash
# Reinstall all requirements
pip install -r requirements.txt --force-reinstall
```

### LLM Not Working

Check your `.env` file:
```env
LLM_ENABLED=true
LLM_PROVIDER=openai
OPENAI_API_KEY=your_actual_api_key_here
```

If you don't have an API key:
```env
LLM_ENABLED=false
```

The game will work without LLM but with simpler text.

## Next Steps

- Read the full [README.md](README.md) for detailed mechanics
- Check [LORE.md](docs/LORE.md) for world background
- See [ADMIN.md](docs/ADMIN.md) for server administration
- Join multiplayer with `python main.py --client`

## Need Help?

- Check logs in `logs/shards.log`
- Review the codebase documentation
- File an issue on GitHub

Happy adventuring in the Shards of Eternity!
