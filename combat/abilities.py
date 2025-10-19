"""
Class-specific Abilities System for Shards of Eternity.

Implements unique abilities for each character class with:
- Stamina/Mana costs
- Cooldown system
- Area-of-Effect abilities
- Class-specific mechanics
"""
import logging
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from database.models import Character, ClassType
from combat.system import StatusEffect, StatusEffectInstance

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class ResourceType(Enum):
    """Type of resource consumed by ability."""
    STAMINA = "stamina"
    MANA = "mana"
    HEALTH = "health"
    SOULS = "souls"


class TargetType(Enum):
    """Ability targeting type."""
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    SINGLE_ALLY = "single_ally"
    ALL_ALLIES = "all_allies"
    AREA = "area"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AbilityEffect:
    """Effect of an ability."""
    damage: int = 0
    healing: int = 0
    status_effect: Optional[StatusEffect] = None
    status_duration: int = 0
    status_potency: int = 0
    stat_buff: Optional[Dict[str, int]] = None
    buff_duration: int = 0


@dataclass
class Ability:
    """Class ability definition."""
    name: str
    description: str
    class_type: ClassType

    # Resource costs
    resource_type: ResourceType
    resource_cost: int

    # Cooldown (in rounds)
    cooldown: int

    # Targeting
    target_type: TargetType

    # Effects
    effects: AbilityEffect

    # Scaling with stats
    scales_with: List[str]  # e.g., ["strength", "intelligence"]
    scaling_factor: float = 1.0

    # Special flags
    can_critical: bool = True
    ignores_defense: bool = False
    requires_weapon: bool = False


@dataclass
class ActiveAbility:
    """Instance of an ability in active use."""
    ability: Ability
    cooldown_remaining: int = 0
    times_used: int = 0

    def is_ready(self) -> bool:
        """Check if ability is off cooldown."""
        return self.cooldown_remaining <= 0

    def use(self):
        """Use the ability and start cooldown."""
        self.cooldown_remaining = self.ability.cooldown
        self.times_used += 1

    def tick_cooldown(self):
        """Reduce cooldown by 1 (called each round)."""
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1


# ============================================================================
# ABILITY DEFINITIONS
# ============================================================================

# ========== WARRIOR ABILITIES ==========
WARRIOR_ABILITIES = [
    Ability(
        name="Whirlwind Strike",
        description="A powerful spinning attack that hits all nearby enemies",
        class_type=ClassType.WARRIOR,
        resource_type=ResourceType.STAMINA,
        resource_cost=40,
        cooldown=3,
        target_type=TargetType.ALL_ENEMIES,
        effects=AbilityEffect(damage=25),
        scales_with=["strength", "dexterity"],
        scaling_factor=1.5
    ),
    Ability(
        name="Shield Bash",
        description="Bash an enemy with your shield, dealing damage and stunning them",
        class_type=ClassType.WARRIOR,
        resource_type=ResourceType.STAMINA,
        resource_cost=30,
        cooldown=2,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(
            damage=20,
            status_effect=StatusEffect.STUN,
            status_duration=1,
            status_potency=0
        ),
        scales_with=["strength"],
        scaling_factor=1.2,
        requires_weapon=True
    ),
    Ability(
        name="Battle Cry",
        description="Unleash a war cry that boosts your attack power",
        class_type=ClassType.WARRIOR,
        resource_type=ResourceType.STAMINA,
        resource_cost=25,
        cooldown=4,
        target_type=TargetType.SELF,
        effects=AbilityEffect(
            status_effect=StatusEffect.STRENGTH_BUFF,
            status_duration=3,
            status_potency=0
        ),
        scales_with=[],
        can_critical=False
    ),
    Ability(
        name="Execute",
        description="Devastating attack that deals massive damage to low-health enemies",
        class_type=ClassType.WARRIOR,
        resource_type=ResourceType.STAMINA,
        resource_cost=50,
        cooldown=5,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(damage=60),  # Extra damage if target < 30% HP
        scales_with=["strength"],
        scaling_factor=2.0,
        can_critical=True
    ),
]

# ========== SORCERER ABILITIES ==========
SORCERER_ABILITIES = [
    Ability(
        name="Fireball",
        description="Launch a ball of fire at your enemy",
        class_type=ClassType.SORCERER,
        resource_type=ResourceType.MANA,
        resource_cost=30,
        cooldown=1,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(
            damage=35,
            status_effect=StatusEffect.BURN,
            status_duration=3,
            status_potency=5
        ),
        scales_with=["intelligence"],
        scaling_factor=2.0,
        ignores_defense=True
    ),
    Ability(
        name="Ice Storm",
        description="Summon a storm of ice that damages and slows all enemies",
        class_type=ClassType.SORCERER,
        resource_type=ResourceType.MANA,
        resource_cost=50,
        cooldown=4,
        target_type=TargetType.ALL_ENEMIES,
        effects=AbilityEffect(
            damage=25,
            status_effect=StatusEffect.FROST,
            status_duration=2,
            status_potency=3
        ),
        scales_with=["intelligence", "wisdom"],
        scaling_factor=1.8,
        ignores_defense=True
    ),
    Ability(
        name="Mana Shield",
        description="Convert mana into a protective barrier",
        class_type=ClassType.SORCERER,
        resource_type=ResourceType.MANA,
        resource_cost=40,
        cooldown=3,
        target_type=TargetType.SELF,
        effects=AbilityEffect(
            status_effect=StatusEffect.DEFENSE_BUFF,
            status_duration=3,
            status_potency=0
        ),
        scales_with=["intelligence"],
        can_critical=False
    ),
    Ability(
        name="Lightning Bolt",
        description="Strike your enemy with a bolt of lightning",
        class_type=ClassType.SORCERER,
        resource_type=ResourceType.MANA,
        resource_cost=35,
        cooldown=2,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(damage=45),
        scales_with=["intelligence"],
        scaling_factor=2.2,
        ignores_defense=True,
        can_critical=True
    ),
    Ability(
        name="Arcane Regeneration",
        description="Channel arcane energy to restore health over time",
        class_type=ClassType.SORCERER,
        resource_type=ResourceType.MANA,
        resource_cost=45,
        cooldown=5,
        target_type=TargetType.SELF,
        effects=AbilityEffect(
            status_effect=StatusEffect.REGENERATION,
            status_duration=5,
            status_potency=8
        ),
        scales_with=["wisdom"],
        can_critical=False
    ),
]

# ========== ROGUE ABILITIES ==========
ROGUE_ABILITIES = [
    Ability(
        name="Backstab",
        description="Strike from the shadows for massive critical damage",
        class_type=ClassType.ROGUE,
        resource_type=ResourceType.STAMINA,
        resource_cost=35,
        cooldown=3,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(damage=40),
        scales_with=["dexterity", "strength"],
        scaling_factor=2.5,
        can_critical=True  # Guaranteed critical
    ),
    Ability(
        name="Poison Blade",
        description="Coat your weapon in deadly poison",
        class_type=ClassType.ROGUE,
        resource_type=ResourceType.STAMINA,
        resource_cost=25,
        cooldown=4,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(
            damage=15,
            status_effect=StatusEffect.POISON,
            status_duration=5,
            status_potency=7
        ),
        scales_with=["dexterity"],
        scaling_factor=1.3
    ),
    Ability(
        name="Shadow Step",
        description="Teleport behind your enemy and gain evasion",
        class_type=ClassType.ROGUE,
        resource_type=ResourceType.STAMINA,
        resource_cost=30,
        cooldown=3,
        target_type=TargetType.SELF,
        effects=AbilityEffect(
            damage=0,
            # Would give evasion buff in full implementation
        ),
        scales_with=[],
        can_critical=False
    ),
    Ability(
        name="Fan of Knives",
        description="Throw multiple knives at all enemies",
        class_type=ClassType.ROGUE,
        resource_type=ResourceType.STAMINA,
        resource_cost=45,
        cooldown=4,
        target_type=TargetType.ALL_ENEMIES,
        effects=AbilityEffect(
            damage=20,
            status_effect=StatusEffect.BLEED,
            status_duration=3,
            status_potency=4
        ),
        scales_with=["dexterity"],
        scaling_factor=1.6
    ),
]

# ========== PALADIN ABILITIES ==========
PALADIN_ABILITIES = [
    Ability(
        name="Divine Smite",
        description="Channel holy energy into a devastating strike",
        class_type=ClassType.PALADIN,
        resource_type=ResourceType.MANA,
        resource_cost=35,
        cooldown=2,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(damage=40),
        scales_with=["strength", "charisma"],
        scaling_factor=1.8,
        can_critical=True
    ),
    Ability(
        name="Lay on Hands",
        description="Heal yourself with divine magic",
        class_type=ClassType.PALADIN,
        resource_type=ResourceType.MANA,
        resource_cost=40,
        cooldown=4,
        target_type=TargetType.SELF,
        effects=AbilityEffect(healing=50),
        scales_with=["charisma", "wisdom"],
        scaling_factor=2.0,
        can_critical=False
    ),
    Ability(
        name="Holy Shield",
        description="Summon a shield of light that protects you",
        class_type=ClassType.PALADIN,
        resource_type=ResourceType.MANA,
        resource_cost=30,
        cooldown=5,
        target_type=TargetType.SELF,
        effects=AbilityEffect(
            status_effect=StatusEffect.DEFENSE_BUFF,
            status_duration=4,
            status_potency=0
        ),
        scales_with=[],
        can_critical=False
    ),
    Ability(
        name="Judgement",
        description="Call down holy wrath on all enemies",
        class_type=ClassType.PALADIN,
        resource_type=ResourceType.MANA,
        resource_cost=60,
        cooldown=5,
        target_type=TargetType.ALL_ENEMIES,
        effects=AbilityEffect(damage=30),
        scales_with=["strength", "charisma"],
        scaling_factor=1.5,
        ignores_defense=True
    ),
]

# ========== NECROMANCER ABILITIES ==========
NECROMANCER_ABILITIES = [
    Ability(
        name="Death Bolt",
        description="Fire a bolt of necrotic energy",
        class_type=ClassType.NECROMANCER,
        resource_type=ResourceType.MANA,
        resource_cost=30,
        cooldown=1,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(damage=35),
        scales_with=["intelligence"],
        scaling_factor=2.0,
        ignores_defense=True
    ),
    Ability(
        name="Life Drain",
        description="Drain life from your enemy to heal yourself",
        class_type=ClassType.NECROMANCER,
        resource_type=ResourceType.MANA,
        resource_cost=40,
        cooldown=3,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(
            damage=30,
            healing=20  # Heal for portion of damage
        ),
        scales_with=["intelligence"],
        scaling_factor=1.5
    ),
    Ability(
        name="Curse of Weakness",
        description="Curse an enemy, reducing their attack power",
        class_type=ClassType.NECROMANCER,
        resource_type=ResourceType.MANA,
        resource_cost=35,
        cooldown=4,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(
            status_effect=StatusEffect.WEAKNESS,
            status_duration=4,
            status_potency=0
        ),
        scales_with=[],
        can_critical=False
    ),
    Ability(
        name="Dark Ritual",
        description="Sacrifice health to restore mana",
        class_type=ClassType.NECROMANCER,
        resource_type=ResourceType.HEALTH,
        resource_cost=30,
        cooldown=3,
        target_type=TargetType.SELF,
        effects=AbilityEffect(
            # Converts health to mana in implementation
        ),
        scales_with=[],
        can_critical=False
    ),
    Ability(
        name="Plague Cloud",
        description="Summon a cloud of disease that poisons all enemies",
        class_type=ClassType.NECROMANCER,
        resource_type=ResourceType.MANA,
        resource_cost=55,
        cooldown=5,
        target_type=TargetType.ALL_ENEMIES,
        effects=AbilityEffect(
            damage=15,
            status_effect=StatusEffect.POISON,
            status_duration=4,
            status_potency=8
        ),
        scales_with=["intelligence"],
        scaling_factor=1.3
    ),
]

# ========== RANGER ABILITIES ==========
RANGER_ABILITIES = [
    Ability(
        name="Precise Shot",
        description="A carefully aimed shot with increased critical chance",
        class_type=ClassType.RANGER,
        resource_type=ResourceType.STAMINA,
        resource_cost=25,
        cooldown=2,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(damage=35),
        scales_with=["dexterity"],
        scaling_factor=2.0,
        can_critical=True  # Enhanced critical
    ),
    Ability(
        name="Multi-Shot",
        description="Fire arrows at all enemies",
        class_type=ClassType.RANGER,
        resource_type=ResourceType.STAMINA,
        resource_cost=40,
        cooldown=3,
        target_type=TargetType.ALL_ENEMIES,
        effects=AbilityEffect(damage=20),
        scales_with=["dexterity"],
        scaling_factor=1.5
    ),
    Ability(
        name="Hunter's Mark",
        description="Mark an enemy, increasing damage dealt to them",
        class_type=ClassType.RANGER,
        resource_type=ResourceType.STAMINA,
        resource_cost=20,
        cooldown=4,
        target_type=TargetType.SINGLE_ENEMY,
        effects=AbilityEffect(
            # Would apply mark debuff in full implementation
        ),
        scales_with=[],
        can_critical=False
    ),
    Ability(
        name="Nature's Blessing",
        description="Call upon nature to heal your wounds",
        class_type=ClassType.RANGER,
        resource_type=ResourceType.MANA,
        resource_cost=35,
        cooldown=4,
        target_type=TargetType.SELF,
        effects=AbilityEffect(
            healing=40,
            status_effect=StatusEffect.REGENERATION,
            status_duration=3,
            status_potency=5
        ),
        scales_with=["wisdom"],
        scaling_factor=1.5,
        can_critical=False
    ),
    Ability(
        name="Explosive Arrow",
        description="Fire an arrow that explodes on impact",
        class_type=ClassType.RANGER,
        resource_type=ResourceType.STAMINA,
        resource_cost=50,
        cooldown=5,
        target_type=TargetType.AREA,
        effects=AbilityEffect(
            damage=40,
            status_effect=StatusEffect.BURN,
            status_duration=2,
            status_potency=6
        ),
        scales_with=["dexterity"],
        scaling_factor=1.8
    ),
]


# ============================================================================
# ABILITY MAPPING
# ============================================================================

CLASS_ABILITIES = {
    ClassType.WARRIOR: WARRIOR_ABILITIES,
    ClassType.SORCERER: SORCERER_ABILITIES,
    ClassType.ROGUE: ROGUE_ABILITIES,
    ClassType.PALADIN: PALADIN_ABILITIES,
    ClassType.NECROMANCER: NECROMANCER_ABILITIES,
    ClassType.RANGER: RANGER_ABILITIES,
}


# ============================================================================
# ABILITY MANAGER
# ============================================================================

class AbilityManager:
    """Manages character abilities and their usage."""

    def __init__(self, character: Character):
        """
        Initialize ability manager for a character.

        Args:
            character: Character to manage abilities for
        """
        self.character = character
        self.abilities: Dict[str, ActiveAbility] = {}

        # Load class abilities
        self._load_abilities()

    def _load_abilities(self):
        """Load all abilities for character's class."""
        class_abilities = CLASS_ABILITIES.get(self.character.character_class, [])

        for ability in class_abilities:
            self.abilities[ability.name] = ActiveAbility(ability=ability)

        logger.debug(
            f"Loaded {len(self.abilities)} abilities for "
            f"{self.character.name} ({self.character.character_class.value})"
        )

    def get_available_abilities(self) -> List[Dict[str, Any]]:
        """
        Get list of abilities that are ready to use.

        Returns:
            List of ability dictionaries with details
        """
        available = []

        for name, active_ability in self.abilities.items():
            ability = active_ability.ability
            is_ready = active_ability.is_ready()

            # Check resource availability
            can_afford = self._can_afford_ability(ability)

            available.append({
                "name": name,
                "description": ability.description,
                "resource_type": ability.resource_type.value,
                "resource_cost": ability.resource_cost,
                "cooldown_remaining": active_ability.cooldown_remaining,
                "is_ready": is_ready,
                "can_afford": can_afford,
                "can_use": is_ready and can_afford,
                "target_type": ability.target_type.value,
                "times_used": active_ability.times_used
            })

        return available

    def _can_afford_ability(self, ability: Ability) -> bool:
        """Check if character has enough resources for ability."""
        if ability.resource_type == ResourceType.STAMINA:
            return self.character.stamina >= ability.resource_cost
        elif ability.resource_type == ResourceType.MANA:
            return self.character.mana >= ability.resource_cost
        elif ability.resource_type == ResourceType.HEALTH:
            return self.character.health > ability.resource_cost
        elif ability.resource_type == ResourceType.SOULS:
            return self.character.souls >= ability.resource_cost
        return False

    def use_ability(
        self,
        ability_name: str,
        target: Optional[Character] = None
    ) -> Tuple[bool, str, Optional[AbilityEffect]]:
        """
        Use an ability.

        Args:
            ability_name: Name of ability to use
            target: Target character (if applicable)

        Returns:
            Tuple of (success, message, effect)
        """
        if ability_name not in self.abilities:
            return False, f"Unknown ability: {ability_name}", None

        active_ability = self.abilities[ability_name]
        ability = active_ability.ability

        # Check if ready
        if not active_ability.is_ready():
            return False, f"{ability_name} is on cooldown ({active_ability.cooldown_remaining} rounds)", None

        # Check if can afford
        if not self._can_afford_ability(ability):
            return False, f"Not enough {ability.resource_type.value} for {ability_name}", None

        # Consume resources
        self._consume_resources(ability)

        # Use ability
        active_ability.use()

        # Calculate effects with scaling
        effect = self._calculate_effect(ability)

        logger.info(
            f"{self.character.name} used {ability_name} "
            f"(cost: {ability.resource_cost} {ability.resource_type.value})"
        )

        return True, f"{ability_name} activated!", effect

    def _consume_resources(self, ability: Ability):
        """Consume resources for ability use."""
        if ability.resource_type == ResourceType.STAMINA:
            self.character.stamina -= ability.resource_cost
        elif ability.resource_type == ResourceType.MANA:
            self.character.mana -= ability.resource_cost
        elif ability.resource_type == ResourceType.HEALTH:
            self.character.health -= ability.resource_cost
        elif ability.resource_type == ResourceType.SOULS:
            self.character.souls -= ability.resource_cost

    def _calculate_effect(self, ability: Ability) -> AbilityEffect:
        """Calculate ability effects with stat scaling."""
        effect = ability.effects

        # Calculate stat scaling
        scaling_bonus = 0
        for stat_name in ability.scales_with:
            stat_value = getattr(self.character, stat_name, 10)
            stat_mod = (stat_value - 10) // 2
            scaling_bonus += stat_mod

        # Apply scaling to damage and healing
        scaled_damage = int(effect.damage * (1 + (scaling_bonus * ability.scaling_factor * 0.1)))
        scaled_healing = int(effect.healing * (1 + (scaling_bonus * ability.scaling_factor * 0.1)))

        return AbilityEffect(
            damage=scaled_damage,
            healing=scaled_healing,
            status_effect=effect.status_effect,
            status_duration=effect.status_duration,
            status_potency=effect.status_potency,
            stat_buff=effect.stat_buff,
            buff_duration=effect.buff_duration
        )

    def tick_cooldowns(self):
        """Reduce all ability cooldowns by 1."""
        for active_ability in self.abilities.values():
            active_ability.tick_cooldown()

    def reset_cooldowns(self):
        """Reset all ability cooldowns (for resting, etc.)."""
        for active_ability in self.abilities.values():
            active_ability.cooldown_remaining = 0

    def get_ability_info(self, ability_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific ability."""
        if ability_name not in self.abilities:
            return None

        active_ability = self.abilities[ability_name]
        ability = active_ability.ability

        return {
            "name": ability.name,
            "description": ability.description,
            "class": ability.class_type.value,
            "resource_type": ability.resource_type.value,
            "resource_cost": ability.resource_cost,
            "cooldown": ability.cooldown,
            "cooldown_remaining": active_ability.cooldown_remaining,
            "target_type": ability.target_type.value,
            "damage": ability.effects.damage,
            "healing": ability.effects.healing,
            "status_effect": ability.effects.status_effect.value if ability.effects.status_effect else None,
            "scales_with": ability.scales_with,
            "scaling_factor": ability.scaling_factor,
            "can_critical": ability.can_critical,
            "ignores_defense": ability.ignores_defense,
            "times_used": active_ability.times_used
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_abilities_for_class(class_type: ClassType) -> List[Ability]:
    """
    Get all abilities for a specific class.

    Args:
        class_type: Character class

    Returns:
        List of Ability objects
    """
    return CLASS_ABILITIES.get(class_type, [])


def get_ability_by_name(ability_name: str) -> Optional[Ability]:
    """
    Find an ability by name across all classes.

    Args:
        ability_name: Name of the ability

    Returns:
        Ability object or None if not found
    """
    for abilities in CLASS_ABILITIES.values():
        for ability in abilities:
            if ability.name == ability_name:
                return ability
    return None
