"""
Combat system for Shards of Eternity.

Provides comprehensive Souls-like combat mechanics including:
- Turn-based combat with stamina management
- Multiple attack types and defensive actions
- Status effects and damage calculations
- Enemy AI with different behavior patterns
- Class-specific abilities with cooldowns
- Boss mechanics and loot generation
"""

from combat.system import (
    CombatSystem,
    Combatant,
    AttackType,
    AttackResult,
    StatusEffect,
    StatusEffectInstance,
    CombatAction,
    CombatStats,
    ATTACK_CONFIGS
)

from combat.enemies import (
    EnemyFactory,
    EnemyTemplate,
    EnemyType,
    EnemyBehavior,
    DamageType,
    LootGenerator,
    EnemyAI,
    ENEMY_TEMPLATES
)

from combat.abilities import (
    AbilityManager,
    Ability,
    AbilityEffect,
    ActiveAbility,
    ResourceType,
    TargetType,
    get_abilities_for_class,
    get_ability_by_name,
    CLASS_ABILITIES
)

__all__ = [
    # Combat System
    "CombatSystem",
    "Combatant",
    "AttackType",
    "AttackResult",
    "StatusEffect",
    "StatusEffectInstance",
    "CombatAction",
    "CombatStats",
    "ATTACK_CONFIGS",

    # Enemy System
    "EnemyFactory",
    "EnemyTemplate",
    "EnemyType",
    "EnemyBehavior",
    "DamageType",
    "LootGenerator",
    "EnemyAI",
    "ENEMY_TEMPLATES",

    # Ability System
    "AbilityManager",
    "Ability",
    "AbilityEffect",
    "ActiveAbility",
    "ResourceType",
    "TargetType",
    "get_abilities_for_class",
    "get_ability_by_name",
    "CLASS_ABILITIES",
]
