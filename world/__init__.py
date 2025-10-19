"""
World systems for Shards of Eternity.
Manages factions, crystal shards, and reality transformations.
"""

from .factions import (
    FactionManager,
    FactionType,
    Faction,
    FactionAbility,
    VictoryCondition,
    Relationship
)

from .shards import (
    ShardManager,
    CrystalShard,
    ShardElement,
    ShardStatus,
    GuardianBoss
)

from .reality import (
    RealityManager,
    RealityState,
    RealityTransformation,
    TransformationType,
    AetherfallEvent
)

__all__ = [
    # Faction system
    "FactionManager",
    "FactionType",
    "Faction",
    "FactionAbility",
    "VictoryCondition",
    "Relationship",

    # Shard system
    "ShardManager",
    "CrystalShard",
    "ShardElement",
    "ShardStatus",
    "GuardianBoss",

    # Reality system
    "RealityManager",
    "RealityState",
    "RealityTransformation",
    "TransformationType",
    "AetherfallEvent",
]
