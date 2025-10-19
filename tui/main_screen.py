"""
Main game screen TUI for Shards of Eternity.
Provides the primary interface for game interaction with panels for stats, party, actions, inventory, and dialogue.
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, Label, ProgressBar,
    ListView, ListItem, RichLog, Input
)
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class StatBar(Static):
    """A progress bar with label for stats like health, stamina, mana."""

    def __init__(self, label: str, current: int, maximum: int, color: str = "green", **kwargs):
        super().__init__(**kwargs)
        self.label_text = label
        self.current = current
        self.maximum = maximum
        self.color = color

    def compose(self) -> ComposeResult:
        yield Label(f"{self.label_text}: {self.current}/{self.maximum}")
        yield ProgressBar(total=self.maximum, show_eta=False)

    def on_mount(self) -> None:
        """Update progress bar on mount."""
        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(progress=self.current)

    def update_values(self, current: int, maximum: int) -> None:
        """Update the stat values and refresh display."""
        self.current = current
        self.maximum = maximum
        label = self.query_one(Label)
        label.update(f"{self.label_text}: {self.current}/{self.maximum}")
        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(total=maximum, progress=current)


class PlayerStatsPanel(Static):
    """Header panel showing player stats."""

    DEFAULT_CSS = """
    PlayerStatsPanel {
        height: 8;
        border: solid $primary;
        padding: 1;
    }

    #stats-container {
        height: 100%;
    }

    StatBar {
        height: 2;
        margin-bottom: 1;
    }
    """

    def __init__(self, character_data: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.character_data = character_data or self._get_default_character()

    def _get_default_character(self) -> Dict[str, Any]:
        """Return default character data for display."""
        return {
            "name": "Adventurer",
            "level": 1,
            "race": "Human",
            "class": "Warrior",
            "faction": "Crimson Covenant",
            "health": 100,
            "max_health": 100,
            "stamina": 100,
            "max_stamina": 100,
            "mana": 100,
            "max_mana": 100,
            "souls": 100
        }

    def compose(self) -> ComposeResult:
        char = self.character_data

        with Vertical(id="stats-container"):
            yield Static(
                f"[bold cyan]{char['name']}[/] - Lvl {char['level']} {char['race']} {char['class']} | "
                f"[yellow]{char['faction']}[/] | [gold1]Souls: {char['souls']}[/]"
            )
            yield StatBar("Health", char["health"], char["max_health"], "red")
            yield StatBar("Stamina", char["stamina"], char["max_stamina"], "yellow")
            yield StatBar("Mana", char["mana"], char["max_mana"], "blue")

    def update_character(self, character_data: Dict[str, Any]) -> None:
        """Update the displayed character data."""
        self.character_data = character_data
        self.refresh(layout=True)


class PartyPanel(Static):
    """Left panel showing party members."""

    DEFAULT_CSS = """
    PartyPanel {
        width: 25;
        border: solid $primary;
        padding: 1;
    }

    #party-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #party-list {
        height: 100%;
    }

    .party-member {
        margin: 1 0;
        padding: 1;
        border: solid $primary-lighten-1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("PARTY", id="party-title")
        with ScrollableContainer(id="party-list"):
            yield Static("[dim]No party members[/]", classes="party-member")

    def add_party_member(self, name: str, level: int, char_class: str, health: int, max_health: int) -> None:
        """Add a party member to the list."""
        container = self.query_one("#party-list")
        health_pct = int((health / max_health) * 100)

        color = "green" if health_pct > 60 else "yellow" if health_pct > 30 else "red"

        member_text = (
            f"[bold]{name}[/]\n"
            f"Lvl {level} {char_class}\n"
            f"[{color}]HP: {health}/{max_health}[/]"
        )

        container.mount(Static(member_text, classes="party-member"))


class ActionPanel(Static):
    """Center panel for main game actions, exploration, combat, dialogue."""

    DEFAULT_CSS = """
    ActionPanel {
        border: solid $primary;
        padding: 1;
    }

    #action-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #action-content {
        height: 100%;
        border: solid $primary-lighten-1;
        padding: 1;
    }

    #action-description {
        height: 60%;
        margin-bottom: 1;
    }

    #action-buttons {
        height: 40%;
        align: center middle;
    }

    .action-button {
        width: 20;
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("EXPLORATION", id="action-title")
        with Vertical(id="action-content"):
            with ScrollableContainer(id="action-description"):
                yield Static(
                    "[bold]Welcome to Shards of Eternity[/]\n\n"
                    "You stand at the threshold of adventure. The world awaits your choices, "
                    "and the Crystal Shards call out across the dimensions. "
                    "Six factions vie for control, and reality itself hangs in the balance.\n\n"
                    "[dim]What will you do?[/]"
                )
            with Horizontal(id="action-buttons"):
                yield Button("Explore", id="btn-explore", classes="action-button", variant="primary")
                yield Button("Rest", id="btn-rest", classes="action-button")
                yield Button("Talk", id="btn-talk", classes="action-button")
                yield Button("Search", id="btn-search", classes="action-button")

    def update_content(self, title: str, description: str, buttons: Optional[list] = None) -> None:
        """Update the action panel content."""
        title_widget = self.query_one("#action-title")
        title_widget.update(title)

        desc_widget = self.query_one("#action-description")
        desc_widget.remove_children()
        desc_widget.mount(Static(description))

        if buttons:
            button_container = self.query_one("#action-buttons")
            button_container.remove_children()
            for btn_label, btn_id in buttons:
                button_container.mount(Button(btn_label, id=btn_id, classes="action-button"))


class InventoryPanel(Static):
    """Right panel showing inventory and equipment."""

    DEFAULT_CSS = """
    InventoryPanel {
        width: 30;
        border: solid $primary;
        padding: 1;
    }

    #inventory-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #equipped-section {
        height: 40%;
        border: solid $primary-lighten-1;
        padding: 1;
        margin-bottom: 1;
    }

    #inventory-section {
        height: 60%;
        border: solid $primary-lighten-1;
        padding: 1;
    }

    .item {
        margin: 1 0;
    }

    .equipped {
        color: $success;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("INVENTORY & EQUIPMENT", id="inventory-title")

        with ScrollableContainer(id="equipped-section"):
            yield Static("[bold]Equipped:[/]", classes="item")
            yield Static("[equipped]Iron Longsword[/] [dim](+10 ATK)[/]", classes="item equipped")
            yield Static("[equipped]Leather Armor[/] [dim](+5 DEF)[/]", classes="item equipped")

        with ScrollableContainer(id="inventory-section"):
            yield Static("[bold]Inventory:[/]", classes="item")
            yield Static("Health Potion x3", classes="item")
            yield Static("[dim]Empty slot[/]", classes="item")

    def update_inventory(self, equipped_items: list, inventory_items: list) -> None:
        """Update the inventory display."""
        equipped_container = self.query_one("#equipped-section")
        equipped_container.remove_children()
        equipped_container.mount(Static("[bold]Equipped:[/]", classes="item"))

        for item in equipped_items:
            bonus_text = ""
            if item.get("attack_bonus"):
                bonus_text = f" [dim](+{item['attack_bonus']} ATK)[/]"
            elif item.get("defense_bonus"):
                bonus_text = f" [dim](+{item['defense_bonus']} DEF)[/]"

            equipped_container.mount(
                Static(f"[equipped]{item['name']}[/]{bonus_text}", classes="item equipped")
            )

        inventory_container = self.query_one("#inventory-section")
        inventory_container.remove_children()
        inventory_container.mount(Static("[bold]Inventory:[/]", classes="item"))

        for item in inventory_items:
            qty = f" x{item['quantity']}" if item.get('quantity', 1) > 1 else ""
            inventory_container.mount(Static(f"{item['name']}{qty}", classes="item"))


class DialoguePanel(Static):
    """Bottom panel for dialogue log and input."""

    DEFAULT_CSS = """
    DialoguePanel {
        height: 12;
        border: solid $primary;
        padding: 1;
    }

    #dialogue-log {
        height: 8;
        border: solid $primary-lighten-1;
        margin-bottom: 1;
    }

    #dialogue-input-container {
        height: 3;
    }
    """

    def compose(self) -> ComposeResult:
        yield RichLog(id="dialogue-log", highlight=True, markup=True)
        with Horizontal(id="dialogue-input-container"):
            yield Input(placeholder="Enter command or speak...", id="dialogue-input")

    def add_message(self, message: str, message_type: str = "info") -> None:
        """Add a message to the dialogue log."""
        log = self.query_one(RichLog)

        color_map = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "combat": "orange1",
            "dialogue": "magenta"
        }

        color = color_map.get(message_type, "white")
        log.write(f"[{color}]{message}[/]")

    def clear_log(self) -> None:
        """Clear the dialogue log."""
        log = self.query_one(RichLog)
        log.clear()


class MainGameScreen(Screen):
    """Main game screen with all panels."""

    BINDINGS = [
        Binding("t", "travel", "Travel"),
        Binding("i", "inventory", "Inventory"),
        Binding("c", "character", "Character"),
        Binding("p", "party", "Party"),
        Binding("s", "settings", "Settings"),
        Binding("q", "quit_game", "Quit"),
    ]

    DEFAULT_CSS = """
    MainGameScreen {
        layout: vertical;
    }

    #main-container {
        layout: horizontal;
        height: 1fr;
    }

    #center-panel {
        width: 1fr;
    }

    #bottom-container {
        height: auto;
    }
    """

    def __init__(self, character_data: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.character_data = character_data

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        yield PlayerStatsPanel(self.character_data, id="player-stats")

        with Horizontal(id="main-container"):
            yield PartyPanel(id="party-panel")
            yield ActionPanel(id="action-panel")
            yield InventoryPanel(id="inventory-panel")

        yield DialoguePanel(id="dialogue-panel")

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        dialogue = self.query_one(DialoguePanel)
        dialogue.add_message("Welcome to Shards of Eternity!", "info")
        dialogue.add_message("The world awaits your adventure. Use the menu to navigate.", "info")
        dialogue.add_message("Type 'help' for available commands.", "info")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        dialogue = self.query_one(DialoguePanel)

        if event.button.id == "btn-explore":
            dialogue.add_message("You explore your surroundings...", "info")
            action_panel = self.query_one(ActionPanel)
            action_panel.update_content(
                "EXPLORING",
                "You venture forth into the unknown. Strange energies ripple through the air, "
                "and you sense the presence of a Crystal Shard nearby...",
                [("Continue", "btn-continue"), ("Return", "btn-return")]
            )

        elif event.button.id == "btn-rest":
            dialogue.add_message("You take a moment to rest and recover...", "success")
            dialogue.add_message("Health, Stamina, and Mana restored!", "success")

        elif event.button.id == "btn-talk":
            dialogue.add_message("You look around for someone to talk to...", "dialogue")

        elif event.button.id == "btn-search":
            dialogue.add_message("You search the area for items and secrets...", "info")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        dialogue = self.query_one(DialoguePanel)
        input_widget = event.input
        command = input_widget.value.strip().lower()

        if command:
            dialogue.add_message(f"> {input_widget.value}", "info")

            if command == "help":
                dialogue.add_message(
                    "Available commands: help, status, look, inventory, rest, quit",
                    "info"
                )
            elif command == "status":
                char = self.character_data or {}
                dialogue.add_message(
                    f"You are {char.get('name', 'Unknown')}, a Level {char.get('level', 1)} "
                    f"{char.get('race', 'Unknown')} {char.get('class', 'Unknown')}",
                    "info"
                )
            elif command == "look":
                dialogue.add_message("You survey your surroundings carefully...", "info")
            else:
                dialogue.add_message(f"Unknown command: {command}", "warning")

            input_widget.value = ""

    def action_travel(self) -> None:
        """Open travel screen."""
        dialogue = self.query_one(DialoguePanel)
        dialogue.add_message("Opening travel map...", "info")

    def action_inventory(self) -> None:
        """Open inventory screen."""
        dialogue = self.query_one(DialoguePanel)
        dialogue.add_message("Opening inventory...", "info")

    def action_character(self) -> None:
        """Open character screen."""
        dialogue = self.query_one(DialoguePanel)
        dialogue.add_message("Opening character sheet...", "info")

    def action_party(self) -> None:
        """Open party management."""
        dialogue = self.query_one(DialoguePanel)
        dialogue.add_message("Opening party management...", "info")

    def action_settings(self) -> None:
        """Open settings."""
        dialogue = self.query_one(DialoguePanel)
        dialogue.add_message("Opening settings...", "info")

    def action_quit_game(self) -> None:
        """Quit the game."""
        self.app.exit()
