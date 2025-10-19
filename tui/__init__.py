"""
TUI (Text-based User Interface) package for Shards of Eternity.
Built with the Textual framework for rich terminal interfaces.
"""

from .main_screen import MainGameScreen, PlayerStatsPanel, PartyPanel, ActionPanel, InventoryPanel, DialoguePanel
from .character_screen import CharacterCreationScreen, CharacterSheetScreen, CharacterCreationWizard, StatDisplay
from .combat_screen import CombatScreen, EnemyDisplay, PlayerCombatPanel, CombatActionMenu, CombatLogPanel
from .world_screen import WorldScreen, LocationCard, ShardInfoPanel, RealityStatePanel, NearbyPlayersPanel

__all__ = [
    # Main Screen
    "MainGameScreen",
    "PlayerStatsPanel",
    "PartyPanel",
    "ActionPanel",
    "InventoryPanel",
    "DialoguePanel",

    # Character Screen
    "CharacterCreationScreen",
    "CharacterSheetScreen",
    "CharacterCreationWizard",
    "StatDisplay",

    # Combat Screen
    "CombatScreen",
    "EnemyDisplay",
    "PlayerCombatPanel",
    "CombatActionMenu",
    "CombatLogPanel",

    # World Screen
    "WorldScreen",
    "LocationCard",
    "ShardInfoPanel",
    "RealityStatePanel",
    "NearbyPlayersPanel",
]
