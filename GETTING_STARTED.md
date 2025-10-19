# Getting Started with Shards of Eternity

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env to add your LLM API key (optional)
# LLM_ENABLED=true
# OPENAI_API_KEY=your_key_here
```

### 3. Run the Game
```bash
python main.py
```

This will:
- Create the database automatically
- Seed 12 Crystal Shards
- Create game locations
- Initialize world state
- Open the character selection screen

### 4. Create Your Character
Follow the in-game wizard to create your character:
- Choose a name
- Select race (6 options with stat bonuses)
- Select class (6 options with unique abilities)
- Choose faction (6 factions competing for shards)
- Allocate stat points
- Add optional description

### 5. Start Playing!
Explore the world, battle enemies, collect Crystal Shards, and compete with other factions!

---

## Game Modes

### Single-Player (Offline)
```bash
python main.py --offline
```
Play solo without networking.

### Multiplayer - Server
```bash
python run_server.py
# Or
python main.py --server
```
Runs the master server for multiplayer.

### Multiplayer - Client
```bash
python main.py --client
```
Connects to a master server.

---

## Key Controls

### Main Game
- `T` - Travel to new location
- `I` - Open inventory
- `C` - Character sheet
- `P` - Party management
- `Q` - Quit game
- `Ctrl+S` - Manual save

### Combat
- `1-3` - Quick attacks/actions
- `D` - Dodge
- `B` - Block
- `F` - Flee

---

## Admin Tools

Manage the game world:

```bash
# View all Crystal Shards
python -m admin.cli list-shards

# Trigger world reset (Aetherfall)
python -m admin.cli trigger-aetherfall

# View world events
python -m admin.cli world-events

# Backup database
python -m admin.cli backup-db

# See all commands
python -m admin.cli --help
```

---

## Game Mechanics Overview

### Crystal Shards
- 12 elemental shards scattered across the world
- Each protected by a guardian boss
- Factions compete to collect all 12
- Collecting all 12 triggers "The Aetherfall" (world reset)

### Factions
- 6 factions with unique philosophies
- Each faction wants to reshape reality
- Choose your allegiance at character creation
- Compete for shard control

### Combat
- Souls-like stamina-based system
- Every action costs stamina
- Attack types: Light, Heavy, Dodge, Block, Parry
- Status effects: Bleed, Poison, Burn, Frost, etc.
- Defeat enemies to gain souls (currency) and XP

### Character Progression
- 25 levels of progression
- Gain XP from combat
- Spend souls on items and upgrades
- Equip better weapons and armor
- Learn class-specific abilities

---

## Troubleshooting

### Database Errors
```bash
# Reset database
python main.py --reset-db
```

### LLM Not Working
- Check your API key in `.env`
- Set `LLM_ENABLED=true`
- Or disable LLM: `LLM_ENABLED=false`

### Multiplayer Connection Issues
- Ensure master server is running
- Check firewall settings
- Verify `MASTER_SERVER_HOST` and `MASTER_SERVER_PORT` in `.env`

---

## Next Steps

1. **Explore the world** - Visit different locations
2. **Join a party** - Team up with other players (multiplayer)
3. **Hunt for shards** - Defeat guardian bosses
4. **Level up** - Gain experience and become stronger
5. **Shape reality** - Help your faction trigger the Aetherfall

---

## Need Help?

- Check [README.md](README.md) for full documentation
- Review module READMEs in each directory
- Run examples in `examples/` directory
- Check the comprehensive docs in each module

**Enjoy your journey through the Shards of Eternity!**
