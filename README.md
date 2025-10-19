# Shards of Eternity

> A Souls-like multiplayer RPG with LLM-powered storytelling, P2P networking, and reality-altering gameplay

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Textual](https://img.shields.io/badge/Textual-TUI-purple.svg)](https://textual.textualize.io/)

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Game Mechanics](#game-mechanics)
- [Admin Tools](#admin-tools)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

---

## About

**Shards of Eternity** is an ambitious text-based multiplayer RPG that combines Souls-like combat mechanics with procedurally-generated storytelling powered by Large Language Models (LLMs). Players compete for control of 12 legendary Crystal Shards that have the power to reshape reality itself.

When all 12 shards are claimed, the **Aetherfall** event occurs, resetting the world and reshaping reality based on which faction controls the most shards. Your choices, alliances, and combat prowess determine not just your fate, but the fate of the entire world.

### Key Highlights

- **Souls-like Combat**: Stamina-based turn-based combat with dodging, parrying, blocking, and critical hits
- **LLM Integration**: Dynamic storytelling, NPC dialogue, and event descriptions powered by OpenAI, Anthropic, or local LLMs
- **P2P Networking**: Decentralized multiplayer using encrypted peer-to-peer connections
- **Reality System**: World changes based on shard ownership - different factions create different realities
- **Rich Character System**: 6 races, 6 classes, detailed stats, inventory, and progression
- **Persistent World**: SQLAlchemy-based database tracking characters, locations, and world events

---

## Features

### Core Systems

- **Character Creation & Progression**
  - 6 playable races: Human, Elf, Dwarf, Tiefling, Dragonborn, Undead
  - 6 classes: Warrior, Sorcerer, Rogue, Paladin, Necromancer, Ranger
  - D&D-inspired stat system (STR, DEX, CON, INT, WIS, CHA)
  - Experience-based leveling with stat increases
  - Equipment system with weapons, armor, and consumables
  - Character memories tracking decisions and events

- **Souls-like Combat System**
  - Stamina-based combat mechanics
  - Multiple attack types: Light Attack, Heavy Attack, Block, Dodge, Parry
  - Hit/Miss/Critical/Dodge/Parry/Block results
  - Status effects: Bleed, Poison, Burn, Frost, Stun, Buffs
  - Initiative-based turn order
  - Armor and defense mitigation
  - Soul currency earned from victories

- **Crystal Shards & Factions**
  - 12 unique Crystal Shards with elemental affinities
  - Guardian bosses protecting each shard
  - 6 competing factions with unique philosophies
  - Faction-based victory conditions
  - Reality shifts when factions control shards

- **LLM-Powered Storytelling**
  - Dynamic location descriptions
  - Contextual NPC dialogue
  - Vivid combat narration
  - Event generation based on world state
  - Support for OpenAI, Anthropic, and local models
  - Graceful fallback to static text

- **P2P Multiplayer**
  - Master server for peer discovery
  - Encrypted P2P connections between clients
  - Party system for cooperative play
  - Shared world state synchronization
  - Up to 20 players per area

- **World & Reality System**
  - Dynamic world state tracking
  - Aetherfall events reshaping reality
  - Faction power influence
  - Location-based gameplay
  - World event logging

---

## Installation

### Requirements

- **Python**: 3.11 or higher
- **Operating System**: Windows, Linux, or macOS
- **Database**: SQLite (default) or PostgreSQL (optional)
- **Internet**: Required for LLM API calls (optional for local models)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/shards_of_eternity.git
cd shards_of_eternity
```

#### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Initialize the Database

```bash
python -m database.migrations
```

This creates the SQLite database and all necessary tables.

---

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```env
# ===========================
# LLM Configuration
# ===========================
LLM_ENABLED=true
LLM_PROVIDER=openai  # openai, anthropic, or local
LLM_MODEL=gpt-4-turbo-preview
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.8

# API Keys (choose based on provider)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Local LLM (if using local provider)
LLM_BASE_URL=http://localhost:11434

# ===========================
# Network Configuration
# ===========================
MASTER_SERVER_HOST=localhost
MASTER_SERVER_PORT=8888
MASTER_SERVER_URL=http://localhost:8888

P2P_PORT=9000
P2P_MAX_CONNECTIONS=10
P2P_ENCRYPTION=true

# ===========================
# Database Configuration
# ===========================
DATABASE_TYPE=sqlite
DATABASE_PATH=./shards_of_eternity.db

# For PostgreSQL (optional)
# DATABASE_TYPE=postgresql
# DATABASE_URL=postgresql://user:password@localhost/shards_db

# ===========================
# Game Configuration
# ===========================
MAX_PLAYERS_PER_AREA=20
AUTOSAVE_INTERVAL=300
WORLD_RESET_THRESHOLD=12
DEBUG_MODE=false

# ===========================
# Security & Admin
# ===========================
ADMIN_TOKEN=your_secure_admin_token_here
SESSION_SECRET=your_secure_session_secret_here

# ===========================
# Logging
# ===========================
LOG_LEVEL=INFO
LOG_FILE=./logs/shards.log
```

### Configuration Options Explained

| Setting | Description | Default |
|---------|-------------|---------|
| `LLM_ENABLED` | Enable/disable LLM text generation | `true` |
| `LLM_PROVIDER` | LLM provider (openai/anthropic/local) | `openai` |
| `LLM_MODEL` | Model identifier | `gpt-4-turbo-preview` |
| `DATABASE_TYPE` | Database type (sqlite/postgresql) | `sqlite` |
| `P2P_ENCRYPTION` | Enable P2P encryption | `true` |
| `WORLD_RESET_THRESHOLD` | Shards needed for Aetherfall | `12` |
| `ADMIN_TOKEN` | Admin authentication token | (change in production) |

---

## Quick Start

### Single-Player Mode

1. **Create a Character**

```bash
python -m admin.cli create-character
```

Follow the interactive prompts to create your character.

2. **Start the Game**

```bash
python main.py
```

This launches the Textual TUI interface for single-player exploration.

### Multiplayer Mode

#### Server Setup

1. **Start the Master Server**

```bash
python run_server.py
```

The server runs on `http://localhost:8888` by default.

Custom host/port:
```bash
python run_server.py --host 0.0.0.0 --port 9000
```

#### Client Setup

1. **Configure Client**

Update `.env` with the master server URL:
```env
MASTER_SERVER_URL=http://your_server_ip:8888
```

2. **Join the Game**

```bash
python main.py --multiplayer
```

#### Party Play

In-game commands:
- `/party create "Party Name"` - Create a party
- `/party invite PlayerName` - Invite a player
- `/party join PartyID` - Join a party
- `/party leave` - Leave your current party

---

## Game Mechanics

### Character System

#### Races & Modifiers

| Race | Stat Bonuses | Special Traits |
|------|--------------|----------------|
| **Human** | +1 all stats | Versatile and adaptable |
| **Elf** | +2 DEX, +1 INT, +1 WIS | Grace and magic affinity |
| **Dwarf** | +2 CON, +1 STR, +1 WIS | Sturdy and resilient |
| **Tiefling** | +2 CHA, +1 INT | Demonic heritage, persuasive |
| **Dragonborn** | +2 STR, +1 CHA | Dragon blood, imposing |
| **Undead** | +2 INT, -1 CON, -1 CHA | Immortal, feared by living |

#### Classes & Roles

| Class | Primary Stats | Starting Resources | Playstyle |
|-------|---------------|-------------------|-----------|
| **Warrior** | STR, CON | HP: 120, Stamina: 120, Mana: 50 | Frontline tank, heavy attacks |
| **Sorcerer** | INT, WIS | HP: 70, Stamina: 70, Mana: 150 | Magic damage, crowd control |
| **Rogue** | DEX, CHA | HP: 90, Stamina: 130, Mana: 60 | Quick strikes, stealth |
| **Paladin** | STR, CHA | HP: 110, Stamina: 100, Mana: 90 | Holy warrior, support |
| **Necromancer** | INT, CHA | HP: 80, Stamina: 80, Mana: 140 | Death magic, summoning |
| **Ranger** | DEX, WIS | HP: 95, Stamina: 110, Mana: 80 | Ranged combat, tracking |

### Combat System

#### Attack Types

- **Light Attack** (15 stamina): Fast, reliable damage with 1.1x accuracy
- **Heavy Attack** (35 stamina): 2.2x damage multiplier, may cause bleed
- **Block** (10 stamina): Reduce incoming damage by 60%
- **Dodge** (20 stamina): Chance to completely evade attacks
- **Parry** (25 stamina): Counter attack on successful timing

#### Combat Flow

1. **Initiative Roll** - Determines turn order (DEX + d20)
2. **Status Effects** - Bleed, poison, burn tick at round start
3. **Actions** - Both combatants execute chosen actions
4. **Resolution** - Calculate hit/miss, damage, status effects
5. **Stamina Regen** - +10 stamina per round
6. **Victory/Defeat** - Souls and XP awarded to winner

#### Status Effects

- **Bleed**: 5 damage per turn for 3 turns
- **Poison**: Damage over time
- **Burn**: Fire damage each turn
- **Frost**: Slows actions, reduces evasion
- **Stun**: Skip next turn
- **Weakness**: 25% attack reduction
- **Strength Buff**: 25% attack increase
- **Defense Buff**: 25% defense increase
- **Regeneration**: Heal each turn

### Crystal Shards

#### The 12 Shards

Each shard has unique properties:

1. **Phoenix Flame** (Fire) - Rebirth and destruction
2. **Tidecaller's Pearl** (Water) - Control over seas and storms
3. **Earthheart Stone** (Earth) - Connection to the land
4. **Stormcry Diamond** (Air) - Command of winds
5. **Dawnbringer** (Light) - Radiance and hope
6. **Nightfall** (Darkness) - Shadows and secrets
7. **Void Star** (Void) - Emptiness and annihilation
8. **Chronos Shard** (Time) - Temporal manipulation
9. **Infinity Prism** (Space) - Spatial control
10. **Lifeseed** (Life) - Growth and healing
11. **Reaper's Fragment** (Death) - Endings and decay
12. **Pandemonium** (Chaos) - Unpredictability and change

#### Capturing Shards

1. **Locate** - Find the shard's guardian location
2. **Battle** - Defeat the guardian boss (Souls-like difficulty)
3. **Claim** - Capture the shard for your faction
4. **Control** - Gain faction abilities and influence reality

### Factions

#### The Six Factions

1. **Crimson Covenant** - Blood magic and sacrifice
2. **Aether Seekers** - Knowledge and enlightenment
3. **Iron Brotherhood** - Strength and honor
4. **Moonlit Circle** - Nature and balance
5. **Shadowborn** - Darkness and subterfuge
6. **Golden Order** - Law and civilization

#### Victory Conditions

Each faction has unique victory conditions. When a faction controls all 12 shards:

- **Reality Reshaping** - World transforms based on faction philosophy
- **Aetherfall** - Current cycle ends, new cycle begins
- **Faction Bonuses** - Members gain permanent abilities
- **World Events** - Unique story events trigger

### Reality System

The world changes based on shard control:

- **Neutral** (0-3 shards claimed) - Normal world
- **Blood Realm** - Crimson Covenant dominance
- **Aether Storm** - Aether Seekers control
- **Iron Age** - Iron Brotherhood rule
- **Twilight Dominion** - Moonlit Circle supremacy
- **Shadow World** - Shadowborn influence
- **Radiant Era** - Golden Order ascendancy

Reality shifts affect:
- Environment descriptions
- NPC behavior
- Enemy types
- Available quests
- Weather and atmosphere

---

## Admin Tools

### Command-Line Interface

The admin CLI provides powerful tools for managing the game:

```bash
python -m admin.cli [command] [options]
```

#### Available Commands

**Character Management:**
```bash
# Create a new character
python -m admin.cli create-character

# List all characters
python -m admin.cli list-characters

# Delete a character
python -m admin.cli delete-character --id 1

# Give items to character
python -m admin.cli give-item --character-id 1 --item "Legendary Sword"
```

**World Management:**
```bash
# Initialize Crystal Shards
python -m admin.cli init-shards

# Trigger Aetherfall
python -m admin.cli trigger-aetherfall

# Reset world state
python -m admin.cli reset-world

# Set faction shard count
python -m admin.cli set-faction-shards --faction "Crimson Covenant" --count 5
```

**Database Operations:**
```bash
# Create database tables
python -m admin.cli init-db

# Backup database
python -m admin.cli backup-db

# View world stats
python -m admin.cli world-stats
```

