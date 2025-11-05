# Aetheris MUD - Alpha Development Roadmap (v1.1)

**Project:** Aetheris - Shards of Eternity  
**Type:** AI-Powered Text-Based MUD (Multi-User Dungeon)  
**Tech Stack:** Python 3.11+, Textual TUI, Qwen3 LLM, SQLAlchemy, P2P Networking  
**Repository:** <https://github.com/nixreborn/aetheris>  
**Current Status:** Foundation Complete, Content Implementation Required  
**Target:** Feature-Complete Alpha Release

**Last Updated:** 2025-01-05  
**Version:** 1.1 - Alpha Roadmap (Revised)  
**Status:** Ready for Development

-----

## Table of Contents

1. [Alpha Goals & Scope](#alpha-goals--scope)
2. [Critical Alignment Tasks](#critical-alignment-tasks)
3. [Vertical Slice Prototype](#vertical-slice-prototype)
4. [Core Systems Implementation](#core-systems-implementation)
5. [Content Population](#content-population)
6. [LLM Integration](#llm-integration)
7. [Testing & Polish](#testing--polish)
8. [Success Metrics](#success-metrics)
9. [Post-Alpha Roadmap](#post-alpha-roadmap)

-----

## Alpha Goals & Scope

### What is Alpha?

A **playable, testable build** that demonstrates:

- Core gameplay loop (character creation → exploration → combat → progression)
- Faction/cult system working
- Party-based multiplayer (2-6 players)
- LLM-powered narrative consistency
- Aetherfall mechanics functional
- 50-100 hours of content for dedicated testers

### Who is Alpha For?

- **Internal testing team** (10-20 dedicated testers)
- **Lore enthusiasts** who will validate world consistency
- **Technical testers** for multiplayer stability
- **Balance testers** for combat and progression

### Alpha Does NOT Need:

- ❌ Full economy (basic vendor system is enough)
- ❌ All 50+ locations (prioritize starting zones + key faction hubs)
- ❌ All cult questlines (2-3 discoverable cults minimum)
- ❌ Endgame raid content (basic shard guardian encounters sufficient)
- ❌ Advanced crafting (save for beta)
- ❌ Housing system (save for beta)
- ❌ Seasonal events (save for beta)

-----

## Critical Alignment Tasks

### 🔴 PHASE 0: Lore-Code Synchronization (HIGHEST PRIORITY)

**Duration:** Week 1  
**Network Stability Milestone:** N/A (foundational work)

These discrepancies between the 'Aetheris - Lore.md' document and the codebase must be resolved FIRST.

#### Task 0.1: Rename Factions

**Current Code → Correct Name (from Lore)**

- `Crimson Covenant` → `The Crimson Legion`
- `Aether Seekers` → `The Arcane Consortium`
- `Iron Brotherhood` → DELETE (not in lore)
- `Moonlit Circle` → `The Wildborn Clans`
- `Shadowborn` → `The Shadow Pact`
- `Golden Order` → `The Celestial Order`

**Files to Update:**

- `/models/character.py` - FactionType enum
- `/models/faction.py` - Faction definitions
- `/database/migrations.py` - Database schema
- All references in combat, world, and LLM prompt files

**Database Migration Required:** YES

```python
# Create migration script: database/migrations/001_rename_factions.py
# Update all existing character faction assignments
# Update world state faction references
# CRITICAL: Include rollback script

def upgrade():
    # Rename faction types
    op.execute("""
        UPDATE characters 
        SET faction = 'CRIMSON_LEGION' 
        WHERE faction = 'CRIMSON_COVENANT'
    """)
    # ... etc for all factions

def downgrade():
    # Rollback changes
    op.execute("""
        UPDATE characters 
        SET faction = 'CRIMSON_COVENANT' 
        WHERE faction = 'CRIMSON_LEGION'
    """)
    # ... etc for all factions
```

-----

#### Task 0.2: Update Race List

**Remove:**

- Tiefling
- Dragonborn
- Undead

**Add:**

- Taur’n (Nomadic Guardians) - 7-9ft horned warriors
- Shadowkin (Masters of Stealth) - Forgotten ones, stealth specialists
- Orc (Warborn Berserkers) - Primal strength, rage mechanics
- Reptilian (Cold-Blooded Hunters) - Lizardfolk, swamp/desert survivors

**Keep:**

- Human (Versatile Survivors)
- Elf (Graceful Mystics)
- Dwarf (Stoneborn Warriors)

**Files to Update:**

- `/models/character.py` - RaceType enum
- `/character_creation/races.py` - Race stat bonuses and descriptions
- `/admin/cli.py` - Character creation flows

**Stat Bonuses from Lore:**

```python
RACE_STATS = {
    "TAURN": {"STR": +2, "CON": +2, "WIS": +1, "height_range": (7, 9)},
    "SHADOWKIN": {"DEX": +2, "CHA": +1, "stealth_bonus": +25},
    "HUMAN": {"all_stats": +1},
    "ORC": {"STR": +3, "CON": +2, "INT": -1, "rage_available": True},
    "REPTILIAN": {"CON": +2, "STR": +1, "environmental_resist": True},
    "ELF": {"DEX": +2, "INT": +1, "WIS": +1},
    "DWARF": {"CON": +2, "STR": +1, "WIS": +1}
}
```

-----

#### Task 0.3: Add Missing Classes

**Current:** Warrior, Sorcerer, Rogue, Paladin, Necromancer, Ranger

**Changes Required:**

- Rename `Sorcerer` → `Mage` (Arcane Scholar)
- Add `Spellblade` (Arcane Swordsman) - Hybrid melee/magic
- Add `Monk` (Way of the Fist) - Unarmed combat specialist
- Add `Shaman` (Spiritwalker) - Spirit summoner, elemental conduit

**Files to Update:**

- `/models/character.py` - ClassType enum
- `/combat/abilities.py` - New class abilities
- `/character_creation/classes.py` - Class descriptions and starting stats

**New Class Mechanics:**

```python
# Spellblade: Can enchant weapon with elemental damage, costs mana per hit
# Monk: Stamina regenerates faster, unarmed attacks scale with level
# Shaman: Can summon spirit guardians (AI-controlled allies), nature magic
```

-----

#### Task 0.4: Align Crystal Shard Names

**Decision:** Keep current names (Option A), document them in lore

**Action:** Update 'Aetheris - Lore.md' to include current shard names and assign 2 shards per faction:

- **Celestial Order:** Dawnbringer (Light) + Lifeseed (Life)
- **Crimson Legion:** Phoenix Flame (Fire) + Reaper’s Fragment (Death)
- **Arcane Consortium:** Chronos Shard (Time) + Infinity Prism (Space)
- **Shadow Pact:** Nightfall (Darkness) + Void Star (Void)
- **Wildborn Clans:** Earthheart Stone (Earth) + Tidecaller’s Pearl (Water)
- **Factionless:** Stormcry Diamond (Air) + Pandemonium (Chaos)

**Files to Update:**

- `/models/shard.py` - Assign faction_affinity to each shard
- 'Aetheris - Lore.md' lore document

-----

#### Task 0.5: Create Lore Lockfile (NEW)

**File:** `/data/lore_schema.json` (NEW)

Create a versioned JSON schema that enforces consistency between 'Aetheris - Lore.md' and codebase.

```json
{
  "version": "1.0.0",
  "last_updated": "2025-01-05",
  "factions": {
    "CELESTIAL_ORDER": {
      "display_name": "The Celestial Order",
      "philosophy": "Divine rule through absolute order",
      "reality_type": "RADIANT_ASCENDANCY",
      "stat_bonuses": {"healing_magic": 1.25}
    }
    // ... etc for all factions
  },
  "races": {
    "TAURN": {
      "display_name": "Taur'n",
      "description": "Nomadic Guardians",
      "height_range": [7, 9],
      "stat_bonuses": {"STR": 2, "CON": 2, "WIS": 1}
    }
    // ... etc for all races
  },
  "classes": {
    // ... all classes
  },
  "shards": {
    // ... all 12 shards with faction assignments
  }
}
```

**Validation Script:**

```python
# /tools/validate_lore.py (NEW)
# Run this before any commit to ensure consistency

def validate_lore_consistency():
    """
    Compare lore_schema.json against:
    - models/character.py enums
    - models/faction.py definitions
    - models/shard.py assignments
    
    Raise errors if mismatches found
    """
```

-----

## Vertical Slice Prototype

### 🟢 PHASE 0.5: Core Loop Validation (NEW)

**Duration:** Week 2  
**Network Stability Milestone:** Basic P2P connection (2 players, same zone, 30min session)

**Goal:** Prove the core gameplay loop works before investing in breadth.

#### Task 0.5.1: Minimal Playable Slice

**Scope:**

- 1 race (Human)
- 1 class (Warrior)
- 1 starting location (The Crossroads of Fate)
- 3 NPCs:
  - Quest Giver (“Wandering Seer”)
  - Vendor (“Traveling Merchant”)
  - Enemy (“Corrupted Scavenger” - level 1-3)
- 1 complete quest: “The First Test”
  - Objective: Kill 5 Corrupted Scavengers
  - Reward: Uncommon weapon, 100 XP, 50 souls
- Basic combat loop (attack, parry, dodge, stamina)
- LLM narration for:
  - Location entry
  - NPC dialogue
  - Combat actions
  - Quest completion

**Files to Create:**

```
/prototypes/
  ├── vertical_slice.py          # Main prototype runner
  ├── test_location.json         # Crossroads data
  ├── test_npcs.json             # 3 NPCs
  ├── test_quest.json            # First Test quest
  └── test_items.json            # Quest reward item
```

#### Task 0.5.2: LLM Integration Test

**File:** `/llm/prototype_prompts.py` (NEW)

Test that Qwen3 can generate acceptable narration with limited context:

```python
PROTOTYPE_SYSTEM_PROMPT = """
You are the narrator for Aetheris, a dark fantasy MUD. 
The player is a Human Warrior standing at The Crossroads of Fate.
Describe this moment in under 100 words, matching a Souls-like atmosphere.

Location: {location_description}
Action: {player_action}
"""

def test_llm_narration():
    # Test 10 common scenarios:
    # - Entering location
    # - Talking to quest giver
    # - Starting combat
    # - Winning combat
    # - Losing combat
    # - Completing quest
    # - Buying item
    # - Leveling up
    # - Dying
    # - Respawning
```

**Success Criteria:**

- [ ] LLM generates appropriate narration 8/10 times
- [ ] Fallback text is acceptable for failures
- [ ] Response time < 2 seconds per interaction

#### Task 0.5.3: Network Stability Baseline

**File:** `/networking/stress_test.py` (NEW)

Test P2P connection with 2 players:

```python
def test_basic_p2p():
    """
    - Player 1 hosts
    - Player 2 connects
    - Both move around same location
    - Both attack same enemy
    - Verify state sync
    - Measure latency
    - Test reconnect after disconnect
    """
```

**Success Criteria:**

- [ ] Connection establishes in < 5 seconds
- [ ] State syncs correctly 95%+ of time
- [ ] Latency < 100ms on local network
- [ ] Reconnect works after 30s disconnect

#### Task 0.5.4: Playtest & Iterate

**Internal Playtest:**

- 3-5 developers play the vertical slice
- Complete quest start to finish
- Test all combat actions
- Evaluate LLM narration quality
- Identify friction points

**Decision Point:**
If core loop feels good → Proceed to Phase 1  
If core loop has major issues → Iterate for 3 more days before proceeding

-----

## Core Systems Implementation

### 🟢 PHASE 1: Faction & Death Systems (Week 3-4)

**Network Stability Milestone:** 5 players, cross-faction party, 1 hour session, death/respawn tested

#### Task 1.1: Faction Membership Mechanics

**File:** `/systems/faction_system.py` (NEW)

```python
class FactionSystem:
    """
    Manages faction membership, reputation, oaths, and switching
    """
    
    def join_faction(character, faction_type):
        """
        - Set character.faction
        - Initialize reputation at 0 (Neutral)
        - Grant faction oath
        - Trigger oath ceremony (LLM-generated)
        - Apply faction bonuses
        """
        
    def leave_faction(character):
        """
        - Brand as "Oathbreaker" (7-day cooldown)
        - Remove faction bonuses
        - Set old faction rep to -500 (Hostile)
        - Strip faction-exclusive items
        """
        
    def check_oath_violation(character, action):
        """
        - Celestial Order: dark magic, murder innocents
        - Crimson Legion: fleeing combat, showing mercy
        - Shadow Pact: revealing secrets, working openly
        - Wildborn: using technology, entering cities
        - Arcane Consortium: destroying knowledge
        """
        
    def calculate_faction_bonuses(character):
        """
        Return stat modifiers based on faction:
        - Celestial Order: +25% healing magic
        - Crimson Legion: +15% melee damage
        - Arcane Consortium: +20% spell power
        - Shadow Pact: +30% crit damage
        - Wildborn Clans: +20% wilderness damage
        - Factionless: None (but can enter all zones)
        """
```

**Database Schema:**

```python
# Add to Character model
faction_reputation = Column(Integer, default=0)  # -1000 to 1000+
oath_broken_count = Column(Integer, default=0)
last_faction_switch = Column(DateTime, nullable=True)
is_oathbreaker = Column(Boolean, default=False)

# New table: FactionReputation
class FactionReputation(Base):
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'))
    faction_type = Column(Enum(FactionType))
    reputation = Column(Integer, default=0)
    rank = Column(String)  # Hated, Hostile, Neutral, Friendly, Honored, Exalted
```

**Commands:**

```
/faction info              - Show current faction, rep, bonuses
/faction join <name>       - Join a faction (if eligible)
/faction leave             - Leave faction (with warnings)
/faction reputation        - Show rep with all factions
```

-----

#### Task 1.2: Faction Reputation System

**File:** `/systems/reputation.py` (NEW)

```python
REPUTATION_LEVELS = {
    "HATED": (-1000, -500),      # Kill on sight
    "HOSTILE": (-500, -100),     # Aggressive NPCs
    "UNFRIENDLY": (-100, 0),     # No services
    "NEUTRAL": (0, 100),         # Basic access
    "FRIENDLY": (100, 500),      # Discounts, quests
    "HONORED": (500, 1000),      # Exclusive gear
    "EXALTED": (1000, 9999)      # Legendary rewards
}

class ReputationSystem:
    def gain_reputation(character, faction, amount, reason):
        """
        Sources:
        - Complete faction quest: +10 to +50
        - Kill rival faction player: +5
        - Donate resources: +1 to +10
        - Claim shard for faction: +100
        """
        
    def lose_reputation(character, faction, amount, reason):
        """
        Sources:
        - Attack faction member: -50
        - Fail faction quest: -10
        - Help rival faction: -25
        - Break oath: -100
        """
        
    def get_faction_rank(character, faction):
        """Returns string rank based on reputation value"""
        
    def check_npc_reaction(character, npc_faction):
        """
        Hated/Hostile: NPC attacks on sight
        Unfriendly: NPC refuses services
        Neutral+: Normal interactions
        """
```

-----

#### Task 1.3: Cross-Faction Party Rules

**File:** `/systems/party_system.py` (UPDATE EXISTING)

```python
# Faction compatibility matrix
FACTION_COMPATIBILITY = {
    ("CELESTIAL_ORDER", "SHADOW_PACT"): "FORBIDDEN",  # Cannot party
    ("CELESTIAL_ORDER", "NECROMANCER"): "FORBIDDEN",  # Class restriction
    ("CELESTIAL_ORDER", "CRIMSON_LEGION"): "UNEASY",  # -10 rep/hour
    ("CRIMSON_LEGION", "WILDBORN"): "NEUTRAL",
    # ... etc
}

def can_party_together(character1, character2):
    """
    Check if two characters can form a party:
    - Same faction: Always yes
    - Factionless: Can party with anyone
    - Rival factions: Check compatibility matrix
    - Enemy factions: Forbidden
    """
    
def apply_cross_faction_penalties(party):
    """
    If party has rival factions:
    - NPC aggro in faction territories
    - Rep loss over time
    - Quest restrictions
    """
```

-----

#### Task 1.4: Death & Respawn System (NEW)

**File:** `/systems/death_system.py` (NEW)

```python
class DeathSystem:
    """
    Souls-like death mechanics
    """
    
    def handle_player_death(character, killer=None):
        """
        On death:
        - Drop 50% of carried souls at death location
        - Create corpse marker (persistent for 30 minutes)
        - Reset to last bonfire/checkpoint
        - Apply death debuff (-10% stats for 5 minutes)
        - Increment death counter
        - Trigger LLM death narration
        """
        
    def create_soul_recovery_point(character, location, souls_amount):
        """
        Create recoverable soul marker:
        - Visible to character only
        - Glows to indicate location
        - If die again before recovery, lost forever
        - Other players cannot interact with it
        """
        
    def recover_souls(character, location):
        """
        On touching soul marker:
        - Restore lost souls
        - Remove death debuff
        - Trigger recovery narration
        """
        
    def calculate_death_penalty(character, death_count):
        """
        Repeated deaths increase penalty:
        - 1st death: -50% souls
        - 2nd death: -60% souls
        - 3rd+ death: -75% souls
        - Resets after 1 hour alive
        """
        
    def set_respawn_point(character, location_id):
        """
        Bonfire/checkpoint system:
        - Interact with bonfire to set respawn
        - Heal to full HP/MP on interaction
        - Save game state
        - Can teleport between discovered bonfires
        """
```

**Database Schema:**

```python
# Add to Character model
death_count = Column(Integer, default=0)
last_death_time = Column(DateTime, nullable=True)
respawn_location_id = Column(String, ForeignKey('locations.id'))
current_soul_marker_location = Column(String, nullable=True)
souls_at_death = Column(Integer, default=0)

# New table: Bonfires
class Bonfire(Base):
    id = Column(Integer, primary_key=True)
    location_id = Column(String, ForeignKey('locations.id'))
    name = Column(String)
    discovered_by = Column(JSON)  # List of character IDs
```

**Commands:**

```
/bonfire activate          - Set as respawn point
/bonfire list              - Show discovered bonfires
/bonfire travel <name>     - Teleport to bonfire (costs souls)
/recover                   - Pick up soul marker at current location
```

**LLM Prompts:**

```python
DEATH_NARRATION_PROMPT = """
The player {player_name} has died to {killer_name} at {location_name}.
Describe their death in 2-3 sentences, dramatic and visceral.
End with: "You awaken at the last bonfire..."
"""

SOUL_RECOVERY_PROMPT = """
The player recovers their lost souls. Describe the sensation of 
reclaiming what was lost, in 1-2 sentences.
"""
```

-----

#### Task 1.5: PvP Flagging System (NEW)

**File:** `/systems/pvp_system.py` (NEW)

```python
class PvPSystem:
    """
    Manages PvP rules and flagging
    """
    
    def get_pvp_status(character, target_character, location):
        """
        Determine if PvP is allowed:
        - PvP zones: Always allowed
        - Safe zones: Never allowed (faction hubs, starting zones)
        - Faction zones: Based on reputation
        - Same faction: Only if both opt-in OR one is Oathbreaker
        """
        
    def initiate_duel(character, target):
        """
        Formal duel request:
        - Both players must accept
        - Fight to first blood or death
        - Winner gets honor, loser loses nothing
        - No reputation loss
        """
        
    def flag_for_pvp(character, duration=1800):
        """
        Voluntary PvP flag:
        - Can attack and be attacked by anyone
        - Lasts 30 minutes or until death
        - Bonus: +20% XP/souls while flagged
        """
        
    def handle_faction_betrayal(attacker, victim):
        """
        If same-faction member attacks:
        - Check if Oathbreaker (allowed)
        - Check if victim is flagged (allowed)
        - Otherwise: Major reputation loss, potential exile
        """
        
    def calculate_pvp_rewards(winner, loser):
        """
        Winner gains:
        - 10% of loser's souls
        - Faction reputation (if rival factions)
        - PvP kill count increment
        
        Loser:
        - Normal death penalties apply
        - No additional penalty (already died)
        """
```

**Database Schema:**

```python
# Add to Character model
pvp_kills = Column(Integer, default=0)
pvp_deaths = Column(Integer, default=0)
is_pvp_flagged = Column(Boolean, default=False)
pvp_flag_expires_at = Column(DateTime, nullable=True)

# New table: DuelRecords
class DuelRecord(Base):
    id = Column(Integer, primary_key=True)
    challenger_id = Column(Integer, ForeignKey('characters.id'))
    opponent_id = Column(Integer, ForeignKey('characters.id'))
    winner_id = Column(Integer, ForeignKey('characters.id'))
    duel_date = Column(DateTime)
    location_id = Column(String)
```

**Commands:**

```
/duel <player>             - Challenge to formal duel
/duel accept               - Accept duel challenge
/duel decline              - Decline duel
/pvp flag                  - Voluntary PvP flag (30min)
/pvp unflag                - Remove flag early (5min cooldown)
/pvp status                - Show your PvP stats
```

-----

#### Task 1.6: Network Stability Testing (Week 4)

**File:** `/tests/network_stress_test.py` (UPDATE)

```python
def test_cross_faction_party():
    """
    5 players, mixed factions, 1 hour session:
    - Form party
    - Navigate multiple zones
    - Engage in combat
    - One player dies and respawns
    - Verify state sync across all clients
    """

def test_pvp_flagging():
    """
    2 players, same faction:
    - Player 1 flags for PvP
    - Player 2 attacks Player 1
    - Verify combat works
    - Player 1 dies
    - Verify death penalties apply
    - Player 1 recovers souls
    """

def test_packet_loss_handling():
    """
    Simulate 10% packet loss:
    - Verify game remains playable
    - Check for desync issues
    - Test reconnect logic
    """
```

-----

### 🟡 PHASE 2: Cult System (Week 5)

**Network Stability Milestone:** 10 players, multiple zones, 2 hour session

#### Task 2.1: Cult Discovery Mechanics

**File:** `/systems/cult_system.py` (NEW)

```python
class CultSystem:
    """
    8 secret cults, discovered through exploration and actions
    """
    
    def check_cult_discovery(character, location, action):
        """
        Trigger conditions for cult discovery:
        - Ashen Covenant: Find First Fire in Ashen Wastes
        - Black Sun: Meet blind prophet in twilight zone
        - Drowned Saints: Discover sunken altar
        - The Nameless: Read forbidden texts in Silent Archive
        - Silent Accord: Find evidence Aetherfall is artificial
        - Hollow Tribunal: 100 hours without crimes
        - Whispering Circle: Die 3 times, trigger prophetic dream
        - Crimson Pact: Complete assassination perfectly
        """
        
    def join_cult(character, cult_type):
        """
        - Check faction compatibility
        - Grant cult powers
        - Assign cult obligations
        - Start cult questline
        """
        
    def check_cult_obligations(character):
        """
        Monthly/weekly requirements:
        - Ashen Covenant: Sacrifice items to pyres
        - Black Sun: Convert others
        - Drowned Saints: Stay wet (must touch water daily)
        - Crimson Pact: Fulfill contracts
        """
```

**Database Schema:**

```python
class CultMembership(Base):
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'))
    cult_type = Column(Enum(CultType))
    join_date = Column(DateTime)
    cult_rank = Column(Integer, default=1)
    obligations_met = Column(Integer, default=0)
    powers_unlocked = Column(JSON)  # Track which abilities granted
    last_obligation_check = Column(DateTime)
```

**Cult Types Enum:**

```python
class CultType(str, Enum):
    ASHEN_COVENANT = "ashen_covenant"
    BLACK_SUN = "black_sun"
    DROWNED_SAINTS = "drowned_saints"
    THE_NAMELESS = "the_nameless"
    SILENT_ACCORD = "silent_accord"
    HOLLOW_TRIBUNAL = "hollow_tribunal"
    WHISPERING_CIRCLE = "whispering_circle"
    CRIMSON_PACT = "crimson_pact"
```

**Alpha Scope: Implement 3 cults fully:**

- Ashen Covenant (easiest to discover)
- Black Sun (medium difficulty)
- Crimson Pact (hardest, requires PvP)

-----

#### Task 2.2: Cult Powers & Penalties

**File:** `/systems/cult_powers.py` (NEW)

```python
CULT_POWERS = {
    "ASHEN_COVENANT": {
        "fire_immunity": True,
        "flame_weapon": {"damage_bonus": 1.3, "mana_cost": 10},
        "phoenix_rebirth": {"uses_per_day": 1, "hp_restore": 0.5}
    },
    "BLACK_SUN": {
        "darkvision": True,
        "shadow_magic_bonus": 1.25,
        "prophecy_vision": {"cooldown": 3600, "lore_reveal": True}
    },
    "CRIMSON_PACT": {
        "assassin_mark": {"crit_bonus": 0.5, "on_backstab": True},
        "blood_contract": {"damage_boost": 1.2, "costs_hp": True},
        "silent_kill": {"no_witnesses": True, "rep_protection": True}
    }
}

CULT_PENALTIES = {
    "ASHEN_COVENANT": {
        "visual_corruption": True,  # Character's eyes glow ember orange
        "fire_attracts_enemies": True,
        "humanity_drain": {"per_hour": 0.1}
    },
    "BLACK_SUN": {
        "light_sensitivity": {"damage_in_daylight": 1.1},
        "prophetic_madness": {"random_visions": True},
        "social_isolation": {"npc_distrust": True}
    },
    "CRIMSON_PACT": {
        "contract_obligation": {"must_accept_kills": True},
        "marked_by_death": {"visible_to_other_assassins": True},
        "no_mercy": {"cannot_spare_targets": True}
    }
}

def apply_cult_powers(character):
    """Add cult bonuses to character stats/abilities"""
    
def enforce_cult_penalties(character):
    """Apply ongoing penalties (visual changes, debuffs, etc.)"""
```

-----

### 🔵 PHASE 3: Quest System (Week 6)

**Network Stability Milestone:** 15 players, quest sharing in parties tested

#### Task 3.1: Quest Database Schema

**File:** `/models/quest.py` (NEW)

```python
class Quest(Base):
    __tablename__ = 'quests'
    
    id = Column(Integer, primary_key=True)
    quest_id = Column(String, unique=True)  # "celestial_order_001"
    title = Column(String)
    description = Column(Text)
    quest_type = Column(Enum(QuestType))  # MAIN, FACTION, CULT, SIDE, DAILY
    
    # Requirements
    required_faction = Column(Enum(FactionType), nullable=True)
    required_cult = Column(Enum(CultType), nullable=True)
    required_level = Column(Integer, default=1)
    required_reputation = Column(Integer, nullable=True)
    prerequisite_quests = Column(JSON)  # List of quest IDs
    
    # Objectives
    objectives = Column(JSON)  # List of objective dicts
    
    # Rewards
    xp_reward = Column(Integer)
    souls_reward = Column(Integer)
    reputation_rewards = Column(JSON)  # {faction: amount}
    item_rewards = Column(JSON)  # List of item IDs
    
    # State
    is_repeatable = Column(Boolean, default=False)
    cooldown_hours = Column(Integer, nullable=True)


class CharacterQuest(Base):
    __tablename__ = 'character_quests'
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'))
    quest_id = Column(String, ForeignKey('quests.quest_id'))
    
    status = Column(Enum(QuestStatus))  # AVAILABLE, ACTIVE, COMPLETED, FAILED
    objectives_progress = Column(JSON)  # Track each objective
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    can_repeat_at = Column(DateTime, nullable=True)
```

-----

#### Task 3.2: Create Starter Quests (15 Minimum - REDUCED)

**File:** `/data/quests/starter_quests.json` (NEW)

**Quest Distribution:**

- **Tutorial Quest:** 1 quest (all players, level 1)
- **Celestial Order:** 3 quests (levels 1-15)
- **Crimson Legion:** 3 quests (levels 1-15)
- **Arcane Consortium:** 3 quests (levels 1-15)
- **Shadow Pact:** 3 quests (levels 1-15)
- **Wildborn Clans:** 3 quests (levels 1-15)
- **Cult Discovery:** 2 quests (Ashen Covenant, Black Sun)

**Total: 17 quests**

**Quest Template:**

```json
{
  "quest_id": "celestial_order_001",
  "title": "Cleansing the Corrupted Shrine",
  "description": "Brother Malthus has asked you to purify the corrupted shrine in the Ashen Wastes. The darkness must be driven out.",
  "quest_type": "FACTION",
  "required_faction": "CELESTIAL_ORDER",
  "required_level": 3,
  "objectives": [
    {
      "type": "kill",
      "target": "corrupted_cultist",
      "count": 5,
      "current": 0
    },
    {
      "type": "interact",
      "target": "shrine_of_light",
      "location": "ashen_wastes"
    }
  ],
  "xp_reward": 500,
  "souls_reward": 100,
  "reputation_rewards": {
    "CELESTIAL_ORDER": 25
  },
  "item_rewards": ["holy_water", "blessed_bandage"]
}
```

**Quest Creation Priority:**

1. Tutorial quest (all factions) - “Awakening in the Broken World”
2. First faction quest for each faction (6 quests)
3. Mid-level faction quest for each faction (6 quests)
4. Cult discovery quests (2 quests - Ashen Covenant, Black Sun)
5. Crystal shard location hints (2 quests - embedded in faction quests)

-----

#### Task 3.3: Quest System Logic

**File:** `/systems/quest_system.py` (NEW)

```python
class QuestSystem:
    def get_available_quests(character):
        """
        Return quests character can accept:
        - Check faction/cult requirements
        - Check level requirements
        - Check reputation requirements
        - Check prerequisites completed
        - Exclude active/completed (non-repeatable)
        """
        
    def accept_quest(character, quest_id):
        """
        - Create CharacterQuest entry
        - Set status to ACTIVE
        - Initialize objectives_progress
        - Notify player
        """
        
    def update_quest_progress(character, action_type, target, location=None):
        """
        Called when character:
        - Kills enemy (check kill objectives)
        - Interacts with object (check interact objectives)
        - Enters location (check location objectives)
        - Collects item (check collection objectives)
        """
        
    def complete_quest(character, quest_id):
        """
        - Grant XP, souls, reputation
        - Grant items to inventory
        - Set status to COMPLETED
        - Check if unlocks new quests
        - Trigger LLM for completion narration
        """
        
    def abandon_quest(character, quest_id):
        """Allow players to drop active quests"""
        
    def share_quest_with_party(character, quest_id, party_id):
        """
        Party quest sharing:
        - All party members get quest (if eligible)
        - Progress shared in real-time
        - Rewards distributed on completion
        """
```

**Commands:**

```
/quest list                - Show available quests
/quest active              - Show active quests
/quest accept <id>         - Accept a quest
/quest progress            - Check objectives progress
/quest abandon <id>        - Abandon quest
/quest completed           - View completed quests
/quest share               - Share active quest with party
```

-----

### 🟠 PHASE 4: World Population (Week 7-8 - COMPRESSED)

**Network Stability Milestone:** 20 players, 5+ zones simultaneously, 3 hour session

**Goal:** Create 10 high-quality locations instead of 15 shallow ones

#### Task 4.1: Prioritize Starting Locations

**From Lore - Create These First:**

1. **The Bloodmarked Fields** (PvP/action starting zone)

- Description: Active battlefield, faction war
- NPCs: 3 faction recruiters, 1 war priest, 2 mercenaries
- Enemies: Rival faction soldiers (level 1-5)
- Objectives: First shard sighting, faction choice tutorial
- Bonfire: “Battlefield Shrine”

1. **The Hollow Refuge** (neutral/lore starting zone)

- Description: Forgotten settlement, safe zone
- NPCs: Blind seer, 2 factionless wanderers, 1 scholar
- Enemies: None (safe zone)
- Objectives: Lore discovery, cult hints, faction information
- Bonfire: “Refuge Hearth”

1. **The Crossroads of Fate** (exploration starting zone - ALREADY CREATED in Phase 0.5)

- Description: Mysterious waystone, travelers’ hub
- NPCs: 2 merchants, 6 faction representatives, 2 mysterious figures
- Enemies: Bandits on roads (level 1-5)
- Objectives: Choose your path, meet all factions
- Bonfire: “Waystone Fire”

**File:** `/data/locations/starting_zones.json` (NEW)

-----

#### Task 4.2: Create Faction Hub Locations

**One hub per faction (6 total):**

1. **Celestial Order - Sanctuary of the Last Light**

- Services: Healer, holy vendor, quest giver
- Safe zone for Order members only
- Aggressive to Shadow Pact members
- Bonfire: “Sacred Altar”

1. **Crimson Legion - The Warlord’s Rest**

- Services: Weapon vendor, arena master, quest giver
- Contains gladiator pit (PvP practice)
- Aggressive to Celestial Order if low rep
- Bonfire: “Victory Pyre”

1. **Arcane Consortium - The Nexus Outpost**

- Services: Spell vendor, researcher, quest giver
- Reality distortions (visual effects)
- Dangerous for non-mages (unstable magic)
- Bonfire: “Arcane Beacon”

1. **Shadow Pact - The Veiled Chamber**

- Services: Poison vendor, contract broker, quest giver
- Hidden (requires discovery to find)
- Entry requires Shadow Pact membership or invitation
- Bonfire: “Shadow Flame” (invisible to non-members)

1. **Wildborn Clans - The Wolf’s Den**

- Services: Nature vendor, beast tamer, quest giver
- No technology allowed (weapons degrade faster)
- Aggressive to city dwellers
- Bonfire: “Primal Hearth”

1. **Factionless Hub - The Hollow Refuge** (reuse starting zone)

- Services: General merchant, information broker
- Neutral ground for all factions
- No faction bonuses apply here
- Bonfire: “Refuge Hearth”

**File:** `/data/locations/faction_hubs.json` (NEW)

-----

#### Task 4.3: Create Key Exploration Locations (10 Total - REDUCED from 15)

**From the Broken World (default reality):**

1. **Ashen Spire** (ruined capital) - Level 5-10

- Contains: Mini-dungeon (1-3 players)
- Bonfire: “Spire Summit”

1. **The Scar** (endless battlefield) - Level 10-15

- Contains: PvP zone
- Bonfire: “Trench Fire”

1. **Blackveil Fortress** (haunted keep) - Level 8-12

- Contains: Mini-dungeon (2-4 players)
- Bonfire: “Courtyard Brazier”

1. **The Sunken Archive** (lost library) - Level 12-16

- Contains: The Nameless cult discovery (not in alpha)
- Bonfire: “Forgotten Lantern”

**Cult Discovery Locations:**
5. **Ashen Wastes** (Ashen Covenant) - Level 12+

- Contains: First Fire location
- Bonfire: “Ember Shrine”

1. **Twilight Reaches** (Black Sun) - Level 10+

- Contains: Blind prophet NPC
- Bonfire: “Eclipse Monument”

**Crystal Shard Locations (3 accessible in alpha - REDUCED from 4):**
7. **Phoenix Flame Guardian Lair** - Level 20+

- Boss: Ember Wyrm (party of 4-6)
- No bonfire (must survive to exit)

1. **Tidecaller’s Pearl Shrine** - Level 20+

- Boss: Leviathan’s Echo (party of 4-6)
- No bonfire (must survive to exit)

1. **Earthheart Stone Cavern** - Level 20+

- Boss: Stone Titan (party of 4-6)
- No bonfire (must survive to exit)

**Transition Zone:**
10. **The Rift** (reality-warping abyss) - Level 15-20

- Contains: Glimpses of alternate realities
- Leads to shard locations
- Bonfire: “Rift Edge”

**File:** `/data/locations/world_locations.json` (NEW)

-----

#### Task 4.4: Populate NPCs (REDUCED SCOPE)

**File:** `/data/npcs/world_npcs.json` (NEW)

**NPC Categories:**

1. **Faction Quest Givers** (6 - one per faction)
2. **Vendors** (10 - mix of general/faction-specific)
3. **Cult Representatives** (3 - Ashen Covenant, Black Sun, Crimson Pact)
4. **Named Characters from Lore** (Priority 3 for alpha):

- Varik “The Bloodforged” (Crimson Pact - assassin trainer)
- Father Iskar “The Tidecaller” (Drowned Saints - not in alpha, just lore reference)
- Azhir “The Blind Seer” (Black Sun - cult discovery NPC)

**Total NPCs: ~20 (down from original estimate)**

**NPC Template:**

```json
{
  "npc_id": "varik_bloodforged",
  "name": "Varik 'The Bloodforged'",
  "title": "Champion of the Crimson Pact",
  "faction": "CRIMSON_PACT",
  "cult": "CRIMSON_PACT",
  "location": "the_veiled_chamber",
  "level": 25,
  "is_hostile": false,
  "dialogue_triggers": {
    "first_meeting": "You approach a scarred warrior...",
    "faction_member": "Brother in blood. What do you seek?",
    "rival_faction": "You dare approach me? Bold... or foolish."
  },
  "services": ["cult_recruiter", "assassin_trainer"],
  "sells_items": [],
  "biography": "A living legend among the Crimson Pact...",
  "personality_matrix": {
    "aggression": 8,
    "honor": 7,
    "trust": 3,
    "humor": 2
  }
}
```

-----

### 🟠 PHASE 5: Economy Basics (Week 9 - PARALLEL WITH PHASE 4)

**Network Stability Milestone:** Economy sync tested (20 players, vendor transactions)

#### Task 5.1: Create Item Database (REDUCED SCOPE)

**File:** `/data/items/weapons.json` (NEW)
**File:** `/data/items/armor.json` (NEW)
**File:** `/data/items/consumables.json` (NEW)

**Minimum Items for Alpha:**

- **Weapons:** 12 (2 per weapon type: sword, axe, dagger, staff, bow, unarmed)
- **Armor:** 10 (2 per slot: head, chest, legs, hands, feet)
- **Consumables:** 8 (health potions, stamina potions, buffs, debuffs)

**Total: 30 items (down from 40)**

**Item Tiers:**

- Common (white) - Starting gear
- Uncommon (green) - Level 5-10
- Rare (blue) - Level 10-15
- Epic (purple) - Level 15-20
- Legendary (orange) - Level 20+ / Quest rewards

**Item Template:**

```json
{
  "item_id": "crimson_blade",
  "name": "Crimson Blade",
  "type": "WEAPON",
  "weapon_type": "SWORD",
  "rarity": "RARE",
  "level_requirement": 10,
  "stats": {
    "damage": 45,
    "attack_speed": 1.2,
    "crit_chance": 0.05
  },
  "faction_requirement": "CRIMSON_LEGION",
  "price": 500,
  "sell_price": 250,
  "description": "A blade forged in the fires of endless war.",
  "lore": "This weapon was carried by a champion who fell defending the Warlord's Rest."
}
```

-----

#### Task 5.2: Vendor System

**File:** `/systems/vendor_system.py` (NEW)

```python
class VendorSystem:
    def get_vendor_inventory(vendor_id, character):
        """
        Return items available for purchase:
        - Check faction reputation (locked items)
        - Check character level
        - Apply reputation discounts
        """
        
    def buy_item(character, vendor_id, item_id, quantity=1):
        """
        - Check character has enough souls
        - Deduct souls
        - Add item to inventory
        - Track purchase (for reputation gain)
        - Sync to all party members (inventory update)
        """
        
    def sell_item(character, vendor_id, item_id, quantity=1):
        """
        - Remove item from inventory
        - Calculate sell price (50% of buy price)
        - Add souls to character
        """
        
    def repair_equipment(character, vendor_id):
        """
        - Calculate total repair cost
        - Restore all equipment durability
        - Deduct souls
        """
```

**Commands:**

```
/vendor list              - Show vendor inventory
/vendor buy <item> [qty]  - Purchase item
/vendor sell <item> [qty] - Sell item
/vendor repair            - Repair all equipment
```

-----

#### Task 5.3: Loot Drop System

**File:** `/systems/loot_system.py` (NEW)

```python
class LootSystem:
    def generate_loot(enemy_type, enemy_level, killer_character):
        """
        Generate loot drops:
        - Souls (always) = enemy_level * 10 * (1 + luck_modifier)
        - Items (chance):
          * Common: 30% chance
          * Uncommon: 10% chance
          * Rare: 3% chance
          * Epic: 0.5% chance
        - Faction-specific items (if enemy is faction member)
        """
        
    def apply_party_loot_rules(party, loot_items):
        """
        Distribute loot based on party settings:
        - ROUND_ROBIN: Take turns
        - NEED_GREED: Roll system
        - LEADER_LOOT: Leader decides
        - FREE_FOR_ALL: First to grab
        """
```

-----

### 🔴 PHASE 6: LLM Integration (Week 10-12 - EXTENDED)

**Network Stability Milestone:** LLM load tested (20 players requesting narration simultaneously)

#### Task 6.1: Context Management System

**File:** `/llm/context_manager.py` (NEW)

```python
class ContextManager:
    """
    Manages what lore/state to inject into Qwen3 prompts
    Token budget: 2000 tokens per interaction
    """
    
    def build_system_prompt(world_state, character):
        """
        Base prompt that sets the stage (500 tokens):
        - Current reality (default, or faction-controlled)
        - Dominant faction
        - Crystal shards claimed
        - Character context (name, race, class, faction)
        """
        
    def inject_location_lore(location_id):
        """
        Pull location description from 'Aetheris - Lore.md' (400 tokens):
        - Detailed description
        - Current state (based on reality)
        - NPCs present
        - Danger level
        """
        
    def inject_npc_personality(npc_id):
        """
        Pull NPC bio from lore (300 tokens):
        - Character description
        - Speech patterns
        - Faction allegiance
        - Recent interactions with player
        - Personality matrix values
        """
        
    def inject_relevant_secrets(character_knowledge):
        """
        Based on what player has discovered (300 tokens):
        - Mythos entries unlocked
        - Cult knowledge
        - Faction secrets
        """
        
    def inject_conversation_history(character_id, npc_id):
        """
        Last 3 interactions with this NPC (500 tokens):
        - Previous dialogue
        - Relationship changes
        - Ongoing questlines
        """
```

**Token Budget Management:**

```python
# Qwen3 context window is limited
# Prioritize:
# 1. System prompt (current state) - 500 tokens
# 2. Character immediate context - 300 tokens
# 3. Location description - 400 tokens
# 4. NPC personality (if talking) - 300 tokens
# 5. Recent conversation history - 500 tokens
# TOTAL: ~2000 tokens (safe for most Qwen3 models)
```

-----

#### Task 6.2: LLM Prompt Templates (Week 10)

**File:** `/llm/prompts.py` (UPDATE)

```python
SYSTEM_PROMPT_TEMPLATE = """
You are the narrator for Aetheris, a dark fantasy MUD where reality resets in an endless cycle called the Aetherfall. You describe actions, locations, NPCs, and combat in vivid detail matching a Souls-like atmosphere.

CURRENT WORLD STATE:
- Reality: {current_reality}
- Dominant Faction: {dominant_faction}
- Crystal Shards Claimed: {shard_count}/12
- Date: {in_game_date}

PLAYER CHARACTER:
- Name: {player_name}
- Race: {player_race} (Level {player_level})
- Class: {player_class}
- Faction: {player_faction}
- Location: {current_location}

TONE & STYLE:
- Dark, atmospheric, foreboding
- Show, don't tell (vivid sensory details)
- Keep responses under 150 words
- Never break character or reference game mechanics directly
- Maintain consistency with established lore

CURRENT SCENE:
{location_description}

{npc_context}

{player_action}
"""

LOCATION_ENTRY_PROMPT = """
The player enters {location_name}. Describe what they see, hear, smell, and feel. Make it atmospheric and immersive. Hint at dangers or secrets without being obvious.

Location Context:
{location_lore}

Current State: {location_state}
Danger Level: {danger_level}
NPCs Present: {npc_list}
"""

NPC_DIALOGUE_PROMPT = """
The player speaks to {npc_name}. Respond in character.

NPC Context:
{npc_bio}
Faction: {npc_faction}
Personality: Aggression {aggression}/10, Honor {honor}/10, Trust {trust}/10, Humor {humor}/10
Current Mood: {npc_mood}
Player Reputation: {player_rep_with_npc_faction}
Conversation History:
{recent_dialogue}

Player said: "{player_message}"

Respond as {npc_name} would, staying true to their personality and faction allegiance. Keep response under 100 words.
"""

COMBAT_NARRATION_PROMPT = """
Describe this combat action dramatically:

Attacker: {attacker_name} ({attacker_class})
Defender: {defender_name} ({defender_class})
Action: {action_type}
Result: {result} ({damage} damage)
Status Effects: {status_effects}

Make it visceral and exciting. 2-3 sentences maximum.
"""

DEATH_NARRATION_PROMPT = """
The player {player_name} has died to {killer_name} at {location_name}.
Describe their death in 2-3 sentences, dramatic and visceral.
End with: "You awaken at the last bonfire..."
"""

SOUL_RECOVERY_PROMPT = """
The player recovers their lost souls at {location_name}. 
Describe the sensation of reclaiming what was lost, in 1-2 sentences.
Focus on the feeling of power returning.
"""

QUEST_COMPLETION_PROMPT = """
The player has completed the quest: {quest_title}
Quest Description: {quest_description}

Describe the moment of completion in 2-3 sentences.
Make it feel rewarding and significant.
"""

CULT_DISCOVERY_PROMPT = """
The player has discovered {cult_name}.
Cult Description: {cult_description}

Describe the moment of discovery in 3-4 sentences.
Make it ominous and mysterious. End with a question or choice.
"""
```

-----

#### Task 6.3: Integrate 'Aetheris - Lore.md' as Knowledge Base (Week 11)

**File:** `/llm/lore_loader.py` (NEW)

```python
import json
from pathlib import Path

class LoreDatabase:
    """
    Load and index 'Aetheris - Lore.md' content for quick retrieval
    """
    
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.factions = {}
        self.cults = {}
        self.mythos = {}
        self.cache = {}  # Cache frequent queries
        
    def load_from_rtf(self, filepath="/mnt/project/Aetheris - Lore.md"):
        """
        Parse RTF (convert to text first) and extract sections:
        - Locations (by keys)
        - Characters (by keys)
        - Factions (by keys)
        - Cults (by keys)
        - Mythos (forbidden knowledge)
        
        Store in structured JSON for fast lookups
        """
        
    def get_location_lore(self, location_id):
        """
        Return detailed description for LLM context
        Check cache first, then load from disk
        """
        if location_id in self.cache:
            return self.cache[location_id]
        
        lore = self._load_location(location_id)
        self.cache[location_id] = lore
        return lore
        
    def get_npc_bio(self, npc_id):
        """Return character bio for dialogue generation"""
        
    def get_faction_philosophy(self, faction_type):
        """Return faction's goals and methods"""
        
    def search_mythos(self, keywords):
        """Search for relevant forbidden knowledge"""
        
    def get_cult_lore(self, cult_type):
        """Return cult description and requirements"""
        
    def clear_cache(self):
        """Clear cache to free memory (call periodically)"""
```

**Pre-Processing Script:**

```python
# /tools/preprocess_lore.py (NEW)
# Run once during build to convert RTF to JSON

import rtfparse  # or use pandoc

def convert_rtf_to_json():
    """
    1. Parse 'Aetheris - Lore.md'
    2. Extract sections by markdown headers
    3. Index by keys (location names, NPC names, etc.)
    4. Save as /data/lore_database.json
    5. Create search index for fast keyword lookups
    """
```

-----

#### Task 6.4: Response Caching System (Week 11)

**File:** `/llm/response_cache.py` (NEW)

```python
class ResponseCache:
    """
    Cache LLM responses to reduce API calls and latency
    """
    
    def __init__(self):
        self.cache = {}
        self.max_cache_size = 1000
        
    def get_cache_key(self, prompt_type, context_hash):
        """
        Generate cache key from:
        - Prompt type (location_entry, npc_dialogue, etc.)
        - Context hash (location_id + player_faction + etc.)
        """
        
    def get_cached_response(self, prompt_type, context):
        """
        Check if we have a cached response for this context
        Return None if not found
        """
        
    def cache_response(self, prompt_type, context, response):
        """
        Store LLM response in cache
        Implement LRU eviction if cache full
        """
        
    def invalidate_cache(self, location_id=None, npc_id=None):
        """
        Clear cache entries when world state changes
        (e.g., after Aetherfall, NPC moves, etc.)
        """
```

**Pre-Generate Common Responses:**

```python
# /tools/pregenerating_narration.py (NEW)
# Run during build to generate common scenarios

COMMON_SCENARIOS = [
    ("location_entry", "bloodmarked_fields", "NEUTRAL"),
    ("location_entry", "hollow_refuge", "NEUTRAL"),
    ("npc_dialogue", "blind_seer", "greeting"),
    ("combat_narration", "slash", "hit", "medium_damage"),
    # ... 100+ common scenarios
]

def pregenerate_responses():
    """
    For each common scenario:
    1. Build prompt
    2. Call LLM
    3. Cache response
    4. Save to disk (/data/pregnenerated_narration.json)
    """
```

-----

#### Task 6.5: Fallback Text System (Week 12)

**File:** `/llm/fallbacks.py` (UPDATE EXISTING)

Ensure graceful degradation if LLM fails:

```python
FALLBACK_NARRATION = {
    "location_entry": {
        "bloodmarked_fields": "You step onto the Bloodmarked Fields, where the scent of iron hangs heavy in the air. Broken weapons litter the ground, and distant war cries echo across the plain.",
        "hollow_refuge": "The Hollow Refuge welcomes you with eerie silence. Crumbling buildings lean against each other, and a few wanderers move through the shadows.",
        # ... etc for all 10 locations
    },
    
    "npc_dialogue": {
        "default_greeting": "{npc_name} looks at you with {emotion}. 'What do you seek here, traveler?'",
        "faction_member": "{npc_name} nods in recognition. 'A fellow {faction} member. How can I assist you?'",
        "hostile": "{npc_name} glares at you with suspicion. 'State your business quickly, before I lose my patience.'",
    },
    
    "combat_narration": {
        "hit": "Your {attack_type} connects, dealing {damage} damage to {target}.",
        "miss": "Your {attack_type} misses {target} by inches.",
        "critical": "A devastating blow! Your {attack_type} strikes true, dealing {damage} critical damage!",
        "death": "{target} falls to the ground, defeated.",
    },
    
    "quest_events": {
        "accepted": "You have accepted the quest: {quest_title}",
        "completed": "Quest completed: {quest_title}. You have been rewarded.",
        "failed": "You have failed the quest: {quest_title}",
    }
}

def get_fallback_text(category, key, **kwargs):
    """
    Retrieve fallback text and format with provided variables
    Always return valid text (never fail)
    """
```

-----

#### Task 6.6: LLM Load Testing (Week 12)

**File:** `/tests/llm_stress_test.py` (NEW)

```python
def test_concurrent_narration_requests():
    """
    Simulate 20 players requesting narration simultaneously:
    - Location entries
    - NPC dialogue
    - Combat narration
    - Quest completions
    
    Verify:
    - No request takes >5 seconds
    - Cache hit rate >50% after warmup
    - Fallback triggers when LLM times out
    - No responses are gibberish
    """

def test_narrative_consistency():
    """
    Same player enters same location 10 times
    Verify narration maintains:
    - Consistent tone
    - Consistent details (no contradictions)
    - Appropriate variation (not identical)
    """

def test_llm_failure_handling():
    """
    Force LLM failures:
    - Network timeout
    - API rate limit
    - Invalid response
    
    Verify fallback text displays correctly
    """
```

-----

### ⚪ PHASE 7: Party System Enhancement (Week 13)

**Network Stability Milestone:** 20 players, 4 simultaneous parties, dungeon instances tested

#### Task 7.1: Party Formation & Management

**File:** `/systems/party_system.py` (UPDATE EXISTING)

```python
class PartySystem:
    MAX_PARTY_SIZE = 6
    MIN_PARTY_SIZE = 2
    
    def create_party(leader, party_name):
        """
        - Create Party entry in database
        - Set leader
        - Generate unique party_id
        - Initialize loot rules (default: ROUND_ROBIN)
        """
        
    def invite_player(party_id, inviter, invitee):
        """
        - Check party size < MAX
        - Check faction compatibility
        - Send invitation to invitee
        - Pending invitation expires in 5 minutes
        """
        
    def join_party(character, party_id):
        """
        - Add to party.members
        - Share party chat
        - Sync current location
        - Apply party buffs
        """
        
    def leave_party(character, party_id):
        """
        - Remove from members
        - If leader leaves, transfer or disband
        - Stop sharing XP/loot
        """
        
    def set_loot_rules(party_id, leader, rule_type):
        """
        ROUND_ROBIN: Take turns automatically
        NEED_GREED: Roll system (100-sided die)
        LEADER_LOOT: Leader distributes
        FREE_FOR_ALL: First to grab
        """
```

**Database Schema:**

```python
class Party(Base):
    id = Column(Integer, primary_key=True)
    party_id = Column(String, unique=True)
    name = Column(String)
    leader_id = Column(Integer, ForeignKey('characters.id'))
    created_at = Column(DateTime)
    loot_rule = Column(Enum(LootRule), default=LootRule.ROUND_ROBIN)
    
    members = relationship("Character", secondary="party_members")


class PartyMember(Base):
    party_id = Column(Integer, ForeignKey('parties.id'))
    character_id = Column(Integer, ForeignKey('characters.id'))
    joined_at = Column(DateTime)
```

**Commands:**

```
/party create "Party Name"     - Create new party
/party invite <player>          - Invite player
/party accept                   - Accept invitation
/party kick <player>            - Kick member (leader only)
/party leave                    - Leave party
/party loot <rule>              - Set loot rules (leader only)
/party info                     - Show party details
```

-----

#### Task 7.2: Party Combat & XP Sharing

**File:** `/combat/party_combat.py` (NEW)

```python
def calculate_party_xp(base_xp, party_size, level_range):
    """
    Party XP formula:
    - Base XP * party_size (more people = more total XP)
    - Split among members in proximity (must be in same zone)
    - Bonus if levels are close (+10% if within 3 levels)
    - Penalty if levels are far apart (-20% if >5 levels)
    """
    
def distribute_party_loot(loot_items, party, loot_rule):
    """
    Apply loot rules:
    - ROUND_ROBIN: Next in turn gets item
    - NEED_GREED: All roll, highest wins
    - LEADER_LOOT: Leader assigns items
    - FREE_FOR_ALL: First to type /loot <item>
    """
    
def apply_party_combat_bonuses(party):
    """
    Party synergies:
    - 2+ players attacking same target: +15% damage
    - Paladin in party: +10% healing received
    - Warrior in party: -10% damage taken
    - Mage in party: +5% spell power for all casters
    """
```

-----

#### Task 7.3: Party Dungeons (2 Minimum - REDUCED from 3)

**File:** `/data/dungeons/party_dungeons.json` (NEW)

Create instanced dungeons that require 2-6 players:

1. **The Crypt of Forgotten Kings** (Level 8-12, 2-4 players)

- 5 rooms, ends with mini-boss
- Boss: “The Hollow King” (undead knight)
- Rewards: Uncommon gear, faction rep
- Duration: 20-30 minutes

1. **The Blood Pit Arena** (Level 15-20, 4-6 players)

- Wave-based combat (Crimson Legion theme)
- 10 waves, final boss: “Champion of the Pit”
- Rewards: Epic weapon, arena title
- Duration: 30-45 minutes

**Dungeon Mechanics:**

- Instance created when party leader enters
- Separate from open world (no other players)
- Resets after completion or 2 hours
- Loot chest at end (party rolls on items)
- Can be repeated (no cooldown for alpha testing)

-----

### 🟢 PHASE 8: Aetherfall Mechanics (Week 14)

**Network Stability Milestone:** Full server Aetherfall tested (all online players simultaneously)

#### Task 8.1: Shard Claim System

**File:** `/systems/shard_system.py` (UPDATE EXISTING)

```python
class ShardSystem:
    def attempt_shard_claim(party, shard_id):
        """
        Requirements:
        - Party of 4-6 players
        - Defeat shard guardian (boss fight)
        - Majority of party must be same faction
        - At least 1 player must survive
        """
        
    def claim_shard(party, shard_id):
        """
        - Assign shard to dominant faction in party
        - Grant rewards to all party members:
          * Epic item for each
          * +100 faction rep
          * Title: "Shardclaimer"
        - Update world state
        - Broadcast to all players
        - Check if Aetherfall triggered (12 shards claimed)
        """
        
    def get_shard_status():
        """
        Return dictionary:
        {
          "shard_id": {
            "name": "Phoenix Flame",
            "controlled_by": "CRIMSON_LEGION",
            "claimed_at": datetime,
            "guardian_defeated_by": ["Player1", "Player2", ...]
          }
        }
        """
```

**Commands:**

```
/shard status              - Show all shard ownership
/shard locate <name>       - Hint at shard location (if rep high enough)
/shard history             - Show past claims
```

**Dev Command (alpha only):**

```
/dev aetherfall <faction>  - Force Aetherfall for testing
```

-----

#### Task 8.2: Aetherfall Trigger Event

**File:** `/systems/aetherfall.py` (NEW)

```python
class AetherfallSystem:
    def check_aetherfall_conditions(world_state):
        """
        Trigger when:
        - All 12 shards claimed by faction(s)
        - One faction controls 7+ shards (majority)
        - Or: 30 days have passed (alpha testing only)
        """
        
    def trigger_aetherfall(winning_faction):
        """
        MAJOR EVENT SEQUENCE:
        
        1. Server-wide notification
           "The Aetherfall begins! Reality fractures as {faction} reshapes existence!"
           
        2. 10-minute grace period
           - Players can finish active content
           - No new dungeon entries
           - All combat halted
           - Save all player data
           
        3. Reality shift
           - World transforms to faction's vision
           - Update all location descriptions
           - Respawn appropriate NPCs
           - Remove incompatible enemies
           
        4. Player persistence
           - Keep: Level, skills, inventory, memories
           - Keep: Quest progress (faction quests reset)
           - Grant: "Cycle Survivor" title
           - Award: "Echo-Touched" item (proof of survival)
           - Increment: cycle_number in player data
           
        5. Broadcast lore
           - LLM generates dramatic narration
           - Update world history log
           - Begin new cycle (Cycle #X)
           
        6. Reset shard ownership
           - All shards return to unclaimed
           - Guardian bosses respawn
           - New race begins
        """
        
    def apply_reality_effects(reality_type):
        """
        Transform world based on winning faction:
        
        CELESTIAL_ORDER (Radiant Ascendancy):
        - Healing magic +25% stronger
        - Dark magic disabled (Necromancers lose spells)
        - Undead enemies removed
        - Golden aesthetic on locations
        - Shadow Pact members hunted by patrols
        
        CRIMSON_LEGION (Tyrant's Dominion):
        - All zones become contested (PvP enabled)
        - Combat XP +50%
        - Peace actions penalized
        - War-torn aesthetic
        - Non-combat quests disabled
        
        ARCANE_CONSORTIUM (Fractured Nexus):
        - Magic +30% power
        - Random anomalies spawn (teleports, time dilation)
        - Reality distortions common
        - Floating island aesthetic
        - Physical weapons -20% damage
        
        SHADOW_PACT (Eternal Veil):
        - Crit damage +30%
        - Stealth effectiveness doubled
        - Illusions everywhere (NPCs may be fake)
        - Eternal twilight aesthetic
        - Trust no one
        
        WILDBORN_CLANS (Verdant Rebirth):
        - Cities overgrown/inaccessible
        - Beast taming enhanced (+2 companions)
        - Technology weakened (guns disabled)
        - Nature reclaimed aesthetic
        - Crafting from nature buffed
        """
        
    def save_cycle_history(cycle_number, winning_faction, duration_days):
        """
        Record this cycle in database:
        - Cycle number
        - Winning faction
        - Duration
        - Key players (top shard claimers)
        - Major events
        """
```

**Alpha Limitation:** Only test 2 realities:

- Default (Broken World)
- One faction victory (preferably Crimson Legion or Celestial Order)

-----

#### Task 8.3: Post-Aetherfall Content (MINIMAL)

**File:** `/data/quests/post_aetherfall_quests.json` (NEW)

Create reality-specific quests (3 total for alpha):

- 1 quest for Radiant Ascendancy (if Celestial Order wins)
- 1 quest for Tyrant’s Dominion (if Crimson Legion wins)
- 1 generic “Cycle Survivor” quest

**Example:**

```json
{
  "quest_id": "tyrant_dominion_001",
  "title": "Prove Your Worth in Blood",
  "description": "In the new world of eternal war, you must prove you belong. Enter the Blood Pit and survive 5 rounds.",
  "available_only_in_reality": "TYRANT_DOMINION",
  "required_title": "CYCLE_SURVIVOR",
  "objectives": [
    {
      "type": "survive_waves",
      "location": "blood_pit_arena",
      "waves": 5
    }
  ],
  "xp_reward": 1000,
  "souls_reward": 500,
  "reputation_rewards": {
    "CRIMSON_LEGION": 50
  }
}
```

-----

### 🔵 PHASE 9: Polish & Testing (Week 15-16)

**Network Stability Milestone:** 30 players, 8-hour stress test, zero crashes

#### Task 9.1: Tutorial System

**File:** `/systems/tutorial.py` (NEW)

```python
class TutorialSystem:
    """
    First-time player experience (30 minutes)
    """
    
    TUTORIAL_STEPS = [
        "welcome",              # Intro narration (LLM)
        "character_creation",   # Race, class, name
        "starting_zone_choice", # Bloodmarked/Hollow/Crossroads
        "movement",             # How to navigate
        "examine",              # How to look at things
        "npc_interaction",      # Talk to guide NPC
        "combat_basics",        # Fight tutorial enemy
        "death_recovery",       # Die intentionally, recover souls
        "inventory",            # Equip item
        "bonfire",              # Activate first bonfire
        "faction_introduction", # Meet faction representatives
        "first_quest",          # Accept starter quest
        "party_basics",         # How to group up
        "tutorial_complete"     # Grant reward, unlock world
    ]
    
    def start_tutorial(character):
        """Begin guided experience"""
        
    def advance_tutorial(character, step_completed):
        """Move to next step, track progress"""
        
    def skip_tutorial(character):
        """For experienced players / alt characters"""
```

**Tutorial Rewards:**

- Starter gear (weapon + armor set)
- 500 XP (reach level 2)
- 100 souls
- “Tutorial Graduate” title
- Access to all starting zones

-----

#### Task 9.2: Help System

**File:** `/systems/help_system.py` (NEW)

```python
HELP_TOPICS = {
    "commands": "List of all available commands",
    "combat": "How combat works (stamina, attacks, parrying)",
    "death": "What happens when you die and how to recover souls",
    "factions": "Explanation of the 6 factions",
    "cults": "How to discover and join secret cults",
    "parties": "How to form and manage parties",
    "quests": "Quest system overview",
    "shards": "Crystal shards and the Aetherfall",
    "reputation": "Faction reputation system",
    "pvp": "PvP rules and flagging system",
    "bonfire": "Checkpoint system and fast travel",
    "beginner": "New player guide (full walkthrough)"
}

def get_help(topic=None):
    """
    /help              - List all topics
    /help <topic>      - Show specific help
    """
```

**In-Game Documentation:**

- `/help commands` - Full command reference
- `/help beginner` - New player guide
- `/help <faction>` - Faction-specific info
- `/help lore` - Brief world summary
- `/help death` - Death mechanics explained
- `/help pvp` - PvP rules and etiquette

-----

#### Task 9.3: Balance Testing Checklist

**Combat Balance:**

- [ ] All classes viable in solo PvE (can reach level 20)
- [ ] No class dominates PvP completely (win rate <60%)
- [ ] Boss fights challenging but fair (4-6 players, 10-15 min fights)
- [ ] Stamina system prevents spamming (3-5 actions per stamina bar)
- [ ] Status effects meaningful but not OP (max 30% damage boost)

**Progression Balance:**

- [ ] Level 1-10 takes ~5 hours (casual play)
- [ ] Level 10-20 takes ~15 hours (casual play)
- [ ] Level 20-25 takes ~10 hours (casual play)
- [ ] Total alpha playtime: 30-40 hours to endgame
- [ ] XP curve feels smooth (no grind walls)

**Economy Balance:**

- [ ] Starting gear free/cheap (<50 souls)
- [ ] Mid-tier gear affordable by level 10 (500-1000 souls)
- [ ] Rare gear requires saving/farming (2000-5000 souls)
- [ ] Epic/Legendary gear feels special (10000+ souls)
- [ ] Souls gained ≈ souls spent (no deflation/inflation)
- [ ] Vendor prices consistent across factions

**Faction Balance:**

- [ ] No faction obviously stronger (shard claim rate within 10%)
- [ ] Each faction has unique advantage (verified in gameplay)
- [ ] Factionless viable (harder but rewarding)
- [ ] Cross-faction parties work mechanically (tested)
- [ ] Faction bonuses feel impactful (+25% is noticeable)

**Cult Balance:**

- [ ] Discovery conditions achievable (playtesters found 2/3 cults)
- [ ] Powers feel powerful but not mandatory
- [ ] Penalties are tolerable (don’t make game unplayable)
- [ ] Cult questlines engaging (positive playtester feedback)

**LLM Quality:**

- [ ] Narration matches atmosphere 90%+ of time
- [ ] NPC dialogue stays in character (no modern slang)
- [ ] Location descriptions immersive (positive feedback)
- [ ] Combat narration dramatic (not repetitive)
- [ ] Fallback text acceptable when LLM fails (<10% usage)
- [ ] Response time <2 seconds average

**Network Stability:**

- [ ] 20 players in one zone stable (no lag spikes)
- [ ] 30 total concurrent players (tested)
- [ ] Party sync works 95%+ of time
- [ ] Combat state sync works 98%+ of time
- [ ] Death/respawn sync works 100% of time
- [ ] Reconnect after disconnect works (30s timeout)

-----

#### Task 9.4: Bug Bash & Stability

**Critical Bugs to Fix:**

- [ ] Character save/load works 100% (no data loss)
- [ ] Party system stable (no desyncs, tested 20+ sessions)
- [ ] Combat doesn’t soft-lock (tested all class combinations)
- [ ] Quests complete properly (all 17 quests tested)
- [ ] Shard claims don’t duplicate (tested 10+ claims)
- [ ] Aetherfall doesn’t corrupt database (tested 3+ cycles)
- [ ] P2P connections stable (reconnect handling tested)
- [ ] LLM timeouts handled gracefully (fallback triggers)
- [ ] Inventory sync works (no item duplication)
- [ ] Death penalties apply correctly (soul recovery tested)

**Performance Testing:**

- [ ] 20 players in one zone (5 minute test)
- [ ] 30+ total concurrent players (30 minute test)
- [ ] 8-hour stress test (weekend marathon)
- [ ] Database queries optimized (no queries >100ms)
- [ ] Memory leaks checked (monitor for 8 hours)
- [ ] Network bandwidth reasonable (<1 Mbps per player)
- [ ] LLM response cache 50%+ hit rate

**Automated Testing:**

```python
# /tests/integration_tests.py
def test_full_playthrough():
    """
    Automated bot completes:
    - Tutorial
    - First faction quest
    - Reaches level 10
    - Joins party
    - Completes dungeon
    - Claims shard
    
    Run nightly to catch regressions
    """
```

-----

#### Task 9.5: Alpha Preview Weekend (NEW)

**Duration:** 3 days (Friday-Sunday)  
**Participants:** 10-15 external testers (not dev team)

**Friday Evening: Onboarding Session**

- 2-hour guided tour
- Tutorial walkthrough
- Faction explanations
- Discord voice chat for questions

**Saturday: Free Play**

- 8-hour open play session
- Devs available for support
- Live feedback in Discord
- Bug reports tracked in real-time

**Sunday: Structured Tests**

- Morning: Boss fight tests (shard guardians)
- Afternoon: PvP tests (flagged combat)
- Evening: Aetherfall event (force trigger)
- Debrief: Feedback session

**Data Collection:**

- Session recordings (with permission)
- Screenshot highlights
- Testimonial quotes
- Balance feedback surveys
- Bug reports

**Deliverables:**

- Marketing screenshots (10+)
- Testimonial quotes (5+)
- Bug priority list
- Balance adjustment recommendations

-----

## Success Metrics

### Alpha is “Complete” When:

**✅ Core Systems Working:**

- [ ] Character creation (9 classes, 7 races) - functional
- [ ] Faction system (join, rep, bonuses, oath-breaking) - tested
- [ ] Cult system (3 discoverable, powers granted) - verified
- [ ] Quest system (17+ quests, tracking, rewards) - all quests completable
- [ ] Party system (2-6 players, loot rules, dungeons) - stable
- [ ] Combat (Souls-like mechanics, balanced) - all classes viable
- [ ] Death system (soul recovery, bonfire respawn) - works 100%
- [ ] PvP system (flagging, duels, rewards) - tested
- [ ] Economy (vendors, loot drops, 30+ items) - balanced
- [ ] LLM integration (narration, dialogue, atmosphere) - 90%+ quality

**✅ Content Populated:**

- [ ] 3 starting zones playable (Bloodmarked, Hollow, Crossroads)
- [ ] 6 faction hubs accessible (all factions represented)
- [ ] 10+ world locations explorable (including cult discovery zones)
- [ ] 20+ NPCs interactable (quest givers, vendors, trainers)
- [ ] 3 Crystal Shards claimable (Phoenix Flame, Tidecaller’s Pearl, Earthheart Stone)
- [ ] 2 party dungeons completable (Crypt, Blood Pit)
- [ ] 10+ bonfires activated (fast travel network)

**✅ Endgame Functional:**

- [ ] Level 1-25 progression path clear (tested)
- [ ] 3 shard guardian boss fights working (balanced for 4-6 players)
- [ ] Aetherfall trigger functional (tested 2+ times)
- [ ] Reality shift observable (at least 1 alternate reality tested)
- [ ] Post-Aetherfall content exists (3+ quests)

**✅ Multiplayer Stable:**

- [ ] P2P networking reliable (reconnect works)
- [ ] Party formation smooth (no desyncs)
- [ ] XP/loot sharing working (tested all loot modes)
- [ ] PvP zones functional (tested flagging system)
- [ ] Cross-faction parties possible (with penalties tested)
- [ ] 30 concurrent players stable (stress tested)

**✅ Polish Complete:**

- [ ] Tutorial guides new players (30min completion time)
- [ ] Help system comprehensive (all topics covered)
- [ ] No game-breaking bugs (critical bug list = 0)
- [ ] Performance acceptable (30 players, <100ms latency)
- [ ] LLM fallbacks prevent immersion breaks (<10% fallback usage)

**✅ Qualitative Metrics (Alpha Preview Weekend):**

- [ ] 60%+ of testers complete tutorial
- [ ] 40%+ reach level 10
- [ ] 20%+ reach level 20
- [ ] Average session length: 2+ hours
- [ ] Positive atmosphere feedback (8/10 rating)
- [ ] Faction system engaging (players debate choices)
- [ ] At least 1 cult discovered organically
- [ ] Players form parties without prompting

-----

## Post-Alpha Roadmap

### What Comes After Alpha?

**Beta Phase 1 (3-4 months):**

- Expand to all 7 realities (full Aetherfall content)
- Add remaining 5 cults (8 total)
- Create 40+ total locations (from 10)
- Implement all named NPCs (25+)
- Add crafting system (basic)
- Expand economy (100+ items)
- Add 8 more dungeons (3-6 players)
- Implement 4 raid bosses (6-player endgame)
- Advanced AI NPC behaviors

**Beta Phase 2 (2-3 months):**

- Add daily/weekly quests (retention)
- Implement achievement system
- Add leaderboards (PvP, PvE, faction contribution)
- Create seasonal events
- Implement housing (basic)
- Add guild halls (faction-based, not player-run)
- Optimize performance (50+ concurrent players)
- Mobile client (iOS/Android)

**Launch Preparation (2-3 months):**

- Full documentation (player guide, lore primer)
- Marketing materials (trailer, website, press kit)
- Community management tools
- Anti-cheat measures
- Server infrastructure scaling (dedicated servers)
- Final balance pass
- Extensive bug fixes
- Launch trailer / demo

-----

## Development Notes

### Tools & Resources

**AI Agents (for Development):**

- **Claude Code** - Primary coding assistant
- **Serena** - AI agent toolkit integration
- **Kanban MCP** - Task tracking and knowledge base management

**LLM Backend:**

- **Qwen3** - Narrative generation, NPC dialogue, location descriptions
- **Context Management** - 2000 token budget per interaction
- **Response Caching** - 50%+ hit rate target
- **Pre-Generation** - 100+ common scenarios
- **Fallback System** - Static text when LLM unavailable

**Database:**

- **SQLAlchemy** - ORM for SQLite (dev) / PostgreSQL (prod)
- **Migrations** - Track schema changes carefully (Aetherfall persistence!)
- **Backups** - Automated backups every 6 hours during alpha
- **Rollback Scripts** - Every migration must have rollback

**Multiplayer:**

- **P2P Architecture** - Decentralized, master server for discovery
- **Encryption** - Required for all connections
- **Max Connections** - 20 players per zone (configurable)
- **State Sync** - 100ms polling, optimistic client prediction
- **Reconnect Logic** - 30s timeout, auto-rejoin party

**Testing Infrastructure:**

- **Automated Bots** - Simulate players for load testing
- **Integration Tests** - Run nightly, catch regressions
- **Performance Profiling** - Monitor memory, CPU, network
- **Error Tracking** - Sentry or similar for crash reports

-----

### Key Design Principles

1. **Lore First** - Every system should reinforce the world’s narrative
2. **No Generic MMO Tropes** - Avoid guild banks, auction houses, etc.
3. **Meaningful Choices** - Faction/cult decisions have consequences
4. **Souls-like Difficulty** - Challenging but fair
5. **AI-Enhanced, Not AI-Dependent** - Game works even if LLM fails
6. **Party Over Solo** - Encourage cooperation (but allow solo play)
7. **Dark Fantasy Atmosphere** - Oppressive, foreboding, mysterious
8. **Respect Player Time** - Alpha should be completable in 30-40 hours
9. **Network Stability First** - Test multiplayer every phase
10. **Iterate Fast** - Vertical slice before breadth

-----

### Critical Path Dependencies

**Before Starting Any Phase:**

- ✅ Phase 0 (Lore Alignment) MUST be complete
  - Faction names synced
  - Race list updated
  - Class list finalized
  - Shard assignments clear
  - Lore lockfile created

**Phase Dependencies:**

- Phase 0.5 (Vertical Slice) → Validates core loop before investing in breadth
- Phase 1 (Factions + Death) → Required for Phase 2 (Cults) and Phase 3 (Quests)
- Phase 4 (World) + Phase 5 (Economy) → Can be done in parallel
- Phase 6 (LLM) → Can be done parallel to Phase 4-5, but requires Phase 0.5 complete
- Phase 7 (Party) → Requires Phase 1, 3, 4 complete
- Phase 8 (Aetherfall) → Requires Phase 1, 4, 6, 7 complete
- Phase 9 (Polish) → Final phase, requires all others

**Recommended Order:**

1. **Week 1:** Phase 0 - Alignment
2. **Week 2:** Phase 0.5 - Vertical Slice
3. **Week 3-4:** Phase 1 - Factions + Death + PvP
4. **Week 5:** Phase 2 - Cults
5. **Week 6:** Phase 3 - Quests
6. **Week 7-8:** Phase 4 (World) + Phase 5 (Economy) - PARALLEL
7. **Week 10-12:** Phase 6 - LLM Integration (EXTENDED)
8. **Week 13:** Phase 7 - Party System
9. **Week 14:** Phase 8 - Aetherfall
10. **Week 15-16:** Phase 9 - Polish + Alpha Preview Weekend

**Total Timeline: 16 weeks (~4 months) for alpha**

-----

### Risk Mitigation

**Technical Risks:**

- **LLM Instability** → Robust fallback system, caching responses, pre-generation
- **P2P Connection Issues** → Reconnect logic, graceful degradation, stress testing
- **Database Corruption** → Automated backups (6hr), transaction safety, rollback scripts
- **Performance Degradation** → Profiling, optimization passes, load testing
- **Scope Creep** → Strict alpha scope, ruthless feature cuts

**Design Risks:**

- **Faction Imbalance** → Iterative balance testing with alpha testers, data tracking
- **Progression Too Slow** → Adjustable XP rates during alpha, playtester feedback
- **Content Drought** → Focus on replayability (multiple factions/cults), quality over quantity
- **LLM Inconsistency** → Strong system prompts, lore context injection, caching
- **Death System Too Punishing** → Tunable penalties, bonfire density, playtester feedback

**Scope Risks:**

- **Feature Creep** → Strict alpha scope, move features to beta, weekly check-ins
- **Timeline Slippage** → Weekly check-ins, cut features if needed, prioritize core loop
- **Tester Burnout** → Rotate testers, limit alpha duration to 2-3 months, reward participation
- **Network Instability** → Test every phase, dedicated stress tests, reconnect logic

**Mitigation Strategy:**

- **Weekly Check-ins** - Review progress, adjust timeline
- **Monthly Milestones** - Phase completion gates
- **Bi-weekly Playtests** - Internal team plays together
- **Alpha Preview Weekend** - External validation before “complete”
- **Feature Cut List** - Pre-approved features to cut if timeline slips

-----

### Definition of Done (Per Phase)

Each phase is “complete” when:

- [ ] All tasks implemented and tested
- [ ] Code reviewed and documented
- [ ] Database migrations created (with rollback scripts)
- [ ] LLM prompts tested (if applicable, 90%+ quality)
- [ ] Integration tested with existing systems
- [ ] No game-breaking bugs (critical list = 0)
- [ ] Performance acceptable (meets milestone)
- [ ] Lore consistency verified (against lore lockfile)
- [ ] Network stability milestone met
- [ ] Unit tests written (for critical systems)

-----

## Contact & Collaboration

**Project Leads:**

- Lead Developer: Matt Olander
- Game Design: J.T. Nixon

**Alpha Tester Requirements:**

- Commitment: 10+ hours/week for 2-3 months
- Feedback: Detailed bug reports, balance suggestions
- Mindset: Focus on core systems, not polish
- Community: Discord for communication
- NDA: Sign non-disclosure agreement (pre-release)

**Feedback Channels:**

- GitHub Issues (bugs, technical problems)
- Discord (balance, design feedback, community)
- In-game feedback system (QoL requests)
- Alpha Preview Weekend (structured feedback sessions)

**Communication Tools:**

- Discord server (primary)
- GitHub Projects (task tracking)
- Weekly dev blog (progress updates)
- Monthly playtests (internal team)

-----

## Appendix: Quick Reference

### File Structure (New/Modified Files)

```
aetheris/
├── systems/
│   ├── faction_system.py        [NEW - Phase 1]
│   ├── reputation.py            [NEW - Phase 1]
│   ├── death_system.py          [NEW - Phase 1]
│   ├── pvp_system.py            [NEW - Phase 1]
│   ├── cult_system.py           [NEW - Phase 2]
│   ├── cult_powers.py           [NEW - Phase 2]
│   ├── quest_system.py          [NEW - Phase 3]
│   ├── vendor_system.py         [NEW - Phase 5]
│   ├── loot_system.py           [NEW - Phase 5]
│   ├── shard_system.py          [UPDATE - Phase 8]
│   ├── aetherfall.py            [NEW - Phase 8]
│   ├── tutorial.py              [NEW - Phase 9]
│   └── help_system.py           [NEW - Phase 9]
│
├── models/
│   ├── character.py             [UPDATE - Phase 0 - races/classes/death]
│   ├── faction.py               [UPDATE - Phase 0 - faction names]
│   ├── quest.py                 [NEW - Phase 3]
│   ├── cult.py                  [NEW - Phase 2]
│   └── shard.py                 [UPDATE - Phase 0 - faction affinity]
│
├── data/
│   ├── lore_schema.json         [NEW - Phase 0.5]
│   ├── lore_database.json       [NEW - Phase 6]
│   ├── pregenerated_narration.json [NEW - Phase 6]
│   ├── quests/
│   │   ├── starter_quests.json      [NEW - Phase 3]
│   │   └── post_aetherfall_quests.json [NEW - Phase 8]
│   ├── locations/
│   │   ├── starting_zones.json      [NEW - Phase 4]
│   │   ├── faction_hubs.json        [NEW - Phase 4]
│   │   └── world_locations.json     [NEW - Phase 4]
│   ├── npcs/
│   │   └── world_npcs.json          [NEW - Phase 4]
│   ├── items/
│   │   ├── weapons.json             [NEW - Phase 5]
│   │   ├── armor.json               [NEW - Phase 5]
│   │   └── consumables.json         [NEW - Phase 5]
│   └── dungeons/
│       └── party_dungeons.json      [NEW - Phase 7]
│
├── llm/
│   ├── context_manager.py       [NEW - Phase 6]
│   ├── lore_loader.py           [NEW - Phase 6]
│   ├── response_cache.py        [NEW - Phase 6]
│   ├── prompts.py               [UPDATE - Phase 6]
│   └── fallbacks.py             [UPDATE - Phase 6]
│
├── combat/
│   └── party_combat.py          [NEW - Phase 7]
│
├── prototypes/
│   ├── vertical_slice.py        [NEW - Phase 0.5]
│   ├── test_location.json       [NEW - Phase 0.5]
│   ├── test_npcs.json           [NEW - Phase 0.5]
│   ├── test_quest.json          [NEW - Phase 0.5]
│   └── test_items.json          [NEW - Phase 0.5]
│
├── tests/
│   ├── integration_tests.py     [NEW - Phase 9]
│   ├── llm_stress_test.py       [NEW - Phase 6]
│   └── network_stress_test.py   [UPDATE - Phase 1, 4, 7, 8, 9]
│
├── tools/
│   ├── validate_lore.py         [NEW - Phase 0.5]
│   ├── preprocess_lore.py       [NEW - Phase 6]
│   └── pregenerate_narration.py [NEW - Phase 6]
│
└── database/
    └── migrations/
        ├── 001_rename_factions.py [NEW - Phase 0]
        ├── 002_add_death_system.py [NEW - Phase 1]
        ├── 003_add_pvp_system.py [NEW - Phase 1]
        ├── 004_add_cult_system.py [NEW - Phase 2]
        ├── 005_add_quest_system.py [NEW - Phase 3]
        └── 006_add_bonfire_system.py [NEW - Phase 1]
```

### Command Reference (Alpha Version)

**Character & Movement:**

```
/who                       - Show online players
/look                      - Examine current location
/examine <target>          - Examine object/NPC/player
/move <direction>          - Move to adjacent zone
/say <message>             - Speak in local chat
/tell <player> <message>   - Private message
/emote <action>            - Perform emote
```

**Combat:**

```
/attack <target>           - Basic attack
/parry                     - Attempt to parry next attack
/dodge                     - Attempt to dodge
/ability <name>            - Use class ability
/target <name>             - Set combat target
/flee                      - Attempt to flee combat
```

**Death & Respawn:**

```
/bonfire activate          - Set as respawn point
/bonfire list              - Show discovered bonfires
/bonfire travel <name>     - Teleport to bonfire (costs souls)
/recover                   - Pick up soul marker at current location
/death                     - Show death statistics
```

**Faction Commands:**

```
/faction info              - Show current faction, rep, bonuses
/faction join <name>       - Join a faction (if eligible)
/faction leave             - Leave faction (with warnings)
/faction reputation        - Show rep with all factions
/faction oath              - View your faction oath
```

**Cult Commands:**

```
/cult info                 - Show cult membership status
/cult powers               - List available cult powers
/cult obligations          - Check obligation requirements
/cult leave                - Leave cult (major consequences)
```

**Quest Commands:**

```
/quest list                - Show available quests
/quest active              - Show active quests
/quest accept <id>         - Accept a quest
/quest progress            - Check objectives progress
/quest abandon <id>        - Abandon quest
/quest completed           - View completed quests
/quest share               - Share active quest with party
```

**Party Commands:**

```
/party create "Name"       - Create new party
/party invite <player>     - Invite player
/party accept              - Accept invitation
/party decline             - Decline invitation
/party kick <player>       - Kick member (leader only)
/party leave               - Leave party
/party loot <rule>         - Set loot rules (leader only)
/party info                - Show party details
/party chat <message>      - Party-only chat
```

**Inventory & Equipment:**

```
/inventory                 - Show inventory
/equip <item>              - Equip item
/unequip <slot>            - Unequip slot
/use <item>                - Use consumable
/drop <item>               - Drop item
/souls                     - Show current souls
```

**Vendor Commands:**

```
/vendor list               - Show vendor inventory
/vendor buy <item> [qty]   - Purchase item
/vendor sell <item> [qty]  - Sell item
/vendor repair             - Repair all equipment
/vendor compare <item>     - Compare with equipped
```

**Shard Commands:**

```
/shard status              - Show all shard ownership
/shard locate <name>       - Hint at shard location (if rep high enough)
/shard history             - Show past claims
```

**PvP Commands:**

```
/duel <player>             - Challenge to formal duel
/duel accept               - Accept duel challenge
/duel decline              - Decline duel
/pvp flag                  - Voluntary PvP flag (30min)
/pvp unflag                - Remove flag early (5min cooldown)
/pvp status                - Show your PvP stats
```

**Help Commands:**

```
/help                      - List all help topics
/help <topic>              - Show specific help
/help commands             - Full command reference
/help beginner             - New player guide
/help <faction>            - Faction-specific info
```

**Admin/Dev Commands (Alpha Only):**

```
/dev aetherfall <faction>  - Force Aetherfall for testing
/dev spawn <enemy> <level> - Spawn test enemy
/dev teleport <location>   - Instant teleport
/dev setlevel <level>      - Set character level
/dev giveitem <item>       - Give item to self
/dev god                   - Toggle invincibility
/dev speed <multiplier>    - Adjust movement speed
/dev resetquest <id>       - Reset quest progress
```

-----

### Network Stability Milestones Summary

|Phase|Week |Players|Duration|Test Focus                        |
|-----|-----|-------|--------|----------------------------------|
|0.5  |2    |2      |30min   |Basic P2P, same zone              |
|1    |3-4  |5      |1hr     |Cross-faction party, death/respawn|
|2    |5    |10     |2hr     |Multiple zones                    |
|3    |6    |15     |3hr     |Quest sharing in parties          |
|4    |7-8  |20     |3hr     |5+ zones simultaneously           |
|5    |9    |20     |2hr     |Economy sync (transactions)       |
|6    |10-12|20     |2hr     |LLM load (simultaneous requests)  |
|7    |13   |20     |3hr     |Dungeon instances, 4 parties      |
|8    |14   |30     |2hr     |Full server Aetherfall            |
|9    |15-16|30     |8hr     |Weekend stress test               |

**Final Stress Test Goal:** 30 concurrent players, 8 hours, zero crashes

-----

### Alpha Testing Schedule

**Week 1: Internal Setup**

- Phase 0 implementation
- Dev environment setup
- Initial migration scripts

**Week 2-4: Core Systems**

- Phase 0.5: Vertical slice
- Phase 1: Factions, death, PvP
- Internal playtest #1 (3 devs)

**Week 5-6: Content Foundation**

- Phase 2: Cults
- Phase 3: Quests
- Internal playtest #2 (5 devs)

**Week 7-9: World Building**

- Phase 4: Locations
- Phase 5: Economy
- Internal playtest #3 (5 devs, 2hr session)

**Week 10-12: AI Integration**

- Phase 6: LLM system
- Quality testing
- Internal playtest #4 (narrative focus)

**Week 13: Multiplayer Enhancement**

- Phase 7: Party system
- Internal playtest #5 (party dungeons)

**Week 14: Endgame**

- Phase 8: Aetherfall
- Internal playtest #6 (forced Aetherfall)

**Week 15-16: Polish & Preview**

- Phase 9: Tutorial, help, balance
- Internal playtest #7 (full playthrough)
- **Alpha Preview Weekend** (10-15 external testers)
- Bug fixes based on feedback
- **ALPHA COMPLETE**

-----

### Content Creation Priorities

**Week-by-Week Content Goals:**

**Week 1-2: Foundation**

- [ ] Lore schema created
- [ ] 3 races implemented (Human, Taur’n, Elf)
- [ ] 3 classes implemented (Warrior, Mage, Rogue)
- [ ] 1 location (Crossroads)
- [ ] 3 NPCs (quest giver, vendor, enemy)

**Week 3-4: Expansion**

- [ ] 4 more races (Orc, Reptilian, Dwarf, Shadowkin)
- [ ] 6 more classes (Paladin, Necromancer, Ranger, Spellblade, Monk, Shaman)
- [ ] 2 more locations (Bloodmarked Fields, Hollow Refuge)
- [ ] 6 faction representatives
- [ ] Death system NPCs (bonfire keepers)

**Week 5: Cults**

- [ ] 3 cult discovery NPCs
- [ ] 3 cult hideouts
- [ ] Cult power descriptions

**Week 6: Quests**

- [ ] 1 tutorial quest
- [ ] 15 faction quests (3 per faction)
- [ ] 2 cult discovery quests

**Week 7-8: World**

- [ ] 6 faction hubs
- [ ] 4 exploration zones
- [ ] 2 cult zones
- [ ] 3 shard guardian lairs
- [ ] 10+ bonfire locations
- [ ] 10+ NPCs (vendors, trainers, lore characters)

**Week 9: Economy**

- [ ] 12 weapons
- [ ] 10 armor pieces
- [ ] 8 consumables
- [ ] Vendor inventories

**Week 10-12: LLM**

- [ ] Lore database (JSON)
- [ ] 100+ pregenerated narrations
- [ ] Fallback text for all scenarios
- [ ] NPC personality matrices

**Week 13: Dungeons**

- [ ] Crypt of Forgotten Kings (5 rooms)
- [ ] Blood Pit Arena (10 waves)

**Week 14: Aetherfall**

- [ ] 3 post-Aetherfall quests
- [ ] 1 alternate reality (Tyrant’s Dominion or Radiant Ascendancy)

**Week 15-16: Polish**

- [ ] Tutorial narration (LLM generated)
- [ ] Help text (all topics)
- [ ] Balance adjustments

-----

### Bug Tracking & Priority

**Critical (P0) - Blocks Alpha Release:**

- Data loss bugs
- Save/load failures
- Crash on startup
- Network complete failure
- Game-breaking exploits

**High (P1) - Must Fix Before Preview Weekend:**

- Combat soft-locks
- Quest completion bugs
- Party desync issues
- Major balance problems
- Duplication exploits

**Medium (P2) - Fix If Time Permits:**

- Visual glitches
- Minor balance issues
- Typos in narration
- Inconsistent LLM responses
- Performance hiccups (<5 second freezes)

**Low (P3) - Move to Beta:**

- Feature requests
- QoL improvements
- Polish items
- Optional content
- Nice-to-have UI tweaks

**Bug Triage Process:**

1. Report bug in GitHub Issues
2. Reproduce bug (add reproduction steps)
3. Assign priority (P0-P3)
4. Assign developer
5. Fix and test
6. Mark as resolved
7. Verify in next playtest

-----

### Performance Targets

**Client Performance:**

- Startup time: <10 seconds
- Memory usage: <500 MB
- CPU usage: <30% (idle), <60% (active)
- Network: <1 Mbps per player

**Server Performance:**

- Response time: <100ms (average)
- Database queries: <50ms (average)
- LLM responses: <2 seconds (average)
- Concurrent players: 30+ stable

**Network Performance:**

- Latency: <100ms (local), <200ms (regional)
- Packet loss tolerance: <5%
- Reconnect time: <30 seconds
- State sync frequency: 10 updates/second

**Database Performance:**

- Read queries: <10ms
- Write queries: <50ms
- Transaction time: <100ms
- Backup size: <100 MB

-----

### Alpha Release Checklist

**Code Readiness:**

- [ ] All phases complete (0-9)
- [ ] All critical bugs fixed (P0 list = 0)
- [ ] All high-priority bugs fixed (P1 list <5)
- [ ] Code reviewed and documented
- [ ] Database migrations tested (including rollbacks)
- [ ] Performance targets met

**Content Readiness:**

- [ ] 17+ quests completable
- [ ] 10+ locations explorable
- [ ] 20+ NPCs interactable
- [ ] 30+ items functional
- [ ] 3 shard guardians beatable
- [ ] 2 dungeons completable
- [ ] Tutorial functional

**System Readiness:**

- [ ] Character creation works (all races/classes)
- [ ] Faction system functional (join, leave, rep)
- [ ] Cult system functional (3 cults discoverable)
- [ ] Quest system functional (accept, progress, complete)
- [ ] Party system functional (form, share XP/loot)
- [ ] Combat system functional (all classes balanced)
- [ ] Death system functional (soul recovery works)
- [ ] PvP system functional (flagging, duels)
- [ ] Economy functional (buy, sell, loot)
- [ ] LLM integration functional (90%+ quality)
- [ ] Aetherfall functional (tested 2+ times)

**Multiplayer Readiness:**

- [ ] P2P networking stable (30 players tested)
- [ ] Party sync works (95%+ reliability)
- [ ] Combat sync works (98%+ reliability)
- [ ] Death/respawn sync works (100% reliability)
- [ ] Reconnect works (30s timeout)
- [ ] 8-hour stress test passed

**Documentation Readiness:**

- [ ] Tutorial complete (30min experience)
- [ ] Help system complete (all topics)
- [ ] README updated
- [ ] Installation guide written
- [ ] Alpha tester guide written
- [ ] FAQ created

**Testing Readiness:**

- [ ] All integration tests passing
- [ ] All network tests passing
- [ ] All LLM tests passing
- [ ] Alpha Preview Weekend completed
- [ ] Feedback incorporated
- [ ] Final playtest successful

**Release Artifacts:**

- [ ] Builds created (Windows, Mac, Linux)
- [ ] Installation packages
- [ ] Server deployment scripts
- [ ] Database backup scripts
- [ ] Monitoring dashboards
- [ ] Error tracking configured

-----

## Final Notes & Philosophy

### The Core Vision

Aetheris is not just another MUD. It’s a living, breathing world where:

- **Choices matter** - Your faction allegiance reshapes reality itself
- **Death is meaningful** - Souls-like consequences make every encounter tense
- **AI enhances atmosphere** - LLM narration brings the dark fantasy world to life
- **Community drives story** - Players collectively determine which faction wins the Aetherfall
- **Replayability through resets** - Each cycle is a new beginning, but you remember

### Development Mantras

1. **“Core loop first, breadth later”** - The vertical slice proves the concept
2. **“Network stability every phase”** - Multiplayer issues compound if ignored
3. **“Lore consistency is sacred”** - Check against lore lockfile constantly
4. **“AI-enhanced, not AI-dependent”** - Game must work without LLM
5. **“Quality over quantity”** - 10 great locations > 20 mediocre ones
6. **“Playtest early, playtest often”** - Internal tests catch issues fast
7. **“Cut features ruthlessly”** - Alpha scope discipline is critical
8. **“Document as you build”** - Future-you will thank present-you
9. **“Celebrate small wins”** - Each phase completion is progress
10. **“Build for the players”** - They’re the reason we’re doing this

### What Makes Alpha Successful?

**Not** perfect graphics. **Not** 100+ hours of content. **Not** zero bugs.

**Alpha succeeds when:**

- 10-15 testers play for 2+ hours without quitting from frustration
- Players debate which faction to join (means choices matter)
- Players form parties without prompting (means multiplayer works)
- Players discover cults organically (means exploration is rewarding)
- Players talk about the game after logging off (means it’s memorable)

If alpha achieves these goals, **we’ve proven the concept**. Everything else can be refined in beta.

### The Path Forward

**After Alpha (4 months):**

- Beta Phase 1 (3-4 months): Expand content, all 7 realities
- Beta Phase 2 (2-3 months): Retention features, events, polish
- Launch Prep (2-3 months): Marketing, infrastructure, final polish

**Total Development: ~12-15 months from start to launch**

This is aggressive but achievable if:

- We maintain scope discipline
- We test network stability continuously
- We leverage LLM for content generation
- We cut features when timeline slips
- We focus on what makes Aetheris unique

### The Unique Selling Proposition

**“Aetheris: Where your faction’s victory rewrites reality itself.”**

No other MUD offers:

- Faction-driven reality resets (Aetherfall)
- AI-generated atmospheric narration
- Souls-like death mechanics in a MUD
- Secret cults with forbidden powers
- Persistent character memory across reality resets

This is what we’re building. This is what makes it special.

### One Final Word

**To the development team:**

You’re not just building a game. You’re creating a world where stories emerge, where communities form, where memories are made. The code you write, the systems you design, the content you create—it all matters.

When you’re deep in the trenches fixing a stubborn bug at 2 AM, remember: somewhere, a player will lose their first duel, recover their souls from a dangerous location, finally discover the Black Sun cult, and feel that rush of “I did it.”

**That moment is why we build.**

Stay focused. Test continuously. Cut ruthlessly. Iterate quickly.

**Let’s make something special.**

-----

**Roadmap Version:** 1.1  
**Last Updated:** 2025-01-05  
**Status:** Ready for Development  
**Next Review:** End of Phase 0 (Week 1)

**Good luck, and may the Aetherfall guide your path.**

⚔️ 🔥 💀 ⚡ 🌙

-----

**END OF ROADMAP**