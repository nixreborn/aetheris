"""
Enemy System for Shards of Eternity.

Defines enemy types, AI behaviors, loot tables, and boss mechanics.
"""
import random
import logging
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass

from sqlalchemy.orm import Session

from database.models import Character, ClassType, RaceType, FactionType
from database import get_db_session
from characters.character import CharacterCreator

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class EnemyType(Enum):
    """Enemy difficulty tiers."""
    BASIC = "basic"
    ELITE = "elite"
    MINI_BOSS = "mini_boss"
    BOSS = "boss"
    WORLD_BOSS = "world_boss"


class EnemyBehavior(Enum):
    """AI behavior patterns for enemies."""
    AGGRESSIVE = "aggressive"  # Prefers heavy attacks
    DEFENSIVE = "defensive"  # Prefers blocking/parrying
    BALANCED = "balanced"  # Mix of all actions
    TACTICAL = "tactical"  # Uses abilities strategically
    BERSERKER = "berserker"  # All-out offense, ignores defense
    COWARD = "coward"  # Tries to escape when low health


class DamageType(Enum):
    """Types of damage for resistances."""
    PHYSICAL = "physical"
    FIRE = "fire"
    FROST = "frost"
    LIGHTNING = "lightning"
    POISON = "poison"
    DARK = "dark"
    HOLY = "holy"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class EnemyTemplate:
    """Template for creating enemy instances."""
    name: str
    enemy_type: EnemyType
    level: int
    behavior: EnemyBehavior

    # Base stats (before modifiers)
    base_health: int
    base_stamina: int
    base_strength: int
    base_dexterity: int
    base_constitution: int
    base_intelligence: int

    # Special properties
    resistances: Dict[DamageType, float] = None  # 0.0 = immune, 1.0 = normal, 2.0 = weak
    special_abilities: List[str] = None
    loot_table: Dict[str, Any] = None

    # Boss mechanics
    boss_phases: List[Dict[str, Any]] = None  # For multi-phase bosses
    enrage_threshold: float = 0.25  # HP % to enrage

    def __post_init__(self):
        if self.resistances is None:
            self.resistances = {dt: 1.0 for dt in DamageType}
        if self.special_abilities is None:
            self.special_abilities = []
        if self.loot_table is None:
            self.loot_table = self._generate_default_loot_table()
        if self.boss_phases is None:
            self.boss_phases = []

    def _generate_default_loot_table(self) -> Dict[str, Any]:
        """Generate default loot based on enemy type."""
        base_souls = {
            EnemyType.BASIC: (10, 30),
            EnemyType.ELITE: (50, 100),
            EnemyType.MINI_BOSS: (150, 300),
            EnemyType.BOSS: (500, 1000),
            EnemyType.WORLD_BOSS: (2000, 5000)
        }

        return {
            "souls": base_souls[self.enemy_type],
            "items": [],
            "guaranteed_drops": []
        }


# ============================================================================
# ENEMY TEMPLATES
# ============================================================================

ENEMY_TEMPLATES = {
    # ========== BASIC ENEMIES ==========
    "hollow_soldier": EnemyTemplate(
        name="Hollow Soldier",
        enemy_type=EnemyType.BASIC,
        level=1,
        behavior=EnemyBehavior.BALANCED,
        base_health=50,
        base_stamina=80,
        base_strength=10,
        base_dexterity=8,
        base_constitution=10,
        base_intelligence=6,
        resistances={
            DamageType.PHYSICAL: 1.0,
            DamageType.FIRE: 1.2,
            DamageType.FROST: 0.8,
            DamageType.LIGHTNING: 1.0,
            DamageType.POISON: 0.5,
            DamageType.DARK: 0.8,
            DamageType.HOLY: 1.5
        },
        loot_table={
            "souls": (10, 25),
            "items": [
                {"name": "Rusty Sword", "chance": 0.1},
                {"name": "Tattered Armor", "chance": 0.05},
                {"name": "Health Potion", "chance": 0.3}
            ]
        }
    ),

    "corrupt_wolf": EnemyTemplate(
        name="Corrupt Wolf",
        enemy_type=EnemyType.BASIC,
        level=2,
        behavior=EnemyBehavior.AGGRESSIVE,
        base_health=60,
        base_stamina=100,
        base_strength=12,
        base_dexterity=14,
        base_constitution=8,
        base_intelligence=4,
        resistances={
            DamageType.PHYSICAL: 0.9,
            DamageType.FIRE: 1.3,
            DamageType.FROST: 1.0,
            DamageType.LIGHTNING: 1.0,
            DamageType.POISON: 0.7,
            DamageType.DARK: 1.2,
            DamageType.HOLY: 1.0
        },
        special_abilities=["bleed_bite"],
        loot_table={
            "souls": (15, 35),
            "items": [
                {"name": "Wolf Pelt", "chance": 0.4},
                {"name": "Sharp Fang", "chance": 0.2}
            ]
        }
    ),

    "skeleton_warrior": EnemyTemplate(
        name="Skeleton Warrior",
        enemy_type=EnemyType.BASIC,
        level=3,
        behavior=EnemyBehavior.DEFENSIVE,
        base_health=70,
        base_stamina=70,
        base_strength=11,
        base_dexterity=10,
        base_constitution=8,
        base_intelligence=5,
        resistances={
            DamageType.PHYSICAL: 0.8,
            DamageType.FIRE: 1.0,
            DamageType.FROST: 0.5,
            DamageType.LIGHTNING: 1.0,
            DamageType.POISON: 0.0,  # Immune
            DamageType.DARK: 0.7,
            DamageType.HOLY: 1.8
        },
        loot_table={
            "souls": (20, 40),
            "items": [
                {"name": "Bone Fragment", "chance": 0.5},
                {"name": "Ancient Coin", "chance": 0.15}
            ]
        }
    ),

    # ========== ELITE ENEMIES ==========
    "dark_knight": EnemyTemplate(
        name="Dark Knight",
        enemy_type=EnemyType.ELITE,
        level=5,
        behavior=EnemyBehavior.TACTICAL,
        base_health=150,
        base_stamina=120,
        base_strength=16,
        base_dexterity=14,
        base_constitution=15,
        base_intelligence=10,
        resistances={
            DamageType.PHYSICAL: 0.7,
            DamageType.FIRE: 0.9,
            DamageType.FROST: 1.0,
            DamageType.LIGHTNING: 1.1,
            DamageType.POISON: 0.6,
            DamageType.DARK: 0.5,
            DamageType.HOLY: 1.5
        },
        special_abilities=["dark_wave", "shield_bash"],
        loot_table={
            "souls": (80, 150),
            "items": [
                {"name": "Dark Steel Sword", "chance": 0.15},
                {"name": "Knight's Shield", "chance": 0.1},
                {"name": "Greater Health Potion", "chance": 0.4}
            ],
            "guaranteed_drops": ["Dark Fragment"]
        }
    ),

    "frost_mage": EnemyTemplate(
        name="Frost Mage",
        enemy_type=EnemyType.ELITE,
        level=6,
        behavior=EnemyBehavior.TACTICAL,
        base_health=100,
        base_stamina=150,
        base_strength=8,
        base_dexterity=12,
        base_constitution=10,
        base_intelligence=18,
        resistances={
            DamageType.PHYSICAL: 1.2,
            DamageType.FIRE: 1.8,
            DamageType.FROST: 0.3,
            DamageType.LIGHTNING: 1.0,
            DamageType.POISON: 1.0,
            DamageType.DARK: 0.9,
            DamageType.HOLY: 1.0
        },
        special_abilities=["frost_bolt", "ice_shield", "freeze"],
        loot_table={
            "souls": (100, 180),
            "items": [
                {"name": "Frost Staff", "chance": 0.12},
                {"name": "Mage Robes", "chance": 0.08},
                {"name": "Mana Potion", "chance": 0.5}
            ],
            "guaranteed_drops": ["Frozen Crystal"]
        }
    ),

    # ========== MINI-BOSSES ==========
    "corrupted_guardian": EnemyTemplate(
        name="Corrupted Guardian",
        enemy_type=EnemyType.MINI_BOSS,
        level=8,
        behavior=EnemyBehavior.DEFENSIVE,
        base_health=300,
        base_stamina=150,
        base_strength=18,
        base_dexterity=10,
        base_constitution=20,
        base_intelligence=12,
        resistances={
            DamageType.PHYSICAL: 0.6,
            DamageType.FIRE: 0.8,
            DamageType.FROST: 0.8,
            DamageType.LIGHTNING: 1.2,
            DamageType.POISON: 0.5,
            DamageType.DARK: 0.7,
            DamageType.HOLY: 1.3
        },
        special_abilities=["ground_slam", "corrupted_aura", "regeneration"],
        enrage_threshold=0.3,
        loot_table={
            "souls": (200, 350),
            "items": [
                {"name": "Guardian's Greatsword", "chance": 0.2},
                {"name": "Heavy Armor Set", "chance": 0.15},
            ],
            "guaranteed_drops": ["Guardian Soul", "Titanite Shard"]
        }
    ),

    # ========== BOSSES ==========
    "lord_of_cinders": EnemyTemplate(
        name="Lord of Cinders",
        enemy_type=EnemyType.BOSS,
        level=10,
        behavior=EnemyBehavior.AGGRESSIVE,
        base_health=500,
        base_stamina=200,
        base_strength=22,
        base_dexterity=16,
        base_constitution=20,
        base_intelligence=15,
        resistances={
            DamageType.PHYSICAL: 0.8,
            DamageType.FIRE: 0.3,
            DamageType.FROST: 1.5,
            DamageType.LIGHTNING: 1.0,
            DamageType.POISON: 0.6,
            DamageType.DARK: 0.9,
            DamageType.HOLY: 1.2
        },
        special_abilities=["flame_wave", "cinder_storm", "burning_blade", "resurrection"],
        boss_phases=[
            {
                "hp_threshold": 0.5,
                "abilities_unlocked": ["cinder_storm"],
                "stat_changes": {"strength": +5, "speed": +2}
            },
            {
                "hp_threshold": 0.25,
                "abilities_unlocked": ["resurrection"],
                "stat_changes": {"strength": +8, "fire_damage": +50}
            }
        ],
        enrage_threshold=0.15,
        loot_table={
            "souls": (800, 1200),
            "items": [
                {"name": "Cinder Blade", "chance": 0.3},
                {"name": "Ashen Crown", "chance": 0.2},
                {"name": "Fire Gem", "chance": 0.4}
            ],
            "guaranteed_drops": ["Lord Soul", "Cinder Heart", "Boss Key"]
        }
    ),

    "crystal_shard_guardian": EnemyTemplate(
        name="Crystal Shard Guardian",
        enemy_type=EnemyType.BOSS,
        level=12,
        behavior=EnemyBehavior.TACTICAL,
        base_health=600,
        base_stamina=250,
        base_strength=20,
        base_dexterity=18,
        base_constitution=22,
        base_intelligence=20,
        resistances={
            DamageType.PHYSICAL: 0.7,
            DamageType.FIRE: 1.0,
            DamageType.FROST: 1.0,
            DamageType.LIGHTNING: 0.5,
            DamageType.POISON: 0.4,
            DamageType.DARK: 1.3,
            DamageType.HOLY: 0.8
        },
        special_abilities=["crystal_spear", "shard_barrier", "reality_distortion", "summon_minions"],
        boss_phases=[
            {
                "hp_threshold": 0.66,
                "abilities_unlocked": ["shard_barrier"],
                "summons": ["hollow_soldier", "hollow_soldier"]
            },
            {
                "hp_threshold": 0.33,
                "abilities_unlocked": ["reality_distortion"],
                "stat_changes": {"all_resistances": -0.2}
            }
        ],
        enrage_threshold=0.1,
        loot_table={
            "souls": (1000, 1500),
            "guaranteed_drops": ["Crystal Shard", "Guardian's Essence", "Legendary Weapon Fragment"]
        }
    ),

    # ========== WORLD BOSS ==========
    "aetherfall_titan": EnemyTemplate(
        name="Aetherfall Titan",
        enemy_type=EnemyType.WORLD_BOSS,
        level=20,
        behavior=EnemyBehavior.BERSERKER,
        base_health=2000,
        base_stamina=500,
        base_strength=30,
        base_dexterity=15,
        base_constitution=35,
        base_intelligence=25,
        resistances={
            DamageType.PHYSICAL: 0.6,
            DamageType.FIRE: 0.7,
            DamageType.FROST: 0.7,
            DamageType.LIGHTNING: 0.7,
            DamageType.POISON: 0.3,
            DamageType.DARK: 0.8,
            DamageType.HOLY: 0.9
        },
        special_abilities=[
            "titan_slam", "aether_beam", "reality_tear", "earthquake",
            "summon_adds", "enrage", "phase_shift"
        ],
        boss_phases=[
            {"hp_threshold": 0.75, "abilities_unlocked": ["aether_beam"]},
            {"hp_threshold": 0.50, "abilities_unlocked": ["reality_tear", "summon_adds"]},
            {"hp_threshold": 0.25, "abilities_unlocked": ["phase_shift", "enrage"]}
        ],
        enrage_threshold=0.1,
        loot_table={
            "souls": (3000, 6000),
            "guaranteed_drops": [
                "Titan's Heart",
                "Aether Crystal",
                "Legendary Armor Set",
                "Mythic Weapon"
            ]
        }
    ),
}


# ============================================================================
# ENEMY FACTORY
# ============================================================================

class EnemyFactory:
    """Factory for creating enemy instances from templates."""

    @staticmethod
    def create_enemy(
        template_name: str,
        level_override: Optional[int] = None,
        session: Optional[Session] = None
    ) -> Character:
        """
        Create an enemy Character from a template.

        Args:
            template_name: Name of the enemy template
            level_override: Optional level override
            session: Database session

        Returns:
            Character object representing the enemy
        """
        if template_name not in ENEMY_TEMPLATES:
            raise ValueError(f"Unknown enemy template: {template_name}")

        template = ENEMY_TEMPLATES[template_name]
        level = level_override or template.level

        # Calculate level-scaled stats
        level_multiplier = 1 + ((level - 1) * 0.15)

        stats = {
            "strength": int(template.base_strength * level_multiplier),
            "dexterity": int(template.base_dexterity * level_multiplier),
            "constitution": int(template.base_constitution * level_multiplier),
            "intelligence": int(template.base_intelligence * level_multiplier),
            "wisdom": 10,
            "charisma": 5
        }

        health = int(template.base_health * level_multiplier)
        stamina = int(template.base_stamina * level_multiplier)

        # Create character using CharacterCreator
        use_context = session is None
        if use_context:
            with get_db_session() as session:
                enemy = Character(
                    name=f"{template.name} (Lv{level})",
                    is_player=False,
                    race=RaceType.UNDEAD,  # Most enemies are undead/monsters
                    character_class=ClassType.WARRIOR,  # Default class
                    faction=FactionType.SHADOWBORN,  # Enemy faction
                    level=level,
                    **stats,
                    health=health,
                    max_health=health,
                    stamina=stamina,
                    max_stamina=stamina,
                    mana=50,
                    max_mana=50
                )
                session.add(enemy)
                session.commit()
                session.refresh(enemy)
        else:
            enemy = Character(
                name=f"{template.name} (Lv{level})",
                is_player=False,
                race=RaceType.UNDEAD,
                character_class=ClassType.WARRIOR,
                faction=FactionType.SHADOWBORN,
                level=level,
                **stats,
                health=health,
                max_health=health,
                stamina=stamina,
                max_stamina=stamina,
                mana=50,
                max_mana=50
            )
            session.add(enemy)
            session.commit()
            session.refresh(enemy)

        logger.info(f"Created enemy: {enemy.name}")
        return enemy

    @staticmethod
    def get_random_enemy_for_level(
        player_level: int,
        enemy_type: Optional[EnemyType] = None,
        session: Optional[Session] = None
    ) -> Character:
        """
        Get a random enemy appropriate for player level.

        Args:
            player_level: Player's level
            enemy_type: Optional specific enemy type to filter by
            session: Database session

        Returns:
            Random enemy Character
        """
        # Filter templates by type if specified
        if enemy_type:
            candidates = [
                name for name, template in ENEMY_TEMPLATES.items()
                if template.enemy_type == enemy_type
            ]
        else:
            candidates = list(ENEMY_TEMPLATES.keys())

        # Filter by appropriate level range
        level_filtered = []
        for name in candidates:
            template = ENEMY_TEMPLATES[name]
            level_diff = abs(template.level - player_level)

            # Basic enemies: ±2 levels
            # Elite: ±3 levels
            # Bosses: any level
            max_diff = {
                EnemyType.BASIC: 2,
                EnemyType.ELITE: 3,
                EnemyType.MINI_BOSS: 5,
                EnemyType.BOSS: 999,
                EnemyType.WORLD_BOSS: 999
            }

            if level_diff <= max_diff[template.enemy_type]:
                level_filtered.append(name)

        if not level_filtered:
            # Fallback to basic enemy
            level_filtered = ["hollow_soldier"]

        # Pick random enemy
        chosen = random.choice(level_filtered)
        return EnemyFactory.create_enemy(chosen, session=session)

    @staticmethod
    def get_template(template_name: str) -> EnemyTemplate:
        """Get an enemy template by name."""
        if template_name not in ENEMY_TEMPLATES:
            raise ValueError(f"Unknown enemy template: {template_name}")
        return ENEMY_TEMPLATES[template_name]

    @staticmethod
    def list_enemies(enemy_type: Optional[EnemyType] = None) -> List[str]:
        """
        List available enemy templates.

        Args:
            enemy_type: Optional filter by enemy type

        Returns:
            List of enemy template names
        """
        if enemy_type:
            return [
                name for name, template in ENEMY_TEMPLATES.items()
                if template.enemy_type == enemy_type
            ]
        return list(ENEMY_TEMPLATES.keys())


# ============================================================================
# LOOT SYSTEM
# ============================================================================

class LootGenerator:
    """Handles loot generation from enemies."""

    @staticmethod
    def generate_loot(template: EnemyTemplate) -> Dict[str, Any]:
        """
        Generate loot drops from an enemy.

        Args:
            template: Enemy template

        Returns:
            Dictionary with souls and items
        """
        loot_table = template.loot_table
        result = {
            "souls": 0,
            "items": []
        }

        # Generate souls
        souls_range = loot_table.get("souls", (0, 0))
        result["souls"] = random.randint(souls_range[0], souls_range[1])

        # Guaranteed drops
        guaranteed = loot_table.get("guaranteed_drops", [])
        result["items"].extend(guaranteed)

        # Random drops
        items = loot_table.get("items", [])
        for item in items:
            if random.random() < item.get("chance", 0.1):
                result["items"].append(item["name"])

        logger.debug(
            f"Generated loot from {template.name}: "
            f"{result['souls']} souls, {len(result['items'])} items"
        )

        return result


# ============================================================================
# AI BEHAVIOR SYSTEM
# ============================================================================

class EnemyAI:
    """AI system for enemy combat decisions."""

    @staticmethod
    def choose_action(
        enemy_template: EnemyTemplate,
        enemy_health_percent: float,
        enemy_stamina: int,
        player_health_percent: float
    ) -> str:
        """
        Choose an action based on enemy behavior and current state.

        Args:
            enemy_template: Enemy template
            enemy_health_percent: Enemy's current health percentage
            enemy_stamina: Enemy's current stamina
            player_health_percent: Player's health percentage

        Returns:
            Action name as string
        """
        behavior = enemy_template.behavior

        # Check for enrage
        if enemy_health_percent <= enemy_template.enrage_threshold:
            # Enraged enemies are aggressive
            behavior = EnemyBehavior.BERSERKER

        # Behavior-based decision making
        if behavior == EnemyBehavior.AGGRESSIVE:
            return EnemyAI._aggressive_ai(enemy_stamina)

        elif behavior == EnemyBehavior.DEFENSIVE:
            return EnemyAI._defensive_ai(enemy_stamina, enemy_health_percent)

        elif behavior == EnemyBehavior.BALANCED:
            return EnemyAI._balanced_ai(enemy_stamina)

        elif behavior == EnemyBehavior.TACTICAL:
            return EnemyAI._tactical_ai(
                enemy_stamina, enemy_health_percent, player_health_percent
            )

        elif behavior == EnemyBehavior.BERSERKER:
            return EnemyAI._berserker_ai(enemy_stamina)

        elif behavior == EnemyBehavior.COWARD:
            return EnemyAI._coward_ai(enemy_stamina, enemy_health_percent)

        return "light_attack"  # Default

    @staticmethod
    def _aggressive_ai(stamina: int) -> str:
        """Aggressive behavior - prefers heavy attacks."""
        if stamina >= 35 and random.random() < 0.6:
            return "heavy_attack"
        elif stamina >= 15:
            return "light_attack"
        return "block"

    @staticmethod
    def _defensive_ai(stamina: int, health_percent: float) -> str:
        """Defensive behavior - focuses on blocking and parrying."""
        if health_percent < 0.3:
            # Low health - be more defensive
            if stamina >= 25 and random.random() < 0.5:
                return "parry"
            return "block"

        rand = random.random()
        if rand < 0.3 and stamina >= 25:
            return "parry"
        elif rand < 0.5 and stamina >= 10:
            return "block"
        elif stamina >= 15:
            return "light_attack"
        return "block"

    @staticmethod
    def _balanced_ai(stamina: int) -> str:
        """Balanced behavior - mix of all actions."""
        if stamina < 15:
            return "block"

        rand = random.random()
        if rand < 0.3 and stamina >= 15:
            return "light_attack"
        elif rand < 0.5 and stamina >= 35:
            return "heavy_attack"
        elif rand < 0.7 and stamina >= 20:
            return "dodge"
        elif rand < 0.85 and stamina >= 25:
            return "parry"
        return "block"

    @staticmethod
    def _tactical_ai(stamina: int, health_percent: float, player_health_percent: float) -> str:
        """Tactical behavior - adapts to situation."""
        # If player is low, go aggressive
        if player_health_percent < 0.3:
            return EnemyAI._aggressive_ai(stamina)

        # If self is low, go defensive
        if health_percent < 0.4:
            return EnemyAI._defensive_ai(stamina, health_percent)

        # Otherwise balanced
        return EnemyAI._balanced_ai(stamina)

    @staticmethod
    def _berserker_ai(stamina: int) -> str:
        """Berserker behavior - all-out offense."""
        if stamina >= 35 and random.random() < 0.8:
            return "heavy_attack"
        elif stamina >= 15:
            return "light_attack"
        # Even when low stamina, never defend much
        return "light_attack" if random.random() < 0.7 else "block"

    @staticmethod
    def _coward_ai(stamina: int, health_percent: float) -> str:
        """Coward behavior - defensive when hurt."""
        if health_percent < 0.5:
            # Mostly defend when hurt
            if stamina >= 20 and random.random() < 0.6:
                return "dodge"
            return "block"

        # When healthy, fight normally
        return EnemyAI._balanced_ai(stamina)
