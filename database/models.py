"""
Shards of Eternity - Database Models
SQLAlchemy ORM models for the game database
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class FactionType(enum.Enum):
    """Six major factions vying for control of the Crystal Shards"""
    CRIMSON_COVENANT = "Crimson Covenant"
    AETHER_SEEKERS = "Aether Seekers"
    IRON_BROTHERHOOD = "Iron Brotherhood"
    MOONLIT_CIRCLE = "Moonlit Circle"
    SHADOWBORN = "Shadowborn"
    GOLDEN_ORDER = "Golden Order"


class RaceType(enum.Enum):
    """Playable races in Shards of Eternity"""
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    TIEFLING = "Tiefling"
    DRAGONBORN = "Dragonborn"
    UNDEAD = "Undead"


class ClassType(enum.Enum):
    """Character classes with unique abilities"""
    WARRIOR = "Warrior"
    SORCERER = "Sorcerer"
    ROGUE = "Rogue"
    PALADIN = "Paladin"
    NECROMANCER = "Necromancer"
    RANGER = "Ranger"


class RealityType(enum.Enum):
    """Different reality states based on shard control"""
    BLOOD_REALM = "Blood Realm"
    AETHER_STORM = "Aether Storm"
    IRON_AGE = "Iron Age"
    TWILIGHT_DOMINION = "Twilight Dominion"
    SHADOW_WORLD = "Shadow World"
    RADIANT_ERA = "Radiant Era"
    NEUTRAL = "Neutral"


# ============================================================================
# ASSOCIATION TABLES
# ============================================================================

party_members = Table(
    'party_members',
    Base.metadata,
    Column('party_id', Integer, ForeignKey('parties.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)


# ============================================================================
# MODELS
# ============================================================================

class Character(Base):
    """
    Main character model representing player characters and NPCs
    """
    __tablename__ = 'characters'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic Information
    name = Column(String(100), nullable=False)
    is_player = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Character Identity
    race = Column(Enum(RaceType), nullable=False)
    character_class = Column(Enum(ClassType), nullable=False)
    faction = Column(Enum(FactionType), nullable=False)

    # Core Stats (D&D style)
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    # Resources
    health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    stamina = Column(Integer, default=100)
    max_stamina = Column(Integer, default=100)
    mana = Column(Integer, default=100)
    max_mana = Column(Integer, default=100)

    # Progression
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    souls = Column(Integer, default=0)  # Currency

    # Location
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)

    # Relationships
    location = relationship('Location', back_populates='characters')
    inventory = relationship('InventoryItem', back_populates='character', cascade='all, delete-orphan')
    memories = relationship('CharacterMemory', back_populates='character', cascade='all, delete-orphan')
    shard_captures = relationship('ShardOwnership', back_populates='character', cascade='all, delete-orphan')
    parties = relationship('Party', secondary=party_members, back_populates='members')

    def to_dict(self):
        """Convert character to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'is_player': self.is_player,
            'race': self.race.value if self.race else None,
            'class': self.character_class.value if self.character_class else None,
            'faction': self.faction.value if self.faction else None,
            'stats': {
                'strength': self.strength,
                'dexterity': self.dexterity,
                'intelligence': self.intelligence,
                'constitution': self.constitution,
                'wisdom': self.wisdom,
                'charisma': self.charisma
            },
            'resources': {
                'health': self.health,
                'max_health': self.max_health,
                'stamina': self.stamina,
                'max_stamina': self.max_stamina,
                'mana': self.mana,
                'max_mana': self.max_mana
            },
            'progression': {
                'level': self.level,
                'experience': self.experience,
                'souls': self.souls
            },
            'location_id': self.location_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', level={self.level}, faction={self.faction.value if self.faction else 'None'})>"


class InventoryItem(Base):
    """
    Items owned by characters
    """
    __tablename__ = 'inventory_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)

    # Item Details
    item_name = Column(String(100), nullable=False)
    item_type = Column(String(50))  # weapon, armor, consumable, quest_item, etc.
    description = Column(Text)
    quantity = Column(Integer, default=1)

    # Item Properties
    attack_bonus = Column(Integer, default=0)
    defense_bonus = Column(Integer, default=0)
    magic_bonus = Column(Integer, default=0)
    value = Column(Integer, default=0)  # In souls

    # Metadata
    is_equipped = Column(Boolean, default=False)
    is_quest_item = Column(Boolean, default=False)
    acquired_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    character = relationship('Character', back_populates='inventory')

    def __repr__(self):
        return f"<InventoryItem(id={self.id}, name='{self.item_name}', quantity={self.quantity})>"


class CrystalShard(Base):
    """
    The 12 Crystal Shards that shape reality
    """
    __tablename__ = 'crystal_shards'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Shard Identity
    shard_number = Column(Integer, unique=True, nullable=False)  # 1-12
    shard_name = Column(String(100), nullable=False)
    description = Column(Text)

    # Location and Guardian
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    guardian_boss_name = Column(String(100))
    guardian_defeated = Column(Boolean, default=False)

    # Ownership
    is_captured = Column(Boolean, default=False)
    owning_faction = Column(Enum(FactionType), nullable=True)
    captured_at = Column(DateTime, nullable=True)

    # Power
    reality_influence = Column(String(100))  # What aspect of reality it controls
    power_level = Column(Integer, default=100)

    # Relationships
    location = relationship('Location', back_populates='shards')
    ownership_history = relationship('ShardOwnership', back_populates='shard', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<CrystalShard(id={self.id}, name='{self.shard_name}', faction={self.owning_faction.value if self.owning_faction else 'Unclaimed'})>"


class ShardOwnership(Base):
    """
    Tracks who captured which shard and when
    """
    __tablename__ = 'shard_ownership'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    shard_id = Column(Integer, ForeignKey('crystal_shards.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    faction = Column(Enum(FactionType), nullable=False)

    # Capture Details
    captured_at = Column(DateTime, default=datetime.utcnow)
    lost_at = Column(DateTime, nullable=True)
    is_current_owner = Column(Boolean, default=True)

    # Battle Stats
    guardian_defeated_by = Column(String(200))  # Party members who helped
    souls_earned = Column(Integer, default=0)

    # Relationships
    shard = relationship('CrystalShard', back_populates='ownership_history')
    character = relationship('Character', back_populates='shard_captures')

    def __repr__(self):
        return f"<ShardOwnership(shard_id={self.shard_id}, character_id={self.character_id}, faction={self.faction.value})>"


class WorldState(Base):
    """
    Current state of the world/reality
    Only one active record at a time
    """
    __tablename__ = 'world_state'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Reality State
    current_reality = Column(Enum(RealityType), default=RealityType.NEUTRAL)
    reality_stability = Column(Float, default=100.0)  # 0-100

    # Aetherfall Counter
    aetherfall_count = Column(Integer, default=0)  # Resets when all shards captured
    total_aetherfalls = Column(Integer, default=0)  # Historical count

    # Faction Power
    dominant_faction = Column(Enum(FactionType), nullable=True)
    faction_shard_counts = Column(Text)  # JSON string of faction: count

    # World Stats
    total_souls_in_economy = Column(Integer, default=0)
    active_players = Column(Integer, default=0)
    total_deaths = Column(Integer, default=0)

    # Metadata
    last_aetherfall = Column(DateTime, nullable=True)
    last_reality_shift = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WorldState(reality={self.current_reality.value}, dominant_faction={self.dominant_faction.value if self.dominant_faction else 'None'})>"


class Location(Base):
    """
    Areas in the game world
    """
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Location Details
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    zone_type = Column(String(50))  # town, dungeon, wilderness, faction_hq, etc.

    # Connections (stored as comma-separated location IDs or JSON)
    connected_locations = Column(Text)  # JSON array of location IDs

    # Inhabitants
    npc_list = Column(Text)  # JSON array of NPC names/IDs
    enemy_types = Column(Text)  # JSON array of enemy types

    # Properties
    is_safe_zone = Column(Boolean, default=False)
    faction_controlled = Column(Enum(FactionType), nullable=True)
    danger_level = Column(Integer, default=1)  # 1-10

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    characters = relationship('Character', back_populates='location')
    shards = relationship('CrystalShard', back_populates='location')

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', danger_level={self.danger_level})>"


class CharacterMemory(Base):
    """
    Decision and event log for each character
    Stores important choices, events, and story beats
    """
    __tablename__ = 'character_memories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)

    # Memory Details
    memory_type = Column(String(50))  # decision, event, dialogue, combat, quest, etc.
    title = Column(String(200))
    description = Column(Text, nullable=False)

    # Context
    location_name = Column(String(100))
    npc_involved = Column(String(100))
    faction_impact = Column(String(100))  # Which faction was affected

    # Impact
    souls_gained = Column(Integer, default=0)
    souls_lost = Column(Integer, default=0)
    reputation_change = Column(Integer, default=0)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    game_day = Column(Integer, default=1)  # In-game day counter

    # Relationships
    character = relationship('Character', back_populates='memories')

    def __repr__(self):
        return f"<CharacterMemory(id={self.id}, type='{self.memory_type}', title='{self.title}')>"


class Party(Base):
    """
    Multiplayer parties for cooperative play
    """
    __tablename__ = 'parties'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Party Details
    party_name = Column(String(100))
    leader_id = Column(Integer, ForeignKey('characters.id'))

    # Settings
    is_active = Column(Boolean, default=True)
    max_members = Column(Integer, default=4)
    loot_sharing = Column(String(20), default='equal')  # equal, leader, roll

    # Stats
    total_souls_earned = Column(Integer, default=0)
    shards_captured = Column(Integer, default=0)
    bosses_defeated = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    disbanded_at = Column(DateTime, nullable=True)

    # Relationships
    leader = relationship('Character', foreign_keys=[leader_id])
    members = relationship('Character', secondary=party_members, back_populates='parties')

    def __repr__(self):
        return f"<Party(id={self.id}, name='{self.party_name}', active={self.is_active})>"


class WorldEvent(Base):
    """
    Admin log of major world events
    Tracks significant happenings like shard captures, reality shifts, etc.
    """
    __tablename__ = 'world_events'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Event Details
    event_type = Column(String(50), nullable=False)  # shard_capture, reality_shift, aetherfall, faction_war, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Participants
    character_ids = Column(Text)  # JSON array of involved character IDs
    faction = Column(Enum(FactionType), nullable=True)

    # Impact
    reality_before = Column(Enum(RealityType), nullable=True)
    reality_after = Column(Enum(RealityType), nullable=True)
    shard_id = Column(Integer, ForeignKey('crystal_shards.id'), nullable=True)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    game_day = Column(Integer, default=1)
    broadcast_to_all = Column(Boolean, default=True)  # Show to all players

    # Relationships
    shard = relationship('CrystalShard')

    def __repr__(self):
        return f"<WorldEvent(id={self.id}, type='{self.event_type}', title='{self.title}')>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def init_db(engine):
    """Initialize database with all tables"""
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(engine)
