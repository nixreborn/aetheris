"""
Shards of Eternity - Main Game Application
===========================================

Entry point for the game application. Provides:
- Database initialization and seeding
- Server/client/offline mode selection
- Character creation and selection
- TUI game loop with autosave
- Graceful shutdown handling
- System integration (combat, world, networking, LLM)

Usage:
    python main.py                     # Start in offline mode with TUI
    python main.py --server            # Run as master server
    python main.py --client            # Connect to master server
    python main.py --offline           # Explicit offline mode
    python main.py --create-character  # Character creation wizard
    python main.py --reset-db          # Reset and reseed database
"""

import argparse
import asyncio
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.binding import Binding

# Database imports
from database import init_database, reset_database, get_db_session
from database.models import (
    Character, CrystalShard, WorldState, Location, WorldEvent,
    RaceType, ClassType, FactionType, RealityType, InventoryItem
)

# System imports
from characters.character import CharacterCreator, CharacterManager
from world.shards import ShardManager
from combat.system import CombatSystem
from llm.generator import get_llm_generator
from network.master_server import MasterServer
from config.settings import get_settings

# TUI screens
from tui.main_screen import MainGameScreen
from tui.character_screen import CharacterCreationScreen, CharacterSheetScreen
from tui.world_screen import WorldScreen
from tui.combat_screen import CombatScreen

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/shards.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# INITIAL DATA SEEDING
# ============================================================================

def seed_crystal_shards(session) -> None:
    """Create the 12 Crystal Shards in the database."""
    logger.info("Seeding Crystal Shards...")

    # Check if shards already exist
    existing = session.query(CrystalShard).count()
    if existing > 0:
        logger.info(f"Crystal Shards already exist ({existing} shards). Skipping seed.")
        return

    shard_data = [
        {
            "shard_number": 1,
            "shard_name": "Phoenix Flame",
            "description": "A blazing crystal that burns with eternal fire",
            "reality_influence": "Fire and Rebirth",
            "guardian_boss_name": "Ignarok the Eternal",
            "power_level": 100
        },
        {
            "shard_number": 2,
            "shard_name": "Ocean's Tear",
            "description": "A sapphire crystal containing the primordial ocean",
            "reality_influence": "Water and Adaptation",
            "guardian_boss_name": "Thalassia the Depths",
            "power_level": 100
        },
        {
            "shard_number": 3,
            "shard_name": "Mountain's Core",
            "description": "Crystallized heart of the world's first mountain",
            "reality_influence": "Earth and Endurance",
            "guardian_boss_name": "Terrakor the Unmoved",
            "power_level": 100
        },
        {
            "shard_number": 4,
            "shard_name": "Tempest Crown",
            "description": "A crystal filled with eternal storms and lightning",
            "reality_influence": "Air and Freedom",
            "guardian_boss_name": "Zephyrath the Hurricane",
            "power_level": 100
        },
        {
            "shard_number": 5,
            "shard_name": "Dawn's Radiance",
            "description": "A brilliant crystal containing the first sunrise",
            "reality_influence": "Light and Truth",
            "guardian_boss_name": "Solarius the Radiant",
            "power_level": 100
        },
        {
            "shard_number": 6,
            "shard_name": "Void Heart",
            "description": "A black crystal that absorbs all light and hope",
            "reality_influence": "Darkness and Fear",
            "guardian_boss_name": "Nocturnyx the Void",
            "power_level": 100
        },
        {
            "shard_number": 7,
            "shard_name": "Null Sphere",
            "description": "A crystal that shouldn't exist, yet does",
            "reality_influence": "Void and Unmaking",
            "guardian_boss_name": "The Unmade",
            "power_level": 100
        },
        {
            "shard_number": 8,
            "shard_name": "Hourglass Eternal",
            "description": "A crystal containing all moments simultaneously",
            "reality_influence": "Time and Fate",
            "guardian_boss_name": "Chronovax the Timeless",
            "power_level": 100
        },
        {
            "shard_number": 9,
            "shard_name": "Infinity Prism",
            "description": "A crystal containing infinite space within finite form",
            "reality_influence": "Space and Distance",
            "guardian_boss_name": "Infinitus the Boundless",
            "power_level": 100
        },
        {
            "shard_number": 10,
            "shard_name": "Genesis Seed",
            "description": "The first spark of life crystallized",
            "reality_influence": "Life and Growth",
            "guardian_boss_name": "Vitaera the Ever-Growing",
            "power_level": 100
        },
        {
            "shard_number": 11,
            "shard_name": "Reaper's Eye",
            "description": "A crystal containing the final breath of all things",
            "reality_influence": "Death and Entropy",
            "guardian_boss_name": "Mortifax the Final",
            "power_level": 100
        },
        {
            "shard_number": 12,
            "shard_name": "Entropy Engine",
            "description": "Pure chaos crystallized into unstable form",
            "reality_influence": "Chaos and Randomness",
            "guardian_boss_name": "Chaoticus the Random",
            "power_level": 100
        }
    ]

    for shard_info in shard_data:
        shard = CrystalShard(**shard_info)
        session.add(shard)

    session.commit()
    logger.info(f"Successfully created {len(shard_data)} Crystal Shards")


def seed_locations(session) -> None:
    """Create initial game locations."""
    logger.info("Seeding locations...")

    # Check if locations already exist
    existing = session.query(Location).count()
    if existing > 0:
        logger.info(f"Locations already exist ({existing} locations). Skipping seed.")
        return

    locations_data = [
        {
            "name": "The Nexus",
            "description": "A neutral hub where all factions meet. The Crystal Shards pulse with energy here.",
            "zone_type": "town",
            "is_safe_zone": True,
            "danger_level": 0,
            "npc_list": '["Merchant", "Blacksmith", "Innkeeper", "Lorekeeper"]',
            "connected_locations": '[]'
        },
        {
            "name": "Ember Volcano",
            "description": "An active volcano shrouded in perpetual flame. Home to the Phoenix Flame shard.",
            "zone_type": "dungeon",
            "is_safe_zone": False,
            "danger_level": 8,
            "enemy_types": '["Fire Elemental", "Lava Beast", "Flame Wraith"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Abyssal Trench",
            "description": "The deepest point of the ocean, where pressure crushes all but the worthy.",
            "zone_type": "dungeon",
            "is_safe_zone": False,
            "danger_level": 8,
            "enemy_types": '["Sea Serpent", "Deep One", "Pressure Wraith"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Titan's Spine Mountains",
            "description": "Impossibly tall mountains that pierce the clouds. Stone golems guard ancient secrets.",
            "zone_type": "dungeon",
            "is_safe_zone": False,
            "danger_level": 9,
            "enemy_types": '["Stone Golem", "Mountain Troll", "Avalanche Spirit"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Crimson Cathedral",
            "description": "Headquarters of the Crimson Covenant. Blood magic permeates the air.",
            "zone_type": "faction_hq",
            "faction_controlled": FactionType.CRIMSON_COVENANT,
            "is_safe_zone": True,
            "danger_level": 0,
            "npc_list": '["Blood Mage", "Covenant Leader", "Ritual Master"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Aether Academy",
            "description": "The grand library and research center of the Aether Seekers.",
            "zone_type": "faction_hq",
            "faction_controlled": FactionType.AETHER_SEEKERS,
            "is_safe_zone": True,
            "danger_level": 0,
            "npc_list": '["Archmage", "Librarian", "Research Scholar"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Iron Foundry",
            "description": "The massive industrial complex of the Iron Brotherhood. Machines never sleep.",
            "zone_type": "faction_hq",
            "faction_controlled": FactionType.IRON_BROTHERHOOD,
            "is_safe_zone": True,
            "danger_level": 0,
            "npc_list": '["Engineer", "Forgemaster", "Automaton Technician"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Twilight Grove",
            "description": "An ethereal forest caught between day and night, home to the Moonlit Circle.",
            "zone_type": "faction_hq",
            "faction_controlled": FactionType.MOONLIT_CIRCLE,
            "is_safe_zone": True,
            "danger_level": 0,
            "npc_list": '["Druid Elder", "Moon Priestess", "Shapeshifter"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Shadow Sanctum",
            "description": "Hidden in darkness, the Shadowborn lurk in the spaces between reality.",
            "zone_type": "faction_hq",
            "faction_controlled": FactionType.SHADOWBORN,
            "is_safe_zone": True,
            "danger_level": 0,
            "npc_list": '["Shadow Master", "Assassin Trainer", "Void Walker"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Golden Citadel",
            "description": "A shining fortress of divine light, bastion of the Golden Order.",
            "zone_type": "faction_hq",
            "faction_controlled": FactionType.GOLDEN_ORDER,
            "is_safe_zone": True,
            "danger_level": 0,
            "npc_list": '["High Paladin", "Divine Oracle", "Holy Knight"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Wilderness Outpost",
            "description": "A small camp in the untamed wilds. Adventurers gather here.",
            "zone_type": "wilderness",
            "is_safe_zone": False,
            "danger_level": 3,
            "enemy_types": '["Wolf", "Bandit", "Wild Beast"]',
            "npc_list": '["Trader", "Scout"]',
            "connected_locations": '["The Nexus"]'
        },
        {
            "name": "Necropolis of Lost Souls",
            "description": "An ancient city of the dead. The Reaper's Eye shard lies at its heart.",
            "zone_type": "dungeon",
            "is_safe_zone": False,
            "danger_level": 9,
            "enemy_types": '["Undead Knight", "Lich", "Soul Harvester"]',
            "connected_locations": '["The Nexus"]'
        }
    ]

    for loc_data in locations_data:
        location = Location(**loc_data)
        session.add(location)

    session.commit()
    logger.info(f"Successfully created {len(locations_data)} locations")

    # Assign shards to locations
    logger.info("Assigning shards to locations...")
    shard_locations = {
        1: "Ember Volcano",
        2: "Abyssal Trench",
        3: "Titan's Spine Mountains",
        11: "Necropolis of Lost Souls"
    }

    for shard_num, loc_name in shard_locations.items():
        location = session.query(Location).filter_by(name=loc_name).first()
        shard = session.query(CrystalShard).filter_by(shard_number=shard_num).first()
        if location and shard:
            shard.location_id = location.id

    session.commit()
    logger.info("Shards assigned to locations")


def seed_world_state(session) -> None:
    """Initialize world state."""
    logger.info("Initializing world state...")

    # Check if world state exists
    world_state = session.query(WorldState).first()
    if world_state:
        logger.info("World state already exists. Skipping initialization.")
        return

    world_state = WorldState(
        current_reality=RealityType.NEUTRAL,
        reality_stability=100.0,
        aetherfall_count=0,
        total_aetherfalls=0,
        active_players=0,
        total_deaths=0,
        total_souls_in_economy=0,
        faction_shard_counts='{"Crimson Covenant": 0, "Aether Seekers": 0, "Iron Brotherhood": 0, "Moonlit Circle": 0, "Shadowborn": 0, "Golden Order": 0}'
    )
    session.add(world_state)
    session.commit()
    logger.info("World state initialized")


def seed_sample_npcs(session) -> None:
    """Create sample NPCs for the world."""
    logger.info("Creating sample NPCs...")

    # Check if NPCs already exist
    existing_npcs = session.query(Character).filter_by(is_player=False).count()
    if existing_npcs > 0:
        logger.info(f"NPCs already exist ({existing_npcs} NPCs). Skipping seed.")
        return

    # Get The Nexus location
    nexus = session.query(Location).filter_by(name="The Nexus").first()
    location_id = nexus.id if nexus else None

    npcs_data = [
        {
            "name": "Merchant Thane",
            "is_player": False,
            "race": RaceType.HUMAN,
            "character_class": ClassType.ROGUE,
            "faction": FactionType.GOLDEN_ORDER,
            "level": 5,
            "location_id": location_id,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 18
        },
        {
            "name": "Blacksmith Gorin",
            "is_player": False,
            "race": RaceType.DWARF,
            "character_class": ClassType.WARRIOR,
            "faction": FactionType.IRON_BROTHERHOOD,
            "level": 8,
            "location_id": location_id,
            "strength": 18,
            "dexterity": 10,
            "constitution": 16,
            "intelligence": 12,
            "wisdom": 14,
            "charisma": 10
        },
        {
            "name": "Lorekeeper Myra",
            "is_player": False,
            "race": RaceType.ELF,
            "character_class": ClassType.SORCERER,
            "faction": FactionType.AETHER_SEEKERS,
            "level": 10,
            "location_id": location_id,
            "strength": 8,
            "dexterity": 12,
            "constitution": 10,
            "intelligence": 18,
            "wisdom": 16,
            "charisma": 14
        },
        {
            "name": "Shadow Whisper",
            "is_player": False,
            "race": RaceType.TIEFLING,
            "character_class": ClassType.ROGUE,
            "faction": FactionType.SHADOWBORN,
            "level": 12,
            "location_id": location_id,
            "strength": 12,
            "dexterity": 18,
            "constitution": 14,
            "intelligence": 14,
            "wisdom": 10,
            "charisma": 16
        }
    ]

    for npc_data in npcs_data:
        npc = Character(**npc_data)
        session.add(npc)

    session.commit()
    logger.info(f"Successfully created {len(npcs_data)} NPCs")


def initialize_game_data(reset: bool = False) -> None:
    """
    Initialize or reset all game data.

    Args:
        reset: If True, drop all tables and recreate them
    """
    logger.info("Initializing game data...")

    if reset:
        logger.warning("Resetting database - all data will be lost!")
        reset_database()
    else:
        init_database()

    # Seed all initial data
    with get_db_session() as session:
        seed_crystal_shards(session)
        seed_locations(session)
        seed_world_state(session)
        seed_sample_npcs(session)

    logger.info("Game data initialization complete!")


# ============================================================================
# CHARACTER SELECTION SCREEN
# ============================================================================

class CharacterSelectionScreen(Screen):
    """Screen for selecting or creating a character."""

    BINDINGS = [
        Binding("escape", "quit", "Quit"),
        Binding("n", "new_character", "New Character"),
    ]

    DEFAULT_CSS = """
    CharacterSelectionScreen {
        layout: vertical;
        align: center middle;
    }

    #selection-container {
        width: 80;
        height: 30;
        border: solid $primary;
        padding: 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 2;
    }

    #character-list {
        height: 1fr;
        margin-bottom: 2;
    }

    #button-container {
        height: 5;
        align: center middle;
    }

    .char-button {
        margin: 0 1;
        min-width: 20;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.characters = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="selection-container"):
            yield Static("SHARDS OF ETERNITY", id="title")
            yield Static("Select a character or create a new one:", id="subtitle")

            with ScrollableContainer(id="character-list"):
                yield ListView(id="char-list")

            with Horizontal(id="button-container"):
                yield Button("New Character", id="btn-new", variant="primary", classes="char-button")
                yield Button("Delete", id="btn-delete", variant="error", classes="char-button")
                yield Button("Quit", id="btn-quit", classes="char-button")

        yield Footer()

    def on_mount(self) -> None:
        """Load characters when screen mounts."""
        self.load_characters()

    def load_characters(self) -> None:
        """Load all player characters from database."""
        try:
            with get_db_session() as session:
                self.characters = session.query(Character).filter_by(is_player=True).all()

                char_list = self.query_one("#char-list", ListView)
                char_list.clear()

                if self.characters:
                    for char in self.characters:
                        char_text = (
                            f"[bold cyan]{char.name}[/] - "
                            f"Lvl {char.level} {char.race.value} {char.character_class.value} | "
                            f"[yellow]{char.faction.value}[/]"
                        )
                        char_list.append(ListItem(Static(char_text), name=str(char.id)))
                else:
                    char_list.append(ListItem(Static("[dim]No characters found. Create your first character![/]")))

        except Exception as e:
            logger.error(f"Error loading characters: {e}")
            self.app.notify(f"Error loading characters: {e}", severity="error")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle character selection."""
        if event.item.name and event.item.name.isdigit():
            character_id = int(event.item.name)
            try:
                with get_db_session() as session:
                    character = session.query(Character).filter_by(id=character_id).first()
                    if character:
                        char_data = character.to_dict()
                        self.app.selected_character = char_data
                        self.app.push_screen(MainGameScreen(char_data))
            except Exception as e:
                logger.error(f"Error selecting character: {e}")
                self.app.notify(f"Error selecting character: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-new":
            self.action_new_character()
        elif event.button.id == "btn-delete":
            self.delete_selected_character()
        elif event.button.id == "btn-quit":
            self.app.exit()

    def action_new_character(self) -> None:
        """Open character creation screen."""
        def on_character_created(char_data):
            # Create character in database
            try:
                creator = CharacterCreator()
                # Create base stats
                base_stats = {
                    "strength": char_data["stats"]["strength"],
                    "dexterity": char_data["stats"]["dexterity"],
                    "constitution": char_data["stats"]["constitution"],
                    "intelligence": char_data["stats"]["intelligence"],
                    "wisdom": char_data["stats"]["wisdom"],
                    "charisma": char_data["stats"]["charisma"]
                }

                character = creator.create_character(
                    name=char_data["name"],
                    race=RaceType[char_data["race"].upper()],
                    character_class=ClassType[char_data["class"].upper()],
                    faction=FactionType[char_data["faction"].upper().replace(" ", "_")],
                    stats=base_stats,
                    description=char_data.get("description", "")
                )

                self.app.notify(f"Character '{character.name}' created successfully!", severity="success")
                self.load_characters()
            except Exception as e:
                logger.error(f"Error creating character: {e}")
                self.app.notify(f"Error creating character: {e}", severity="error")

        self.app.push_screen(CharacterCreationScreen(on_complete=on_character_created))

    def delete_selected_character(self) -> None:
        """Delete the selected character."""
        char_list = self.query_one("#char-list", ListView)
        if char_list.index is not None and char_list.index >= 0:
            selected_item = char_list.children[char_list.index]
            if hasattr(selected_item, 'name') and selected_item.name and selected_item.name.isdigit():
                character_id = int(selected_item.name)
                try:
                    with get_db_session() as session:
                        character = session.query(Character).filter_by(id=character_id).first()
                        if character:
                            char_name = character.name
                            session.delete(character)
                            session.commit()
                            self.app.notify(f"Character '{char_name}' deleted", severity="warning")
                            self.load_characters()
                except Exception as e:
                    logger.error(f"Error deleting character: {e}")
                    self.app.notify(f"Error deleting character: {e}", severity="error")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class ShardsOfEternityApp(App):
    """Main game application."""

    TITLE = "Shards of Eternity"
    CSS_PATH = None

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit Game"),
        Binding("ctrl+s", "save", "Save Game"),
    ]

    def __init__(self, mode: str = "offline", **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
        self.selected_character: Optional[Dict[str, Any]] = None
        self.autosave_interval = get_settings().autosave_interval
        self.last_save_time = time.time()
        self.master_server: Optional[MasterServer] = None
        self.shutdown_event = asyncio.Event()

    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        logger.info(f"Starting Shards of Eternity in {self.mode} mode")

        # Start with character selection
        self.push_screen(CharacterSelectionScreen())

        # Setup autosave
        if self.mode == "offline":
            self.set_interval(self.autosave_interval, self.autosave)

    def action_save(self) -> None:
        """Manual save action."""
        self.save_game()
        self.notify("Game saved!", severity="information")

    def autosave(self) -> None:
        """Automatic save handler."""
        current_time = time.time()
        if current_time - self.last_save_time >= self.autosave_interval:
            self.save_game()
            self.last_save_time = current_time
            logger.info("Autosave completed")

    def save_game(self) -> None:
        """Save current game state."""
        if not self.selected_character:
            return

        try:
            with get_db_session() as session:
                char_id = self.selected_character.get('id')
                if char_id:
                    character = session.query(Character).filter_by(id=char_id).first()
                    if character:
                        # Update character data
                        # Note: This would be expanded to save current state
                        character.updated_at = datetime.utcnow()
                        session.commit()
                        logger.debug(f"Saved character: {character.name}")
        except Exception as e:
            logger.error(f"Error saving game: {e}")

    def action_quit(self) -> None:
        """Handle graceful shutdown."""
        logger.info("Initiating graceful shutdown...")

        # Save game before quitting
        if self.selected_character:
            self.save_game()
            logger.info("Final save completed")

        # Cleanup and exit
        self.exit()


# ============================================================================
# SERVER MODE
# ============================================================================

async def run_server_mode():
    """Run as master server."""
    logger.info("Starting Shards of Eternity Master Server...")

    # Initialize database
    init_database()

    # Create and start master server
    server = MasterServer()

    def shutdown_handler(signum, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(server.stop())

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        await server.start()
        logger.info("Master server is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        await server.stop()
        logger.info("Master server shutdown complete")


# ============================================================================
# CLIENT MODE
# ============================================================================

def run_client_mode():
    """Run as client connected to master server."""
    logger.info("Starting Shards of Eternity Client...")

    # Initialize local database for caching
    init_database()

    # Start TUI in client mode
    app = ShardsOfEternityApp(mode="client")
    app.run()


# ============================================================================
# OFFLINE MODE
# ============================================================================

def run_offline_mode():
    """Run in single-player offline mode."""
    logger.info("Starting Shards of Eternity (Offline Mode)...")

    # Initialize database
    init_database()

    # Seed initial data if needed
    with get_db_session() as session:
        if session.query(CrystalShard).count() == 0:
            logger.info("No game data found. Seeding initial data...")
            initialize_game_data(reset=False)

    # Start TUI
    app = ShardsOfEternityApp(mode="offline")
    app.run()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Shards of Eternity - A multiplayer souls-like text adventure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Start in offline mode
  python main.py --server            # Run as master server
  python main.py --client            # Connect as client
  python main.py --reset-db          # Reset database and reseed
  python main.py --create-character  # Character creation only
        """
    )

    parser.add_argument(
        '--server',
        action='store_true',
        help='Run as master server'
    )

    parser.add_argument(
        '--client',
        action='store_true',
        help='Run as client (connect to master server)'
    )

    parser.add_argument(
        '--offline',
        action='store_true',
        help='Run in offline/single-player mode (default)'
    )

    parser.add_argument(
        '--create-character',
        action='store_true',
        help='Open character creation wizard'
    )

    parser.add_argument(
        '--reset-db',
        action='store_true',
        help='Reset database and reseed initial data (WARNING: destroys all data)'
    )

    args = parser.parse_args()

    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    # Handle reset database
    if args.reset_db:
        confirm = input("This will DELETE ALL DATA. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            logger.warning("Resetting database...")
            initialize_game_data(reset=True)
            logger.info("Database reset complete!")
        else:
            logger.info("Database reset cancelled")
        return

    # Handle character creation mode
    if args.create_character:
        logger.info("Starting character creation wizard...")
        init_database()

        class CharCreatorApp(App):
            def on_mount(self):
                def on_complete(char_data):
                    logger.info(f"Character created: {char_data}")
                    self.exit()
                self.push_screen(CharacterCreationScreen(on_complete=on_complete))

        app = CharCreatorApp()
        app.run()
        return

    # Determine mode
    if args.server:
        asyncio.run(run_server_mode())
    elif args.client:
        run_client_mode()
    else:
        # Default to offline mode
        run_offline_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
