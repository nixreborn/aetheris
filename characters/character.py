"""
Character creation and management system for Shards of Eternity.

This module provides comprehensive character creation and management functionality,
including stat rolling, validation, inventory management, and experience tracking.
"""
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import random
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.models import (
    Character, RaceType, ClassType, FactionType,
    InventoryItem, CharacterMemory, Location
)
from database import get_db_session

logger = logging.getLogger(__name__)


class CharacterCreationError(Exception):
    """Raised when character creation fails."""
    pass


class CharacterNotFoundError(Exception):
    """Raised when a character cannot be found."""
    pass


class CharacterCreator:
    """
    Handles character creation with validation and stat generation.

    Supports both random stat rolling and point-buy systems.
    """

    # Constants for character creation
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 50
    POINT_BUY_TOTAL = 60  # Total points for point-buy system
    MIN_STAT_VALUE = 3
    MAX_STAT_VALUE = 18
    STARTING_SOULS_MIN = 50
    STARTING_SOULS_MAX = 150

    # Race stat modifiers
    RACE_MODIFIERS = {
        RaceType.HUMAN: {"strength": 1, "dexterity": 1, "constitution": 1, "intelligence": 1, "wisdom": 1, "charisma": 1},
        RaceType.ELF: {"dexterity": 2, "intelligence": 1, "wisdom": 1},
        RaceType.DWARF: {"constitution": 2, "strength": 1, "wisdom": 1},
        RaceType.TIEFLING: {"intelligence": 1, "charisma": 2},
        RaceType.DRAGONBORN: {"strength": 2, "charisma": 1},
        RaceType.UNDEAD: {"constitution": -1, "intelligence": 2, "charisma": -1},
    }

    # Class stat preferences (for recommended builds)
    CLASS_RECOMMENDED_STATS = {
        ClassType.WARRIOR: ["strength", "constitution", "dexterity"],
        ClassType.SORCERER: ["intelligence", "wisdom", "constitution"],
        ClassType.ROGUE: ["dexterity", "charisma", "intelligence"],
        ClassType.PALADIN: ["strength", "charisma", "constitution"],
        ClassType.NECROMANCER: ["intelligence", "wisdom", "charisma"],
        ClassType.RANGER: ["dexterity", "wisdom", "constitution"],
    }

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize the character creator.

        Args:
            session: Database session. If None, uses context manager.
        """
        self._external_session = session

    def _get_session(self):
        """Get database session (either external or context manager)."""
        if self._external_session:
            return self._external_session
        return get_db_session()

    def validate_name(self, name: str, session: Optional[Session] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate character name.

        Args:
            name: The character name to validate
            session: Optional database session

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check length
        if len(name) < self.MIN_NAME_LENGTH:
            return False, f"Name must be at least {self.MIN_NAME_LENGTH} characters long"

        if len(name) > self.MAX_NAME_LENGTH:
            return False, f"Name must be no more than {self.MAX_NAME_LENGTH} characters long"

        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c in " '-" for c in name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"

        # Check for uniqueness
        use_context = session is None
        if use_context:
            with get_db_session() as session:
                existing = session.query(Character).filter(Character.name == name).first()
        else:
            existing = session.query(Character).filter(Character.name == name).first()

        if existing:
            return False, f"Character name '{name}' is already taken"

        return True, None

    def roll_stats(self, method: str = "4d6_drop_lowest") -> Dict[str, int]:
        """
        Roll character stats using various methods.

        Args:
            method: Rolling method - "4d6_drop_lowest", "3d6", "heroic" (4d6 drop lowest reroll 1s)

        Returns:
            Dictionary of stat names to values
        """
        stats = {}
        stat_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        for stat in stat_names:
            if method == "3d6":
                stats[stat] = sum(random.randint(1, 6) for _ in range(3))
            elif method == "4d6_drop_lowest":
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.remove(min(rolls))
                stats[stat] = sum(rolls)
            elif method == "heroic":
                rolls = [max(random.randint(1, 6), 2) for _ in range(4)]  # Reroll 1s
                rolls.remove(min(rolls))
                stats[stat] = sum(rolls)
            else:
                stats[stat] = 10  # Default to 10

        return stats

    def point_buy_stats(self, allocations: Dict[str, int]) -> Tuple[bool, Optional[str], Dict[str, int]]:
        """
        Validate and apply point-buy stat allocation.

        Args:
            allocations: Dictionary of stat names to point allocations (before racial modifiers)

        Returns:
            Tuple of (is_valid, error_message, final_stats)
        """
        stat_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        # Validate all stats are present
        if not all(stat in allocations for stat in stat_names):
            return False, "All stats must be allocated", {}

        # Validate stat ranges
        for stat, value in allocations.items():
            if value < self.MIN_STAT_VALUE or value > self.MAX_STAT_VALUE:
                return False, f"Stat {stat} must be between {self.MIN_STAT_VALUE} and {self.MAX_STAT_VALUE}", {}

        # Validate total points
        total_points = sum(allocations.values())
        if total_points != self.POINT_BUY_TOTAL:
            return False, f"Total stat points must equal {self.POINT_BUY_TOTAL} (current: {total_points})", {}

        return True, None, allocations

    def apply_racial_modifiers(self, base_stats: Dict[str, int], race: RaceType) -> Dict[str, int]:
        """
        Apply racial stat modifiers to base stats.

        Args:
            base_stats: Base stat values
            race: Character race

        Returns:
            Modified stat dictionary
        """
        modified_stats = base_stats.copy()
        modifiers = self.RACE_MODIFIERS.get(race, {})

        for stat, modifier in modifiers.items():
            modified_stats[stat] = modified_stats.get(stat, 10) + modifier

        return modified_stats

    def calculate_starting_resources(
        self,
        character_class: ClassType,
        constitution: int,
        intelligence: int,
        wisdom: int
    ) -> Dict[str, int]:
        """
        Calculate starting health, stamina, and mana based on class and stats.

        Args:
            character_class: Character class
            constitution: Constitution score
            intelligence: Intelligence score
            wisdom: Wisdom score

        Returns:
            Dictionary with max_health, max_stamina, max_mana
        """
        con_mod = (constitution - 10) // 2
        int_mod = (intelligence - 10) // 2
        wis_mod = (wisdom - 10) // 2

        # Base values by class
        class_resources = {
            ClassType.WARRIOR: {"health": 120, "stamina": 120, "mana": 50},
            ClassType.SORCERER: {"health": 70, "stamina": 70, "mana": 150},
            ClassType.ROGUE: {"health": 90, "stamina": 130, "mana": 60},
            ClassType.PALADIN: {"health": 110, "stamina": 100, "mana": 90},
            ClassType.NECROMANCER: {"health": 80, "stamina": 80, "mana": 140},
            ClassType.RANGER: {"health": 95, "stamina": 110, "mana": 80},
        }

        base = class_resources.get(character_class, {"health": 100, "stamina": 100, "mana": 100})

        return {
            "max_health": base["health"] + (con_mod * 5),
            "max_stamina": base["stamina"] + (con_mod * 3),
            "max_mana": base["mana"] + (int_mod * 5) + (wis_mod * 3),
        }

    def create_character(
        self,
        name: str,
        race: RaceType,
        character_class: ClassType,
        faction: FactionType,
        description: str = "",
        stats: Optional[Dict[str, int]] = None,
        stat_method: str = "4d6_drop_lowest",
        starting_location_id: Optional[int] = None,
        is_player: bool = True
    ) -> Character:
        """
        Create a new character with full validation and initialization.

        Args:
            name: Character name
            race: Character race
            character_class: Character class
            faction: Character faction
            description: Character description
            stats: Pre-defined stats (if None, will roll)
            stat_method: Method for rolling stats if stats not provided
            starting_location_id: Starting location ID
            is_player: Whether this is a player character (vs NPC)

        Returns:
            Created Character object

        Raises:
            CharacterCreationError: If character creation fails
        """
        with get_db_session() as session:
            # Validate name
            is_valid, error = self.validate_name(name, session)
            if not is_valid:
                raise CharacterCreationError(error)

            # Generate or validate stats
            if stats is None:
                stats = self.roll_stats(stat_method)

            # Apply racial modifiers
            final_stats = self.apply_racial_modifiers(stats, race)

            # Calculate resources
            resources = self.calculate_starting_resources(
                character_class,
                final_stats["constitution"],
                final_stats["intelligence"],
                final_stats["wisdom"]
            )

            # Generate starting souls (currency)
            starting_souls = random.randint(self.STARTING_SOULS_MIN, self.STARTING_SOULS_MAX)

            # Create character
            character = Character(
                name=name,
                is_player=is_player,
                race=race,
                character_class=character_class,
                faction=faction,
                strength=final_stats["strength"],
                dexterity=final_stats["dexterity"],
                constitution=final_stats["constitution"],
                intelligence=final_stats["intelligence"],
                wisdom=final_stats["wisdom"],
                charisma=final_stats["charisma"],
                max_health=resources["max_health"],
                health=resources["max_health"],
                max_stamina=resources["max_stamina"],
                stamina=resources["max_stamina"],
                max_mana=resources["max_mana"],
                mana=resources["max_mana"],
                souls=starting_souls,
                location_id=starting_location_id
            )

            try:
                session.add(character)
                session.commit()
                session.refresh(character)

                logger.info(f"Created character: {character.name} (ID: {character.id})")

                # Add starting items
                self._add_starting_items(character.id, character_class, session)

                # Add creation memory
                self._add_memory(
                    character.id,
                    "character_creation",
                    f"{character.name} began their journey as a {race.value} {character_class.value}",
                    f"{character.name} joined the {faction.value} faction",
                    session=session
                )

                return character

            except IntegrityError as e:
                session.rollback()
                logger.error(f"Database error creating character: {e}")
                raise CharacterCreationError(f"Failed to create character: {e}")

    def _add_starting_items(self, character_id: int, character_class: ClassType, session: Session):
        """Add starting equipment based on class."""
        starting_items = {
            ClassType.WARRIOR: [
                {
                    "item_name": "Iron Longsword",
                    "item_type": "weapon",
                    "description": "A sturdy iron longsword, well-balanced for combat.",
                    "attack_bonus": 10,
                    "value": 50
                },
                {
                    "item_name": "Leather Armor",
                    "item_type": "armor",
                    "description": "Basic leather armor providing modest protection.",
                    "defense_bonus": 5,
                    "value": 40
                },
                {
                    "item_name": "Health Potion",
                    "item_type": "consumable",
                    "description": "Restores 50 health points.",
                    "quantity": 3,
                    "value": 20
                },
            ],
            ClassType.SORCERER: [
                {
                    "item_name": "Wooden Staff",
                    "item_type": "weapon",
                    "description": "A simple staff imbued with magical energy.",
                    "attack_bonus": 5,
                    "magic_bonus": 8,
                    "value": 60
                },
                {
                    "item_name": "Cloth Robes",
                    "item_type": "armor",
                    "description": "Light robes that enhance magical abilities.",
                    "defense_bonus": 2,
                    "magic_bonus": 5,
                    "value": 45
                },
                {
                    "item_name": "Mana Potion",
                    "item_type": "consumable",
                    "description": "Restores 50 mana points.",
                    "quantity": 5,
                    "value": 25
                },
            ],
            ClassType.ROGUE: [
                {
                    "item_name": "Steel Dagger",
                    "item_type": "weapon",
                    "description": "A sharp dagger perfect for quick strikes.",
                    "attack_bonus": 8,
                    "value": 45
                },
                {
                    "item_name": "Light Leather Armor",
                    "item_type": "armor",
                    "description": "Lightweight armor for stealth and agility.",
                    "defense_bonus": 3,
                    "value": 35
                },
                {
                    "item_name": "Lockpick Set",
                    "item_type": "tool",
                    "description": "A set of tools for opening locks.",
                    "quantity": 1,
                    "value": 30
                },
            ],
            ClassType.PALADIN: [
                {
                    "item_name": "Blessed Mace",
                    "item_type": "weapon",
                    "description": "A mace blessed with holy power.",
                    "attack_bonus": 9,
                    "magic_bonus": 3,
                    "value": 70
                },
                {
                    "item_name": "Chainmail Armor",
                    "item_type": "armor",
                    "description": "Heavy chainmail providing solid protection.",
                    "defense_bonus": 7,
                    "value": 80
                },
                {
                    "item_name": "Holy Water",
                    "item_type": "consumable",
                    "description": "Blessed water that heals and protects.",
                    "quantity": 2,
                    "value": 30
                },
            ],
            ClassType.NECROMANCER: [
                {
                    "item_name": "Bone Staff",
                    "item_type": "weapon",
                    "description": "A staff crafted from ancient bones.",
                    "attack_bonus": 4,
                    "magic_bonus": 10,
                    "value": 65
                },
                {
                    "item_name": "Dark Robes",
                    "item_type": "armor",
                    "description": "Robes steeped in necromantic energy.",
                    "defense_bonus": 2,
                    "magic_bonus": 6,
                    "value": 50
                },
                {
                    "item_name": "Soul Gem",
                    "item_type": "quest_item",
                    "description": "A gem used to capture and store souls.",
                    "quantity": 1,
                    "is_quest_item": True,
                    "value": 100
                },
            ],
            ClassType.RANGER: [
                {
                    "item_name": "Hunting Bow",
                    "item_type": "weapon",
                    "description": "A well-crafted bow for ranged combat.",
                    "attack_bonus": 9,
                    "value": 55
                },
                {
                    "item_name": "Leather Armor",
                    "item_type": "armor",
                    "description": "Flexible leather armor for mobility.",
                    "defense_bonus": 4,
                    "value": 40
                },
                {
                    "item_name": "Arrows",
                    "item_type": "consumable",
                    "description": "Standard arrows for your bow.",
                    "quantity": 50,
                    "value": 10
                },
            ],
        }

        items = starting_items.get(character_class, [
            {
                "item_name": "Basic Weapon",
                "item_type": "weapon",
                "description": "A basic weapon.",
                "attack_bonus": 5,
                "value": 20
            },
            {
                "item_name": "Basic Armor",
                "item_type": "armor",
                "description": "Basic protective armor.",
                "defense_bonus": 3,
                "value": 20
            },
        ])

        for item_data in items:
            item = InventoryItem(
                character_id=character_id,
                **item_data
            )
            session.add(item)

        session.commit()

    def _add_memory(
        self,
        character_id: int,
        memory_type: str,
        title: str,
        description: str,
        session: Session,
        location_name: Optional[str] = None,
        souls_gained: int = 0
    ):
        """Add a memory to character."""
        memory = CharacterMemory(
            character_id=character_id,
            memory_type=memory_type,
            title=title,
            description=description,
            location_name=location_name,
            souls_gained=souls_gained
        )
        session.add(memory)
        session.commit()


class CharacterManager:
    """
    Manages character operations including updates, inventory, and progression.
    """

    # Experience thresholds for leveling (XP needed to reach each level)
    EXPERIENCE_PER_LEVEL = [
        0,      # Level 1
        100,    # Level 2
        300,    # Level 3
        600,    # Level 4
        1000,   # Level 5
        1500,   # Level 6
        2100,   # Level 7
        2800,   # Level 8
        3600,   # Level 9
        4500,   # Level 10
        5500,   # Level 11
        6600,   # Level 12
        7800,   # Level 13
        9100,   # Level 14
        10500,  # Level 15
        12000,  # Level 16
        13600,  # Level 17
        15300,  # Level 18
        17100,  # Level 19
        19000,  # Level 20
        21000,  # Level 21
        23100,  # Level 22
        25300,  # Level 23
        27600,  # Level 24
        30000,  # Level 25
    ]

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize the character manager.

        Args:
            session: Database session. If None, uses context manager.
        """
        self._external_session = session

    def load_character(self, character_id: Optional[int] = None, name: Optional[str] = None) -> Character:
        """
        Load a character from the database.

        Args:
            character_id: Character ID (takes precedence)
            name: Character name

        Returns:
            Character object

        Raises:
            CharacterNotFoundError: If character not found
        """
        if not character_id and not name:
            raise ValueError("Must provide either character_id or name")

        with get_db_session() as session:
            if character_id:
                character = session.query(Character).filter(Character.id == character_id).first()
            else:
                character = session.query(Character).filter(Character.name == name).first()

            if not character:
                raise CharacterNotFoundError(f"Character not found: {character_id or name}")

            # Update last access timestamp
            character.updated_at = datetime.utcnow()
            session.commit()

            return character

    def update_health(self, character_id: int, amount: int) -> int:
        """
        Update character health (can be positive or negative).

        Args:
            character_id: Character ID
            amount: Health change (positive for healing, negative for damage)

        Returns:
            New current health value
        """
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            character.health = max(0, min(character.max_health, character.health + amount))
            session.commit()

            logger.info(f"Character {character.name} health: {character.health}/{character.max_health}")

            # Log if character died
            if character.health == 0:
                logger.warning(f"Character {character.name} has died!")
                self._add_death_memory(character_id, session)

            return character.health

    def update_stamina(self, character_id: int, amount: int) -> int:
        """Update character stamina."""
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            character.stamina = max(0, min(character.max_stamina, character.stamina + amount))
            session.commit()

            return character.stamina

    def update_mana(self, character_id: int, amount: int) -> int:
        """Update character mana."""
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            character.mana = max(0, min(character.max_mana, character.mana + amount))
            session.commit()

            return character.mana

    def add_experience(self, character_id: int, amount: int) -> Tuple[int, bool, int]:
        """
        Add experience to character and check for level up.

        Args:
            character_id: Character ID
            amount: Experience to add

        Returns:
            Tuple of (new_experience, leveled_up, new_level)
        """
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            old_level = character.level
            character.experience += amount
            leveled_up = False

            # Check for level up (potentially multiple levels)
            while self._should_level_up(character):
                self._level_up_character(character, session)
                leveled_up = True

            session.commit()

            if leveled_up:
                logger.info(f"Character {character.name} leveled up from {old_level} to {character.level}!")

            return character.experience, leveled_up, character.level

    def _should_level_up(self, character: Character) -> bool:
        """Check if character should level up."""
        if character.level >= len(self.EXPERIENCE_PER_LEVEL):
            # Max level reached
            return False

        return character.experience >= self.EXPERIENCE_PER_LEVEL[character.level]

    def _level_up_character(self, character: Character, session: Session):
        """Level up character and increase stats."""
        old_level = character.level
        character.level += 1

        # Calculate stat increases based on class
        stat_increases = self._calculate_level_up_stats(character.character_class)

        # Apply stat increases
        character.strength += stat_increases.get("strength", 0)
        character.dexterity += stat_increases.get("dexterity", 0)
        character.constitution += stat_increases.get("constitution", 0)
        character.intelligence += stat_increases.get("intelligence", 0)
        character.wisdom += stat_increases.get("wisdom", 0)
        character.charisma += stat_increases.get("charisma", 0)

        # Recalculate max resources
        resources = CharacterCreator().calculate_starting_resources(
            character.character_class,
            character.constitution,
            character.intelligence,
            character.wisdom
        )

        # Increase max resources based on level
        health_per_level = 10
        stamina_per_level = 8
        mana_per_level = 12

        character.max_health = resources["max_health"] + ((character.level - 1) * health_per_level)
        character.max_stamina = resources["max_stamina"] + ((character.level - 1) * stamina_per_level)
        character.max_mana = resources["max_mana"] + ((character.level - 1) * mana_per_level)

        # Fully restore resources on level up
        character.health = character.max_health
        character.stamina = character.max_stamina
        character.mana = character.max_mana

        logger.info(f"Character {character.name} leveled up: {old_level} -> {character.level}")

        # Add memory
        memory = CharacterMemory(
            character_id=character.id,
            memory_type="level_up",
            title=f"Level Up: {character.level}",
            description=f"Reached level {character.level} and gained increased power",
        )
        session.add(memory)

    def _calculate_level_up_stats(self, character_class: ClassType) -> Dict[str, int]:
        """Calculate stat increases on level up based on class."""
        base_increase = {
            "strength": 0, "dexterity": 0, "constitution": 1,
            "intelligence": 0, "wisdom": 0, "charisma": 0
        }

        class_bonuses = {
            ClassType.WARRIOR: {"strength": 2, "constitution": 1},
            ClassType.SORCERER: {"intelligence": 2, "wisdom": 1},
            ClassType.ROGUE: {"dexterity": 2, "charisma": 1},
            ClassType.PALADIN: {"strength": 1, "charisma": 1, "constitution": 1},
            ClassType.NECROMANCER: {"intelligence": 2, "charisma": 1},
            ClassType.RANGER: {"dexterity": 1, "wisdom": 1, "constitution": 1},
        }

        bonuses = class_bonuses.get(character_class, {})
        for stat, value in bonuses.items():
            base_increase[stat] += value

        return base_increase

    def add_item_to_inventory(
        self,
        character_id: int,
        item_name: str,
        item_type: str,
        quantity: int = 1,
        description: str = "",
        attack_bonus: int = 0,
        defense_bonus: int = 0,
        magic_bonus: int = 0,
        value: int = 0,
        is_quest_item: bool = False
    ) -> InventoryItem:
        """
        Add an item to character's inventory.

        Args:
            character_id: Character ID
            item_name: Name of the item
            item_type: Type of item (weapon, armor, consumable, etc.)
            quantity: Item quantity
            description: Item description
            attack_bonus: Attack bonus (for weapons)
            defense_bonus: Defense bonus (for armor)
            magic_bonus: Magic bonus
            value: Item value in souls
            is_quest_item: Whether this is a quest item

        Returns:
            Created InventoryItem
        """
        with get_db_session() as session:
            # Check if character exists
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            # Check if item already exists (for stackable items)
            existing = session.query(InventoryItem).filter(
                InventoryItem.character_id == character_id,
                InventoryItem.item_name == item_name,
                InventoryItem.item_type == item_type
            ).first()

            if existing and item_type in ["consumable", "misc"] and not is_quest_item:
                # Stack items
                existing.quantity += quantity
                session.commit()
                logger.info(f"Added {quantity}x {item_name} to {character.name}'s inventory (stacked)")
                return existing
            else:
                # Create new item
                item = InventoryItem(
                    character_id=character_id,
                    item_name=item_name,
                    item_type=item_type,
                    quantity=quantity,
                    description=description,
                    attack_bonus=attack_bonus,
                    defense_bonus=defense_bonus,
                    magic_bonus=magic_bonus,
                    value=value,
                    is_quest_item=is_quest_item
                )
                session.add(item)
                session.commit()
                session.refresh(item)

                logger.info(f"Added {quantity}x {item_name} to {character.name}'s inventory")
                return item

    def remove_item_from_inventory(self, character_id: int, item_id: int, quantity: int = 1) -> bool:
        """
        Remove an item from character's inventory.

        Args:
            character_id: Character ID
            item_id: Item ID to remove
            quantity: Quantity to remove

        Returns:
            True if item removed/reduced, False if not found
        """
        with get_db_session() as session:
            item = session.query(InventoryItem).filter(
                InventoryItem.id == item_id,
                InventoryItem.character_id == character_id
            ).first()

            if not item:
                return False

            if item.quantity <= quantity:
                # Remove entire item
                item_name = item.item_name
                session.delete(item)
                logger.info(f"Removed {item_name} from inventory")
            else:
                # Reduce quantity
                item.quantity -= quantity
                logger.info(f"Reduced {item.item_name} quantity by {quantity}")

            session.commit()
            return True

    def equip_item(self, character_id: int, item_id: int) -> bool:
        """
        Equip an item (toggle equipped status).

        Args:
            character_id: Character ID
            item_id: Item ID to equip

        Returns:
            True if equipped successfully
        """
        with get_db_session() as session:
            item = session.query(InventoryItem).filter(
                InventoryItem.id == item_id,
                InventoryItem.character_id == character_id
            ).first()

            if not item:
                return False

            # Can only equip weapons and armor
            if item.item_type not in ["weapon", "armor"]:
                logger.warning(f"Cannot equip {item.item_type}")
                return False

            # Unequip other items of the same type
            if not item.is_equipped:
                session.query(InventoryItem).filter(
                    InventoryItem.character_id == character_id,
                    InventoryItem.item_type == item.item_type,
                    InventoryItem.is_equipped == True
                ).update({"is_equipped": False})

            # Toggle equipped status
            item.is_equipped = not item.is_equipped

            session.commit()
            logger.info(f"{'Equipped' if item.is_equipped else 'Unequipped'} {item.item_name}")
            return True

    def change_location(self, character_id: int, location_id: int) -> bool:
        """
        Move character to a new location.

        Args:
            character_id: Character ID
            location_id: New location ID

        Returns:
            True if location changed successfully
        """
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            location = session.query(Location).filter(Location.id == location_id).first()
            if not location:
                logger.warning(f"Location {location_id} not found")
                return False

            old_location_id = character.location_id
            character.location_id = location_id

            # Add travel memory
            memory = CharacterMemory(
                character_id=character_id,
                memory_type="travel",
                title=f"Traveled to {location.name}",
                description=f"Journeyed to {location.name}",
                location_name=location.name
            )
            session.add(memory)
            session.commit()

            logger.info(f"Character {character.name} moved to {location.name}")
            return True

    def add_memory(
        self,
        character_id: int,
        memory_type: str,
        title: str,
        description: str,
        location_name: Optional[str] = None,
        npc_involved: Optional[str] = None,
        faction_impact: Optional[str] = None,
        souls_gained: int = 0,
        souls_lost: int = 0,
        reputation_change: int = 0
    ) -> CharacterMemory:
        """
        Add a memory/event to character's history.

        Args:
            character_id: Character ID
            memory_type: Type of event (quest, combat, dialogue, etc.)
            title: Memory title
            description: Event description
            location_name: Location name where event occurred
            npc_involved: NPC name if applicable
            faction_impact: Faction affected
            souls_gained: Souls gained from event
            souls_lost: Souls lost in event
            reputation_change: Reputation change

        Returns:
            Created CharacterMemory
        """
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            memory = CharacterMemory(
                character_id=character_id,
                memory_type=memory_type,
                title=title,
                description=description,
                location_name=location_name,
                npc_involved=npc_involved,
                faction_impact=faction_impact,
                souls_gained=souls_gained,
                souls_lost=souls_lost,
                reputation_change=reputation_change
            )

            session.add(memory)
            session.commit()
            session.refresh(memory)

            logger.info(f"Added memory for {character.name}: {title}")
            return memory

    def _add_death_memory(self, character_id: int, session: Session):
        """Add a death memory when character dies."""
        memory = CharacterMemory(
            character_id=character_id,
            memory_type="death",
            title="Fell in Battle",
            description="Your vision fades to black as your life force ebbs away..."
        )
        session.add(memory)
        session.commit()

    def get_character_memories(
        self,
        character_id: int,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[CharacterMemory]:
        """
        Get character's recent memories.

        Args:
            character_id: Character ID
            memory_type: Filter by memory type (optional)
            limit: Maximum number of memories to return

        Returns:
            List of CharacterMemory objects
        """
        with get_db_session() as session:
            query = session.query(CharacterMemory).filter(
                CharacterMemory.character_id == character_id
            )

            if memory_type:
                query = query.filter(CharacterMemory.memory_type == memory_type)

            memories = query.order_by(CharacterMemory.timestamp.desc()).limit(limit).all()

            return memories

    def calculate_derived_stats(self, character: Character) -> Dict[str, Any]:
        """
        Calculate all derived stats from base stats.

        Args:
            character: Character object

        Returns:
            Dictionary of derived stats (modifiers, AC, initiative, etc.)
        """
        def stat_modifier(stat_value: int) -> int:
            return (stat_value - 10) // 2

        # Get equipped bonuses
        equipped_items = [item for item in character.inventory if item.is_equipped]
        total_attack_bonus = sum(item.attack_bonus for item in equipped_items)
        total_defense_bonus = sum(item.defense_bonus for item in equipped_items)
        total_magic_bonus = sum(item.magic_bonus for item in equipped_items)

        return {
            "stat_modifiers": {
                "strength": stat_modifier(character.strength),
                "dexterity": stat_modifier(character.dexterity),
                "constitution": stat_modifier(character.constitution),
                "intelligence": stat_modifier(character.intelligence),
                "wisdom": stat_modifier(character.wisdom),
                "charisma": stat_modifier(character.charisma),
            },
            "armor_class": 10 + stat_modifier(character.dexterity) + total_defense_bonus,
            "initiative": stat_modifier(character.dexterity),
            "attack_power": stat_modifier(character.strength) + total_attack_bonus,
            "magic_power": stat_modifier(character.intelligence) + total_magic_bonus,
            "health_per_level": 10 + stat_modifier(character.constitution),
            "mana_per_level": 12 + stat_modifier(character.intelligence),
            "stamina_per_level": 8 + stat_modifier(character.constitution),
            "equipment_bonuses": {
                "attack": total_attack_bonus,
                "defense": total_defense_bonus,
                "magic": total_magic_bonus,
            }
        }

    def get_character_summary(self, character_id: int) -> Dict[str, Any]:
        """
        Get a complete summary of character data.

        Args:
            character_id: Character ID

        Returns:
            Dictionary with all character information
        """
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            inventory = session.query(InventoryItem).filter(
                InventoryItem.character_id == character_id
            ).all()

            equipped = [item for item in inventory if item.is_equipped]
            unequipped = [item for item in inventory if not item.is_equipped]

            derived_stats = self.calculate_derived_stats(character)

            # Calculate XP needed for next level
            next_level_xp = None
            if character.level < len(self.EXPERIENCE_PER_LEVEL):
                next_level_xp = self.EXPERIENCE_PER_LEVEL[character.level] - character.experience

            return {
                "id": character.id,
                "name": character.name,
                "is_player": character.is_player,
                "race": character.race.value,
                "class": character.character_class.value,
                "faction": character.faction.value,
                "level": character.level,
                "experience": character.experience,
                "next_level_xp": next_level_xp,
                "stats": {
                    "strength": character.strength,
                    "dexterity": character.dexterity,
                    "constitution": character.constitution,
                    "intelligence": character.intelligence,
                    "wisdom": character.wisdom,
                    "charisma": character.charisma,
                },
                "derived_stats": derived_stats,
                "resources": {
                    "health": f"{character.health}/{character.max_health}",
                    "stamina": f"{character.stamina}/{character.max_stamina}",
                    "mana": f"{character.mana}/{character.max_mana}",
                },
                "souls": character.souls,
                "location": character.location.name if character.location else "Unknown",
                "location_id": character.location_id,
                "equipped_items": [
                    {
                        "id": item.id,
                        "name": item.item_name,
                        "type": item.item_type,
                        "attack_bonus": item.attack_bonus,
                        "defense_bonus": item.defense_bonus,
                        "magic_bonus": item.magic_bonus
                    }
                    for item in equipped
                ],
                "inventory_items": [
                    {
                        "id": item.id,
                        "name": item.item_name,
                        "type": item.item_type,
                        "quantity": item.quantity,
                        "value": item.value
                    }
                    for item in unequipped
                ],
                "total_inventory_value": sum(item.value * item.quantity for item in inventory),
                "created_at": character.created_at.isoformat() if character.created_at else None,
                "updated_at": character.updated_at.isoformat() if character.updated_at else None,
            }

    def add_souls(self, character_id: int, amount: int) -> int:
        """
        Add souls (currency) to character.

        Args:
            character_id: Character ID
            amount: Souls to add (can be negative)

        Returns:
            New souls total
        """
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            character.souls = max(0, character.souls + amount)
            session.commit()

            logger.info(f"Character {character.name} souls: {character.souls} ({'+' if amount >= 0 else ''}{amount})")
            return character.souls

    def rest_character(self, character_id: int, full_rest: bool = True) -> Dict[str, int]:
        """
        Rest to restore character resources.

        Args:
            character_id: Character ID
            full_rest: If True, fully restore all resources. If False, restore 50%.

        Returns:
            Dictionary with restored amounts
        """
        with get_db_session() as session:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise CharacterNotFoundError(f"Character {character_id} not found")

            if full_rest:
                health_restored = character.max_health - character.health
                stamina_restored = character.max_stamina - character.stamina
                mana_restored = character.max_mana - character.mana

                character.health = character.max_health
                character.stamina = character.max_stamina
                character.mana = character.max_mana
            else:
                # Partial rest - restore 50%
                health_restore = character.max_health // 2
                stamina_restore = character.max_stamina // 2
                mana_restore = character.max_mana // 2

                health_restored = min(health_restore, character.max_health - character.health)
                stamina_restored = min(stamina_restore, character.max_stamina - character.stamina)
                mana_restored = min(mana_restore, character.max_mana - character.mana)

                character.health = min(character.max_health, character.health + health_restore)
                character.stamina = min(character.max_stamina, character.stamina + stamina_restore)
                character.mana = min(character.max_mana, character.mana + mana_restore)

            # Add memory
            memory = CharacterMemory(
                character_id=character_id,
                memory_type="rest",
                title="Rested and Recovered",
                description=f"{'Fully recovered' if full_rest else 'Partially recovered'} health, stamina, and mana"
            )
            session.add(memory)
            session.commit()

            logger.info(f"Character {character.name} rested ({'full' if full_rest else 'partial'})")

            return {
                "health_restored": health_restored,
                "stamina_restored": stamina_restored,
                "mana_restored": mana_restored
            }
