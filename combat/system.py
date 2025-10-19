"""
Souls-like Combat System for Shards of Eternity.

Implements a comprehensive turn-based combat system with:
- Stamina-based attacks and dodges
- Multiple attack types (light, heavy, block, parry)
- Hit/miss/critical/dodge/parry mechanics
- Damage calculation with armor mitigation
- Status effects (bleed, poison, burn, frost, etc.)
- Combat logging and LLM-generated descriptions
"""
import random
import logging
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from database.models import Character, ClassType
from database import get_db_session
from characters.character import CharacterManager
from llm.generator import get_llm_generator

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class AttackType(Enum):
    """Types of attacks available in combat."""
    LIGHT_ATTACK = "light_attack"
    HEAVY_ATTACK = "heavy_attack"
    DODGE = "dodge"
    BLOCK = "block"
    PARRY = "parry"
    ABILITY = "ability"
    ITEM = "item"


class AttackResult(Enum):
    """Possible results of an attack."""
    HIT = "hit"
    MISS = "miss"
    CRITICAL = "critical"
    DODGED = "dodged"
    BLOCKED = "blocked"
    PARRIED = "parried"


class StatusEffect(Enum):
    """Status effects that can be applied in combat."""
    BLEED = "bleed"
    POISON = "poison"
    BURN = "burn"
    FROST = "frost"
    STUN = "stun"
    WEAKNESS = "weakness"
    STRENGTH_BUFF = "strength_buff"
    DEFENSE_BUFF = "defense_buff"
    REGENERATION = "regeneration"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AttackConfig:
    """Configuration for different attack types."""
    stamina_cost: int
    accuracy_modifier: float
    damage_multiplier: float
    critical_chance: float
    speed_modifier: float  # For turn order
    can_be_parried: bool = True


@dataclass
class StatusEffectInstance:
    """Instance of a status effect on a combatant."""
    effect_type: StatusEffect
    duration: int  # Rounds remaining
    potency: int  # Damage per turn or stat modifier
    applied_by: str  # Name of who applied it

    def tick(self) -> Tuple[int, bool]:
        """
        Process the effect for one round.

        Returns:
            Tuple of (damage_or_healing, is_expired)
        """
        self.duration -= 1
        damage = 0

        if self.effect_type in [StatusEffect.BLEED, StatusEffect.POISON, StatusEffect.BURN]:
            damage = self.potency
        elif self.effect_type == StatusEffect.REGENERATION:
            damage = -self.potency  # Negative damage = healing

        return damage, self.duration <= 0


@dataclass
class CombatAction:
    """Represents a single combat action."""
    actor: str
    target: str
    action_type: AttackType
    result: AttackResult
    damage: int = 0
    stamina_cost: int = 0
    status_applied: Optional[StatusEffect] = None
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CombatStats:
    """Derived combat statistics for a combatant."""
    attack_power: int
    defense: int
    accuracy: int
    evasion: int
    critical_chance: float
    critical_damage: float
    initiative: int
    poise: int  # Resistance to stagger/interruption


# ============================================================================
# ATTACK CONFIGURATIONS
# ============================================================================

ATTACK_CONFIGS = {
    AttackType.LIGHT_ATTACK: AttackConfig(
        stamina_cost=15,
        accuracy_modifier=1.1,
        damage_multiplier=1.0,
        critical_chance=0.05,
        speed_modifier=1.2,
        can_be_parried=True
    ),
    AttackType.HEAVY_ATTACK: AttackConfig(
        stamina_cost=35,
        accuracy_modifier=0.8,
        damage_multiplier=2.2,
        critical_chance=0.15,
        speed_modifier=0.7,
        can_be_parried=True
    ),
    AttackType.DODGE: AttackConfig(
        stamina_cost=20,
        accuracy_modifier=0.0,
        damage_multiplier=0.0,
        critical_chance=0.0,
        speed_modifier=1.5,
        can_be_parried=False
    ),
    AttackType.BLOCK: AttackConfig(
        stamina_cost=10,
        accuracy_modifier=0.0,
        damage_multiplier=0.0,
        critical_chance=0.0,
        speed_modifier=1.3,
        can_be_parried=False
    ),
    AttackType.PARRY: AttackConfig(
        stamina_cost=25,
        accuracy_modifier=0.0,
        damage_multiplier=0.0,
        critical_chance=0.0,
        speed_modifier=1.4,
        can_be_parried=False
    ),
}


# ============================================================================
# COMBATANT CLASS
# ============================================================================

class Combatant:
    """
    Represents a participant in combat (player or enemy).
    Tracks current state, status effects, and defensive stance.
    """

    def __init__(
        self,
        character: Character,
        is_enemy: bool = False,
        enemy_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a combatant.

        Args:
            character: Character database model
            is_enemy: Whether this is an enemy
            enemy_data: Optional enemy-specific data (overrides, etc.)
        """
        self.character = character
        self.is_enemy = is_enemy
        self.enemy_data = enemy_data or {}

        # Current state
        self.current_health = character.health
        self.current_stamina = character.stamina
        self.current_mana = character.mana

        # Status effects
        self.status_effects: List[StatusEffectInstance] = []

        # Defensive stance
        self.is_blocking = False
        self.is_dodging = False
        self.is_parrying = False

        # Combat stats
        self.combat_stats = self._calculate_combat_stats()

    def _calculate_combat_stats(self) -> CombatStats:
        """Calculate derived combat statistics."""
        char = self.character

        # Get stat modifiers
        def stat_mod(stat: int) -> int:
            return (stat - 10) // 2

        str_mod = stat_mod(char.strength)
        dex_mod = stat_mod(char.dexterity)
        con_mod = stat_mod(char.constitution)

        # Get equipment bonuses
        equipped_items = [item for item in char.inventory if item.is_equipped]
        total_attack_bonus = sum(item.attack_bonus for item in equipped_items)
        total_defense_bonus = sum(item.defense_bonus for item in equipped_items)

        # Calculate stats
        attack_power = 10 + str_mod + total_attack_bonus
        defense = 10 + dex_mod + total_defense_bonus
        accuracy = 60 + (dex_mod * 3) + (str_mod * 2)
        evasion = 10 + (dex_mod * 4)
        critical_chance = 0.05 + (dex_mod * 0.01)
        critical_damage = 1.5 + (str_mod * 0.1)
        initiative = 10 + dex_mod
        poise = 10 + con_mod

        return CombatStats(
            attack_power=max(1, attack_power),
            defense=max(0, defense),
            accuracy=max(10, accuracy),
            evasion=max(0, evasion),
            critical_chance=max(0.01, min(0.5, critical_chance)),
            critical_damage=max(1.0, critical_damage),
            initiative=max(1, initiative),
            poise=max(1, poise)
        )

    def take_damage(self, damage: int, is_true_damage: bool = False) -> int:
        """
        Apply damage to combatant.

        Args:
            damage: Raw damage amount
            is_true_damage: If True, bypass defense

        Returns:
            Actual damage taken
        """
        if is_true_damage:
            actual_damage = damage
        else:
            # Apply defense mitigation
            defense_reduction = self.combat_stats.defense * 0.5
            actual_damage = max(1, damage - defense_reduction)

            # Blocking reduces damage by 60%
            if self.is_blocking:
                actual_damage = int(actual_damage * 0.4)

        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage

    def consume_stamina(self, amount: int) -> bool:
        """
        Consume stamina. Returns False if not enough stamina.

        Args:
            amount: Stamina to consume

        Returns:
            True if successful, False if insufficient stamina
        """
        if self.current_stamina < amount:
            return False
        self.current_stamina = max(0, self.current_stamina - amount)
        return True

    def restore_stamina(self, amount: int):
        """Restore stamina (capped at max)."""
        self.current_stamina = min(
            self.character.max_stamina,
            self.current_stamina + amount
        )

    def add_status_effect(self, effect: StatusEffectInstance):
        """Add a status effect."""
        # Check if effect already exists - refresh duration if so
        for existing in self.status_effects:
            if existing.effect_type == effect.effect_type:
                existing.duration = max(existing.duration, effect.duration)
                existing.potency = max(existing.potency, effect.potency)
                return

        self.status_effects.append(effect)
        logger.debug(f"{self.character.name} afflicted with {effect.effect_type.value}")

    def process_status_effects(self) -> List[Tuple[StatusEffect, int]]:
        """
        Process all status effects for this round.

        Returns:
            List of (effect_type, damage) tuples
        """
        effects_damage = []
        expired_effects = []

        for effect in self.status_effects:
            damage, expired = effect.tick()

            if damage != 0:
                actual_damage = self.take_damage(abs(damage), is_true_damage=True)
                if damage > 0:
                    effects_damage.append((effect.effect_type, actual_damage))
                else:
                    effects_damage.append((effect.effect_type, -actual_damage))

            if expired:
                expired_effects.append(effect)

        # Remove expired effects
        for effect in expired_effects:
            self.status_effects.remove(effect)
            logger.debug(f"{effect.effect_type.value} expired on {self.character.name}")

        return effects_damage

    def get_status_modifier(self, stat_type: str) -> float:
        """Get total modifier from status effects for a stat."""
        modifier = 1.0

        for effect in self.status_effects:
            if effect.effect_type == StatusEffect.WEAKNESS and stat_type == "attack":
                modifier *= 0.75
            elif effect.effect_type == StatusEffect.STRENGTH_BUFF and stat_type == "attack":
                modifier *= 1.25
            elif effect.effect_type == StatusEffect.DEFENSE_BUFF and stat_type == "defense":
                modifier *= 1.25

        return modifier

    def reset_defensive_stance(self):
        """Reset all defensive stances."""
        self.is_blocking = False
        self.is_dodging = False
        self.is_parrying = False

    def is_alive(self) -> bool:
        """Check if combatant is still alive."""
        return self.current_health > 0

    def get_status_summary(self) -> str:
        """Get a summary of current status."""
        effects = ", ".join([e.effect_type.value for e in self.status_effects]) or "None"
        return (
            f"{self.character.name} | "
            f"HP: {self.current_health}/{self.character.max_health} | "
            f"Stamina: {self.current_stamina}/{self.character.max_stamina} | "
            f"Effects: {effects}"
        )


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class CombatSystem:
    """
    Main combat system orchestrating turn-based Souls-like combat.
    """

    def __init__(
        self,
        player: Character,
        enemy: Character,
        session: Optional[Session] = None,
        use_llm: bool = True
    ):
        """
        Initialize a combat encounter.

        Args:
            player: Player character
            enemy: Enemy character
            session: Database session
            use_llm: Whether to generate LLM descriptions
        """
        self.session = session
        self.use_llm = use_llm
        self.llm = get_llm_generator() if use_llm else None

        # Create combatants
        self.player = Combatant(player, is_enemy=False)
        self.enemy = Combatant(enemy, is_enemy=True)

        # Combat state
        self.round_number = 0
        self.combat_log: List[CombatAction] = []
        self.is_active = True

        # Turn order (based on initiative)
        self._determine_first_attacker()

        logger.info(f"Combat started: {player.name} vs {enemy.name}")

    def _determine_first_attacker(self):
        """Determine who attacks first based on initiative."""
        player_init = self.player.combat_stats.initiative + random.randint(1, 20)
        enemy_init = self.enemy.combat_stats.initiative + random.randint(1, 20)

        self.player_first = player_init >= enemy_init

        logger.debug(
            f"Initiative: Player {player_init} vs Enemy {enemy_init} - "
            f"{'Player' if self.player_first else 'Enemy'} goes first"
        )

    def execute_round(
        self,
        player_action: AttackType,
        player_target_ability: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute one round of combat.

        Args:
            player_action: The action the player wants to take
            player_target_ability: If using ability, which ability

        Returns:
            Dictionary with round results
        """
        self.round_number += 1
        round_log = []

        logger.info(f"\n=== Round {self.round_number} ===")

        # Process status effects at start of round
        player_effects = self.player.process_status_effects()
        enemy_effects = self.enemy.process_status_effects()

        if player_effects:
            for effect, damage in player_effects:
                round_log.append(f"Player takes {damage} from {effect.value}")

        if enemy_effects:
            for effect, damage in enemy_effects:
                round_log.append(f"Enemy takes {damage} from {effect.value}")

        # Check if combat ended from status effects
        if not self.player.is_alive() or not self.enemy.is_alive():
            return self._end_combat()

        # Determine turn order
        if self.player_first:
            actions = [
                (self.player, self.enemy, player_action),
                (self.enemy, self.player, self._get_enemy_action())
            ]
        else:
            actions = [
                (self.enemy, self.player, self._get_enemy_action()),
                (self.player, self.enemy, player_action)
            ]

        # Execute actions
        for attacker, defender, action in actions:
            if not attacker.is_alive() or not defender.is_alive():
                break

            result = self._execute_action(attacker, defender, action)
            self.combat_log.append(result)
            round_log.append(result.description)

        # Restore some stamina at end of round
        self.player.restore_stamina(10)
        self.enemy.restore_stamina(10)

        # Reset defensive stances
        self.player.reset_defensive_stance()
        self.enemy.reset_defensive_stance()

        # Check for combat end
        if not self.player.is_alive() or not self.enemy.is_alive():
            return self._end_combat()

        return {
            "round": self.round_number,
            "actions": round_log,
            "player_status": self.player.get_status_summary(),
            "enemy_status": self.enemy.get_status_summary(),
            "combat_ended": False
        }

    def _get_enemy_action(self) -> AttackType:
        """Simple AI to choose enemy action."""
        # Check stamina
        if self.enemy.current_stamina < 15:
            # Not enough for any attack, just recover
            return AttackType.BLOCK

        # Random behavior with some logic
        rand = random.random()

        # 40% light attack
        if rand < 0.4 and self.enemy.current_stamina >= 15:
            return AttackType.LIGHT_ATTACK

        # 25% heavy attack if enough stamina
        elif rand < 0.65 and self.enemy.current_stamina >= 35:
            return AttackType.HEAVY_ATTACK

        # 15% dodge
        elif rand < 0.8 and self.enemy.current_stamina >= 20:
            return AttackType.DODGE

        # 10% parry
        elif rand < 0.9 and self.enemy.current_stamina >= 25:
            return AttackType.PARRY

        # 10% block or default
        else:
            return AttackType.BLOCK

    def _execute_action(
        self,
        attacker: Combatant,
        defender: Combatant,
        action_type: AttackType
    ) -> CombatAction:
        """Execute a single combat action."""
        config = ATTACK_CONFIGS.get(action_type)

        # Check stamina
        if not attacker.consume_stamina(config.stamina_cost):
            # Not enough stamina - action fails
            return CombatAction(
                actor=attacker.character.name,
                target=defender.character.name,
                action_type=action_type,
                result=AttackResult.MISS,
                stamina_cost=0,
                description=f"{attacker.character.name} is too exhausted to act!"
            )

        # Handle defensive actions
        if action_type == AttackType.BLOCK:
            attacker.is_blocking = True
            return CombatAction(
                actor=attacker.character.name,
                target=defender.character.name,
                action_type=action_type,
                result=AttackResult.HIT,
                stamina_cost=config.stamina_cost,
                description=f"{attacker.character.name} raises their guard defensively."
            )

        elif action_type == AttackType.DODGE:
            attacker.is_dodging = True
            return CombatAction(
                actor=attacker.character.name,
                target=defender.character.name,
                action_type=action_type,
                result=AttackResult.HIT,
                stamina_cost=config.stamina_cost,
                description=f"{attacker.character.name} prepares to dodge."
            )

        elif action_type == AttackType.PARRY:
            attacker.is_parrying = True
            return CombatAction(
                actor=attacker.character.name,
                target=defender.character.name,
                action_type=action_type,
                result=AttackResult.HIT,
                stamina_cost=config.stamina_cost,
                description=f"{attacker.character.name} readies a parry."
            )

        # Handle attacks
        elif action_type in [AttackType.LIGHT_ATTACK, AttackType.HEAVY_ATTACK]:
            return self._execute_attack(attacker, defender, action_type, config)

        return CombatAction(
            actor=attacker.character.name,
            target=defender.character.name,
            action_type=action_type,
            result=AttackResult.MISS,
            description=f"{attacker.character.name} hesitates."
        )

    def _execute_attack(
        self,
        attacker: Combatant,
        defender: Combatant,
        action_type: AttackType,
        config: AttackConfig
    ) -> CombatAction:
        """Execute an attack action."""
        # Check if defender is dodging
        if defender.is_dodging:
            dodge_chance = defender.combat_stats.evasion + 20
            if random.randint(1, 100) <= dodge_chance:
                return CombatAction(
                    actor=attacker.character.name,
                    target=defender.character.name,
                    action_type=action_type,
                    result=AttackResult.DODGED,
                    stamina_cost=config.stamina_cost,
                    description=f"{defender.character.name} nimbly dodges {attacker.character.name}'s attack!"
                )

        # Check if defender is parrying
        if defender.is_parrying and config.can_be_parried:
            parry_chance = 30 + (defender.combat_stats.initiative * 2)
            if random.randint(1, 100) <= parry_chance:
                # Successful parry - defender ripostes for half damage
                riposte_damage = attacker.combat_stats.attack_power // 2
                actual_damage = attacker.take_damage(riposte_damage)

                return CombatAction(
                    actor=attacker.character.name,
                    target=defender.character.name,
                    action_type=action_type,
                    result=AttackResult.PARRIED,
                    damage=actual_damage,
                    stamina_cost=config.stamina_cost,
                    description=f"{defender.character.name} parries and ripostes for {actual_damage} damage!"
                )

        # Calculate hit chance
        base_accuracy = attacker.combat_stats.accuracy
        modified_accuracy = base_accuracy * config.accuracy_modifier
        evasion = defender.combat_stats.evasion

        hit_chance = max(10, min(95, modified_accuracy - evasion))
        hit_roll = random.randint(1, 100)

        # Miss
        if hit_roll > hit_chance:
            return CombatAction(
                actor=attacker.character.name,
                target=defender.character.name,
                action_type=action_type,
                result=AttackResult.MISS,
                stamina_cost=config.stamina_cost,
                description=f"{attacker.character.name}'s attack misses {defender.character.name}!"
            )

        # Calculate damage
        base_damage = attacker.combat_stats.attack_power
        attack_modifier = attacker.get_status_modifier("attack")
        damage = int(base_damage * config.damage_multiplier * attack_modifier)

        # Check for critical
        crit_chance = attacker.combat_stats.critical_chance + config.critical_chance
        is_critical = random.random() < crit_chance

        result_type = AttackResult.CRITICAL if is_critical else AttackResult.HIT

        if is_critical:
            damage = int(damage * attacker.combat_stats.critical_damage)

        # Apply damage
        actual_damage = defender.take_damage(damage)

        # Check for status effect application (bleed on heavy attacks, etc.)
        status_applied = None
        if action_type == AttackType.HEAVY_ATTACK and random.random() < 0.3:
            bleed = StatusEffectInstance(
                effect_type=StatusEffect.BLEED,
                duration=3,
                potency=5,
                applied_by=attacker.character.name
            )
            defender.add_status_effect(bleed)
            status_applied = StatusEffect.BLEED

        # Generate description
        description = self._generate_attack_description(
            attacker.character.name,
            defender.character.name,
            action_type.value,
            result_type.value,
            actual_damage,
            status_applied.value if status_applied else None
        )

        return CombatAction(
            actor=attacker.character.name,
            target=defender.character.name,
            action_type=action_type,
            result=result_type,
            damage=actual_damage,
            stamina_cost=config.stamina_cost,
            status_applied=status_applied,
            description=description
        )

    def _generate_attack_description(
        self,
        attacker: str,
        defender: str,
        action: str,
        result: str,
        damage: int,
        status: Optional[str]
    ) -> str:
        """Generate a description for an attack."""
        if self.use_llm and self.llm:
            try:
                import asyncio
                description = asyncio.run(
                    self.llm.generate_combat_description(
                        attacker=attacker,
                        defender=defender,
                        action=action,
                        result=result,
                        damage=damage,
                        special_effects=status
                    )
                )
                return description
            except Exception as e:
                logger.warning(f"LLM description failed: {e}")

        # Fallback descriptions
        if result == "critical":
            base = f"{attacker}'s {action} CRITICALLY strikes {defender} for {damage} damage!"
        elif result == "hit":
            base = f"{attacker}'s {action} hits {defender} for {damage} damage."
        else:
            base = f"{attacker}'s attack {result}."

        if status:
            base += f" {defender} is now afflicted with {status}!"

        return base

    def _end_combat(self) -> Dict[str, Any]:
        """End combat and return results."""
        self.is_active = False

        player_won = self.player.is_alive()

        # Calculate rewards
        souls_gained = 0
        xp_gained = 0
        loot = []

        if player_won:
            # Calculate rewards based on enemy level
            souls_gained = random.randint(50, 150) * self.enemy.character.level
            xp_gained = 100 * self.enemy.character.level

            # Update player in database
            if self.session:
                char_manager = CharacterManager(self.session)
                char_manager.add_souls(self.player.character.id, souls_gained)
                char_manager.add_experience(self.player.character.id, xp_gained)
                char_manager.update_health(
                    self.player.character.id,
                    -(self.player.character.max_health - self.player.current_health)
                )

                # Add combat memory
                char_manager.add_memory(
                    self.player.character.id,
                    "combat",
                    f"Victory over {self.enemy.character.name}",
                    f"Defeated {self.enemy.character.name} in combat after {self.round_number} rounds",
                    souls_gained=souls_gained
                )

        logger.info(
            f"Combat ended: {'Player Victory' if player_won else 'Player Defeat'} "
            f"after {self.round_number} rounds"
        )

        return {
            "combat_ended": True,
            "player_won": player_won,
            "rounds": self.round_number,
            "player_health": self.player.current_health,
            "souls_gained": souls_gained,
            "xp_gained": xp_gained,
            "loot": loot,
            "combat_log": [
                {
                    "actor": action.actor,
                    "target": action.target,
                    "action": action.action_type.value,
                    "result": action.result.value,
                    "damage": action.damage,
                    "description": action.description
                }
                for action in self.combat_log
            ]
        }

    def get_available_actions(self, is_player: bool = True) -> List[Dict[str, Any]]:
        """
        Get list of available actions for a combatant.

        Args:
            is_player: Whether to get player actions (vs enemy)

        Returns:
            List of action dictionaries with cost and description
        """
        combatant = self.player if is_player else self.enemy

        actions = []
        for action_type, config in ATTACK_CONFIGS.items():
            can_afford = combatant.current_stamina >= config.stamina_cost

            actions.append({
                "action": action_type.value,
                "stamina_cost": config.stamina_cost,
                "can_use": can_afford,
                "description": self._get_action_description(action_type, config)
            })

        return actions

    def _get_action_description(self, action: AttackType, config: AttackConfig) -> str:
        """Get description for an action."""
        descriptions = {
            AttackType.LIGHT_ATTACK: f"Quick attack ({config.stamina_cost} stamina) - Fast, reliable damage",
            AttackType.HEAVY_ATTACK: f"Powerful attack ({config.stamina_cost} stamina) - High damage, may cause bleed",
            AttackType.DODGE: f"Dodge ({config.stamina_cost} stamina) - Evade next attack",
            AttackType.BLOCK: f"Block ({config.stamina_cost} stamina) - Reduce incoming damage by 60%",
            AttackType.PARRY: f"Parry ({config.stamina_cost} stamina) - Counter attack if successful",
        }
        return descriptions.get(action, "Unknown action")
