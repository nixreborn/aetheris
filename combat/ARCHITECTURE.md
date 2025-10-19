# Combat System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COMBAT SYSTEM                                │
│                    Shards of Eternity v1.0                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│              │           │              │           │              │
│  COMBAT      │           │  ENEMY       │           │  ABILITY     │
│  SYSTEM      │◄─────────►│  SYSTEM      │           │  SYSTEM      │
│              │           │              │           │              │
│  system.py   │           │  enemies.py  │           │  abilities.py│
│              │           │              │           │              │
└──────┬───────┘           └──────┬───────┘           └──────┬───────┘
       │                          │                          │
       │ Uses                     │ Creates                  │ Manages
       │                          │                          │
       ▼                          ▼                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                      SHARED COMPONENTS                            │
├──────────────────────────────────────────────────────────────────┤
│  • Character (database.models)                                   │
│  • CharacterManager (characters.character)                       │
│  • LLMGenerator (llm.generator)                                  │
│  • Database Session (database)                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. Combat System (system.py)

```
┌─────────────────────────────────────────────────────┐
│              COMBAT SYSTEM MODULE                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐         ┌──────────────┐         │
│  │ CombatSystem │────────►│  Combatant   │         │
│  └──────┬───────┘         └──────┬───────┘         │
│         │                        │                  │
│         │ Contains               │ Has              │
│         ▼                        ▼                  │
│  ┌──────────────┐         ┌──────────────┐         │
│  │ Combat Flow  │         │ CombatStats  │         │
│  │ - Initiative │         │ StatusEffects│         │
│  │ - Rounds     │         │ Defensive    │         │
│  │ - Actions    │         │ Stance       │         │
│  └──────────────┘         └──────────────┘         │
│                                                      │
│  DATA STRUCTURES                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │ AttackType    (Enum)                         │  │
│  │ AttackResult  (Enum)                         │  │
│  │ StatusEffect  (Enum)                         │  │
│  │ AttackConfig  (Dataclass)                    │  │
│  │ CombatAction  (Dataclass)                    │  │
│  │ CombatStats   (Dataclass)                    │  │
│  │ StatusEffectInstance (Dataclass)             │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2. Enemy System (enemies.py)

```
┌─────────────────────────────────────────────────────┐
│               ENEMY SYSTEM MODULE                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐         ┌──────────────┐         │
│  │ EnemyFactory │────────►│EnemyTemplate │         │
│  └──────┬───────┘         └──────┬───────┘         │
│         │                        │                  │
│         │ Creates                │ Defines          │
│         ▼                        ▼                  │
│  ┌──────────────┐         ┌──────────────┐         │
│  │  Character   │         │ Stats        │         │
│  │  (Enemy)     │         │ Behavior     │         │
│  │              │         │ Loot         │         │
│  └──────────────┘         │ Resistances  │         │
│                           └──────────────┘         │
│  ┌──────────────┐         ┌──────────────┐         │
│  │  EnemyAI     │────────►│  Behavior    │         │
│  │              │         │  Patterns    │         │
│  └──────────────┘         └──────────────┘         │
│                                                      │
│  ┌──────────────┐                                   │
│  │LootGenerator │                                   │
│  └──────────────┘                                   │
│                                                      │
│  13 ENEMY TEMPLATES                                 │
│  ┌──────────────────────────────────────────────┐  │
│  │ Basic (3)    Elite (2)   Mini-Boss (1)      │  │
│  │ Boss (2)     World Boss (1)                  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 3. Ability System (abilities.py)

```
┌─────────────────────────────────────────────────────┐
│              ABILITY SYSTEM MODULE                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐         ┌──────────────┐         │
│  │AbilityManager│────────►│ActiveAbility │         │
│  └──────┬───────┘         └──────┬───────┘         │
│         │                        │                  │
│         │ Manages                │ Wraps            │
│         ▼                        ▼                  │
│  ┌──────────────┐         ┌──────────────┐         │
│  │  Cooldowns   │         │   Ability    │         │
│  │  Resources   │         └──────┬───────┘         │
│  │  Activation  │                │                  │
│  └──────────────┘                │ Has              │
│                                  ▼                  │
│                           ┌──────────────┐         │
│                           │AbilityEffect │         │
│                           └──────────────┘         │
│                                                      │
│  24 CLASS ABILITIES                                 │
│  ┌──────────────────────────────────────────────┐  │
│  │ Warrior (4)    Sorcerer (5)   Rogue (4)     │  │
│  │ Paladin (4)    Necro (5)      Ranger (5)    │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Combat Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     COMBAT FLOW                              │
└─────────────────────────────────────────────────────────────┘

    START COMBAT
         │
         ▼
    ┌─────────┐
    │ Init    │─────► Determine Initiative (Player vs Enemy)
    └────┬────┘
         │
         ▼
    ┌─────────────────────────────────────────────┐
    │           ROUND LOOP                        │
    │                                              │
    │  1. Process Status Effects (DoT, Buffs)     │
    │     │                                        │
    │     ▼                                        │
    │  2. Execute Actions (by initiative order)   │
    │     │                                        │
    │     ├──► Action 1: Attacker → Defender      │
    │     │     │                                  │
    │     │     ├─► Check Stamina                 │
    │     │     ├─► Apply Defensive Stance        │
    │     │     ├─► Calculate Hit/Miss            │
    │     │     ├─► Calculate Damage              │
    │     │     ├─► Apply Status Effects          │
    │     │     └─► Log Action                    │
    │     │                                        │
    │     └──► Action 2: Defender → Attacker      │
    │           (same flow)                        │
    │     │                                        │
    │     ▼                                        │
    │  3. Restore Stamina (+10)                   │
    │     │                                        │
    │     ▼                                        │
    │  4. Reset Defensive Stances                 │
    │     │                                        │
    │     ▼                                        │
    │  5. Check Combat End Conditions             │
    │     │                                        │
    │     ├─ Yes ──────────┐                      │
    │     └─ No ───────────┘                      │
    │           │                                  │
    └───────────┘                                  │
                                                   │
                                                   ▼
                                            END COMBAT
                                                   │
                                                   ▼
                                            ┌──────────────┐
                                            │ Calculate    │
                                            │ - Winner     │
                                            │ - Souls      │
                                            │ - XP         │
                                            │ - Loot       │
                                            └──────────────┘
                                                   │
                                                   ▼
                                            ┌──────────────┐
                                            │ Update DB    │
                                            │ - Character  │
                                            │ - Memory     │
                                            │ - Stats      │
                                            └──────────────┘
```

## Action Resolution

```
┌────────────────────────────────────────────────────┐
│              ACTION RESOLUTION                      │
└────────────────────────────────────────────────────┘

    ATTACK ACTION
         │
         ▼
    Check Stamina ────No───► FAIL (Exhausted)
         │
        Yes
         │
         ▼
    Is Defender Dodging? ──Yes──► Roll vs Evasion
         │                             │
         No                            ├─Success──► DODGED
         │                             │
         ▼                             └─Fail─────┐
    Is Defender Parrying? ──Yes──► Roll vs Parry │
         │                             │          │
         No                            ├─Success──┤
         │                             │          │
         ▼                             └─Fail─────┤
    Calculate Hit Chance                          │
         │                                         │
         ▼                                         │
    Roll d100 ───────────────────────────────────┘
         │
         ├─Miss (>accuracy)──► MISS
         │
         └─Hit (≤accuracy)
               │
               ▼
         Roll for Critical
               │
               ├─Yes──► Damage × Crit Multiplier
               │
               └─No───► Base Damage
                        │
                        ▼
                  Apply Stat Modifiers
                        │
                        ▼
                  Apply Defense Mitigation
                        │
                        ▼
                  Apply Blocking (if active)
                        │
                        ▼
                  Deal Final Damage
                        │
                        ▼
                  Apply Status Effect (chance)
                        │
                        ▼
                  Generate Description
                        │
                        ▼
                  Return CombatAction
```

## Status Effect Processing

```
┌────────────────────────────────────────────────────┐
│           STATUS EFFECT PROCESSING                  │
└────────────────────────────────────────────────────┘

    For Each Active Status Effect:
         │
         ▼
    ┌─────────────────────┐
    │ Tick Duration       │─────► Duration - 1
    └──────┬──────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Apply Effect        │
    └──────┬──────────────┘
           │
           ├──► DoT (Bleed, Poison, Burn)
           │    └─► Deal True Damage
           │
           ├──► Heal (Regeneration)
           │    └─► Restore Health
           │
           ├──► Stat Modifier (Weakness, Strength)
           │    └─► Apply to Next Attack
           │
           └──► Control (Stun, Frost)
                └─► Skip Turn / Reduce Speed
           │
           ▼
    Check Expiration
           │
           ├─ Expired ──► Remove Effect
           │
           └─ Active ───► Keep for Next Round
```

## AI Decision Making

```
┌────────────────────────────────────────────────────┐
│              ENEMY AI DECISION TREE                 │
└────────────────────────────────────────────────────┘

    Check Enemy State
         │
         ├─► Health < Enrage Threshold?
         │   └─Yes──► BERSERKER Behavior
         │
         └─No──► Use Template Behavior
                 │
                 ├─► AGGRESSIVE
                 │   └─► 60% Heavy, 30% Light, 10% Block
                 │
                 ├─► DEFENSIVE
                 │   └─► 50% Block/Parry, 30% Light, 20% Heavy
                 │
                 ├─► BALANCED
                 │   └─► Mix all actions evenly
                 │
                 ├─► TACTICAL
                 │   └─► Adapt to player/self health
                 │
                 ├─► BERSERKER
                 │   └─► 80% Heavy, 20% Light (no defense)
                 │
                 └─► COWARD
                     └─► 60% Dodge/Block if hurt
```

## Data Flow

```
┌────────────────────────────────────────────────────┐
│                  DATA FLOW                          │
└────────────────────────────────────────────────────┘

    DATABASE
       │
       ├─► Load Character
       │      │
       │      ▼
       │   COMBAT SYSTEM
       │      │
       │      ├─► Read Stats
       │      ├─► Read Equipment
       │      └─► Calculate Combat Stats
       │             │
       │             ▼
       │      Execute Combat Rounds
       │             │
       │             ├─► Generate Actions
       │             ├─► Apply Effects
       │             └─► Log Events
       │                    │
       └────────────────────┼─► Save Results
                            │     │
                            │     ├─► Update Health
                            │     ├─► Add XP/Souls
                            │     └─► Create Memories
                            │
                            ▼
                    LLM GENERATOR (Optional)
                            │
                            └─► Generate Descriptions
```

## Integration Points

```
┌────────────────────────────────────────────────────┐
│             INTEGRATION ARCHITECTURE                │
└────────────────────────────────────────────────────┘

    ┌─────────────┐
    │  COMBAT     │
    │  SYSTEM     │
    └──────┬──────┘
           │
           ├─────────────┬────────────┬─────────────┐
           │             │            │             │
           ▼             ▼            ▼             ▼
    ┌──────────┐  ┌──────────┐ ┌─────────┐  ┌──────────┐
    │CHARACTER │  │ DATABASE │ │   LLM   │  │  WORLD   │
    │ SYSTEM   │  │  MODELS  │ │GENERATOR│  │  STATE   │
    └──────────┘  └──────────┘ └─────────┘  └──────────┘
         │              │            │             │
         │              │            │             │
         ├─► Stats      ├─► Session  ├─► Prompts   ├─► Reality
         ├─► Manager    ├─► Commit   ├─► Fallback  ├─► Faction
         └─► Inventory  └─► Logging  └─► Cache     └─► Location
```

## Class Relationships

```
CombatSystem
├── player: Combatant
│   ├── character: Character
│   ├── status_effects: List[StatusEffectInstance]
│   ├── combat_stats: CombatStats
│   └── defensive_stance: bool flags
├── enemy: Combatant
│   └── (same structure)
├── combat_log: List[CombatAction]
└── llm: LLMGenerator (optional)

EnemyFactory
└── ENEMY_TEMPLATES: Dict[str, EnemyTemplate]
    └── EnemyTemplate
        ├── stats
        ├── behavior: EnemyBehavior
        ├── resistances: Dict[DamageType, float]
        ├── loot_table
        └── boss_phases (optional)

AbilityManager
├── character: Character
└── abilities: Dict[str, ActiveAbility]
    └── ActiveAbility
        ├── ability: Ability
        │   ├── effects: AbilityEffect
        │   ├── resource_cost
        │   └── cooldown
        └── cooldown_remaining: int
```

## Performance Characteristics

```
┌────────────────────────────────────────────────────┐
│            PERFORMANCE PROFILE                      │
└────────────────────────────────────────────────────┘

Operation                    Time Complexity    Notes
─────────────────────────────────────────────────────
Combat Initialization        O(1)               Fast
Round Execution              O(n)               n = status effects
Status Effect Processing     O(n)               Linear in effects
Damage Calculation           O(1)               Constant time
Action Resolution            O(1)               Direct computation
AI Decision                  O(1)               Simple logic
Ability Usage                O(1)               Hash lookup
Enemy Creation               O(1)               Template copy
Loot Generation              O(m)               m = loot items

Database Operations
─────────────────────────────────────────────────────
Load Character               1 query            Eager loading
Save Combat Results          1 commit           Batched
Create Memory                1 insert           Per combat

LLM Operations
─────────────────────────────────────────────────────
Generate Description         1-3s               API call
With Caching                 <10ms              Hash lookup
```

---

**Version**: 1.0
**Last Updated**: January 18, 2025
