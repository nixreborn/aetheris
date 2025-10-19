"""
Example application demonstrating the Shards of Eternity TUI.
Run this file to see all the TUI screens in action.

Usage:
    python -m tui.example_app
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Button
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen

from tui.main_screen import MainGameScreen
from tui.character_screen import CharacterCreationScreen, CharacterSheetScreen
from tui.combat_screen import CombatScreen
from tui.world_screen import WorldScreen


class MenuScreen(Screen):
    """Main menu for selecting which screen to view."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    MenuScreen {
        align: center middle;
    }

    #menu-container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 2;
        background: $surface;
    }

    .menu-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        padding: 1;
        margin-bottom: 2;
    }

    .menu-button {
        width: 100%;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="menu-container"):
            yield Button(
                "SHARDS OF ETERNITY - TUI DEMO",
                id="title",
                classes="menu-title",
                disabled=True
            )
            yield Button("1. Main Game Screen", id="main", classes="menu-button", variant="primary")
            yield Button("2. Character Creation", id="create", classes="menu-button")
            yield Button("3. Character Sheet", id="sheet", classes="menu-button")
            yield Button("4. Combat Screen", id="combat", classes="menu-button", variant="error")
            yield Button("5. World & Travel", id="world", classes="menu-button", variant="success")
            yield Button("Quit", id="quit", classes="menu-button", variant="warning")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu button presses."""
        if event.button.id == "main":
            self.app.push_screen(self.create_main_screen())

        elif event.button.id == "create":
            self.app.push_screen(CharacterCreationScreen(on_complete=self.on_character_created))

        elif event.button.id == "sheet":
            self.app.push_screen(self.create_character_sheet())

        elif event.button.id == "combat":
            self.app.push_screen(self.create_combat_screen())

        elif event.button.id == "world":
            self.app.push_screen(self.create_world_screen())

        elif event.button.id == "quit":
            self.app.exit()

    def create_main_screen(self) -> MainGameScreen:
        """Create the main game screen with sample data."""
        character_data = {
            "name": "Eldrin Shadowbane",
            "level": 5,
            "race": "Elf",
            "class": "Ranger",
            "faction": "Moonlit Circle",
            "health": 85,
            "max_health": 110,
            "stamina": 95,
            "max_stamina": 120,
            "mana": 70,
            "max_mana": 90,
            "souls": 450
        }
        return MainGameScreen(character_data)

    def create_character_sheet(self) -> CharacterSheetScreen:
        """Create a character sheet with sample data."""
        character_data = {
            "name": "Eldrin Shadowbane",
            "level": 5,
            "race": "Elf",
            "class": "Ranger",
            "faction": "Moonlit Circle",
            "experience": 1200,
            "next_level_xp": 1500,
            "souls": 450,
            "stats": {
                "strength": 12,
                "dexterity": 18,
                "constitution": 14,
                "intelligence": 13,
                "wisdom": 16,
                "charisma": 11
            },
            "resources": {
                "health": "85/110",
                "stamina": "95/120",
                "mana": "70/90"
            },
            "equipped_items": [
                {
                    "name": "Hunting Bow",
                    "type": "weapon",
                    "attack_bonus": 12
                },
                {
                    "name": "Leather Armor",
                    "type": "armor",
                    "defense_bonus": 6
                }
            ],
            "inventory_items": [
                {"name": "Health Potion", "quantity": 3, "value": 20},
                {"name": "Arrows", "quantity": 50, "value": 1},
                {"name": "Lockpick Set", "quantity": 1, "value": 30}
            ],
            "derived_stats": {
                "armor_class": 16,
                "initiative": 4,
                "attack_power": 13,
                "magic_power": 8,
                "equipment_bonuses": {
                    "attack": 12,
                    "defense": 6,
                    "magic": 0
                }
            }
        }
        return CharacterSheetScreen(character_data)

    def create_combat_screen(self) -> CombatScreen:
        """Create a combat screen with sample data."""
        character_data = {
            "name": "Eldrin Shadowbane",
            "health": 85,
            "max_health": 110,
            "stamina": 95,
            "max_stamina": 120,
            "mana": 70,
            "max_mana": 90,
            "attack_power": 13,
            "armor_class": 16,
            "initiative": 4
        }

        enemies = [
            {
                "name": "Shadow Wolf",
                "level": 4,
                "type": "Beast",
                "health": 45,
                "max_health": 60,
                "status_effects": ["Enraged"]
            },
            {
                "name": "Dark Cultist",
                "level": 5,
                "type": "Humanoid",
                "health": 40,
                "max_health": 50,
                "status_effects": []
            }
        ]

        return CombatScreen(character_data, enemies, on_combat_end=self.on_combat_end)

    def create_world_screen(self) -> WorldScreen:
        """Create a world/travel screen."""
        return WorldScreen(
            current_location="Starting Town",
            on_travel=self.on_travel
        )

    def on_character_created(self, character_data: dict) -> None:
        """Callback when character is created."""
        self.app.notify(
            f"Character created: {character_data.get('name', 'Unknown')}",
            title="Success",
            severity="information"
        )

    def on_combat_end(self, result: dict) -> None:
        """Callback when combat ends."""
        if result.get("player_victory"):
            self.app.notify("Victory!", title="Combat Complete", severity="information")
        else:
            self.app.notify("Defeat...", title="Combat Complete", severity="warning")

    def on_travel(self, location_name: str) -> None:
        """Callback when traveling to a new location."""
        self.app.notify(
            f"Traveling to {location_name}...",
            title="Travel",
            severity="information"
        )

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class ShardsOfEternityTUI(App):
    """Main TUI application for Shards of Eternity."""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    TITLE = "Shards of Eternity - TUI Demo"
    SUB_TITLE = "Text-based Interface Demonstration"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    def on_mount(self) -> None:
        """Called when app starts."""
        self.push_screen(MenuScreen())


def main():
    """Run the TUI application."""
    app = ShardsOfEternityTUI()
    app.run()


if __name__ == "__main__":
    main()
