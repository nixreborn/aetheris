"""
Combat interface TUI for Shards of Eternity.
Provides turn-based combat visualization with enemies, actions, and combat log.
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Grid
from textual.widgets import (
    Header, Footer, Static, Button, Label, ProgressBar, RichLog, ListView, ListItem
)
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from typing import Optional, Dict, Any, List, Callable
import logging

logger = logging.getLogger(__name__)


class EnemyDisplay(Static):
    """Display a single enemy with health bar and status effects."""

    DEFAULT_CSS = """
    EnemyDisplay {
        border: solid $error;
        padding: 1;
        margin: 1;
        height: 12;
    }

    .enemy-name {
        text-align: center;
        text-style: bold;
        color: $error;
        background: $error-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }

    .enemy-level {
        text-align: center;
        color: $warning;
    }

    .enemy-health-bar {
        height: 3;
        margin: 1 0;
    }

    .enemy-status {
        text-align: center;
        margin-top: 1;
    }
    """

    def __init__(self, enemy_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.enemy_data = enemy_data

    def compose(self) -> ComposeResult:
        enemy = self.enemy_data

        yield Static(enemy.get("name", "Unknown Enemy"), classes="enemy-name")
        yield Static(f"Level {enemy.get('level', 1)} - {enemy.get('type', 'Enemy')}", classes="enemy-level")

        with Vertical(classes="enemy-health-bar"):
            health = enemy.get("health", 100)
            max_health = enemy.get("max_health", 100)
            yield Label(f"HP: {health}/{max_health}")
            bar = ProgressBar(total=max_health, show_eta=False)
            bar.update(progress=health)
            yield bar

        status_effects = enemy.get("status_effects", [])
        if status_effects:
            effects_text = ", ".join(status_effects)
            yield Static(f"[yellow]Status:[/] {effects_text}", classes="enemy-status")
        else:
            yield Static("[dim]No status effects[/]", classes="enemy-status")

    def update_health(self, current: int, maximum: int) -> None:
        """Update the enemy's health display."""
        self.enemy_data["health"] = current
        self.enemy_data["max_health"] = maximum

        label = self.query_one(Label)
        label.update(f"HP: {current}/{maximum}")

        bar = self.query_one(ProgressBar)
        bar.update(total=maximum, progress=current)


class PlayerCombatPanel(Static):
    """Display player status during combat."""

    DEFAULT_CSS = """
    PlayerCombatPanel {
        border: solid $success;
        padding: 1;
        height: 15;
    }

    .player-name {
        text-align: center;
        text-style: bold;
        color: $success;
        background: $success-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }

    .resource-bar {
        height: 2;
        margin-bottom: 1;
    }

    .combat-stats {
        margin-top: 1;
        padding: 1;
        border: solid $primary-lighten-1;
    }
    """

    def __init__(self, character_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.character_data = character_data

    def compose(self) -> ComposeResult:
        char = self.character_data

        yield Static(char.get("name", "Player"), classes="player-name")

        # Health
        with Vertical(classes="resource-bar"):
            health = char.get("health", 100)
            max_health = char.get("max_health", 100)
            yield Label(f"[red]Health:[/] {health}/{max_health}")
            bar = ProgressBar(total=max_health, show_eta=False)
            bar.update(progress=health)
            yield bar

        # Stamina
        with Vertical(classes="resource-bar"):
            stamina = char.get("stamina", 100)
            max_stamina = char.get("max_stamina", 100)
            yield Label(f"[yellow]Stamina:[/] {stamina}/{max_stamina}")
            bar = ProgressBar(total=max_stamina, show_eta=False)
            bar.update(progress=stamina)
            yield bar

        # Mana
        with Vertical(classes="resource-bar"):
            mana = char.get("mana", 100)
            max_mana = char.get("max_mana", 100)
            yield Label(f"[blue]Mana:[/] {mana}/{max_mana}")
            bar = ProgressBar(total=max_mana, show_eta=False)
            bar.update(progress=mana)
            yield bar

        # Combat stats
        with Vertical(classes="combat-stats"):
            attack = char.get("attack_power", 10)
            defense = char.get("armor_class", 10)
            yield Static(
                f"[bold]ATK:[/] {attack}  [bold]DEF:[/] {defense}\n"
                f"[bold]Initiative:[/] +{char.get('initiative', 0)}"
            )


class CombatActionMenu(Static):
    """Combat action menu with buttons for different actions."""

    DEFAULT_CSS = """
    CombatActionMenu {
        border: solid $primary;
        padding: 1;
        height: 100%;
    }

    .menu-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #action-grid {
        grid-size: 2;
        grid-gutter: 1;
        margin: 1 0;
    }

    .combat-action-btn {
        width: 100%;
        height: 5;
        margin: 0 0 1 0;
    }

    .ability-list {
        height: 100%;
        border: solid $primary-lighten-1;
        padding: 1;
        margin-top: 1;
    }
    """

    def __init__(self, abilities: Optional[List[Dict[str, Any]]] = None, **kwargs):
        super().__init__(**kwargs)
        self.abilities = abilities or []
        self.current_mode = "main"  # main, abilities, items

    def compose(self) -> ComposeResult:
        yield Static("COMBAT ACTIONS", classes="menu-title")

        with Grid(id="action-grid"):
            yield Button("Attack", id="combat-attack", classes="combat-action-btn", variant="primary")
            yield Button("Abilities", id="combat-abilities", classes="combat-action-btn")
            yield Button("Items", id="combat-items", classes="combat-action-btn")
            yield Button("Dodge", id="combat-dodge", classes="combat-action-btn", variant="success")
            yield Button("Block", id="combat-block", classes="combat-action-btn", variant="warning")
            yield Button("Flee", id="combat-flee", classes="combat-action-btn", variant="error")

        with ScrollableContainer(classes="ability-list"):
            if self.abilities:
                for ability in self.abilities:
                    yield Static(
                        f"[bold]{ability.get('name', 'Unknown')}[/]\n"
                        f"[dim]{ability.get('description', '')}[/]\n"
                        f"Cost: {ability.get('cost', 0)} {ability.get('cost_type', 'MP')}"
                    )
            else:
                yield Static("[dim]No special abilities[/]")


class CombatLogPanel(Static):
    """Combat log showing actions and results."""

    DEFAULT_CSS = """
    CombatLogPanel {
        border: solid $primary;
        padding: 1;
        height: 100%;
    }

    .log-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #combat-log {
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("COMBAT LOG", classes="log-title")
        yield RichLog(id="combat-log", highlight=True, markup=True)

    def add_log(self, message: str, log_type: str = "info") -> None:
        """Add a message to the combat log."""
        log = self.query_one(RichLog)

        color_map = {
            "info": "cyan",
            "attack": "orange1",
            "damage": "red",
            "heal": "green",
            "defend": "yellow",
            "ability": "magenta",
            "critical": "bold red",
            "miss": "dim white"
        }

        color = color_map.get(log_type, "white")
        log.write(f"[{color}]{message}[/]")

    def clear(self) -> None:
        """Clear the combat log."""
        log = self.query_one(RichLog)
        log.clear()


class TurnIndicator(Static):
    """Shows whose turn it is."""

    DEFAULT_CSS = """
    TurnIndicator {
        height: 3;
        text-align: center;
        text-style: bold;
        padding: 1;
        border: solid $accent;
        background: $accent-darken-3;
    }
    """

    def __init__(self, is_player_turn: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.is_player_turn = is_player_turn

    def compose(self) -> ComposeResult:
        if self.is_player_turn:
            yield Static("[bold green]YOUR TURN[/] - Choose an action")
        else:
            yield Static("[bold red]ENEMY TURN[/] - Preparing to act...")

    def set_turn(self, is_player_turn: bool) -> None:
        """Update the turn indicator."""
        self.is_player_turn = is_player_turn
        self.remove_children()

        if is_player_turn:
            self.mount(Static("[bold green]YOUR TURN[/] - Choose an action"))
        else:
            self.mount(Static("[bold red]ENEMY TURN[/] - Preparing to act..."))


class CombatScreen(Screen):
    """Main combat screen."""

    BINDINGS = [
        Binding("1", "quick_attack", "Attack"),
        Binding("2", "quick_ability", "Ability"),
        Binding("3", "quick_item", "Item"),
        Binding("d", "quick_dodge", "Dodge"),
        Binding("b", "quick_block", "Block"),
        Binding("f", "quick_flee", "Flee"),
        Binding("escape", "try_flee", "Flee"),
    ]

    DEFAULT_CSS = """
    CombatScreen {
        layout: vertical;
    }

    #combat-container {
        layout: horizontal;
        height: 1fr;
        padding: 1;
    }

    #left-combat-column {
        width: 30%;
        padding-right: 1;
    }

    #center-combat-column {
        width: 40%;
        padding: 0 1;
    }

    #right-combat-column {
        width: 30%;
        padding-left: 1;
    }

    #enemies-container {
        height: 60%;
        border: solid $error;
        padding: 1;
        margin-bottom: 1;
    }

    #enemies-title {
        text-align: center;
        text-style: bold;
        background: $error;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #player-container {
        height: 40%;
    }

    #turn-indicator {
        margin-bottom: 1;
    }

    #action-menu-container {
        height: 100%;
    }

    #combat-log-container {
        height: 100%;
    }
    """

    def __init__(
        self,
        character_data: Dict[str, Any],
        enemies: List[Dict[str, Any]],
        on_combat_end: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.character_data = character_data
        self.enemies = enemies
        self.on_combat_end = on_combat_end
        self.is_player_turn = True
        self.turn_count = 1

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        yield TurnIndicator(self.is_player_turn, id="turn-indicator")

        with Horizontal(id="combat-container"):
            # Left: Player status
            with Vertical(id="left-combat-column"):
                with Vertical(id="player-container"):
                    yield PlayerCombatPanel(self.character_data, id="player-panel")

            # Center: Enemies
            with Vertical(id="center-combat-column"):
                with ScrollableContainer(id="enemies-container"):
                    yield Static("ENEMIES", id="enemies-title")
                    for i, enemy in enumerate(self.enemies):
                        yield EnemyDisplay(enemy, id=f"enemy-{i}")

            # Right: Actions and log
            with Vertical(id="right-combat-column"):
                with Vertical(id="action-menu-container"):
                    abilities = [
                        {
                            "name": "Power Strike",
                            "description": "A powerful melee attack",
                            "cost": 20,
                            "cost_type": "Stamina"
                        },
                        {
                            "name": "Fireball",
                            "description": "Launch a ball of fire",
                            "cost": 30,
                            "cost_type": "Mana"
                        }
                    ]
                    yield CombatActionMenu(abilities, id="action-menu")

                with Vertical(id="combat-log-container"):
                    yield CombatLogPanel(id="combat-log")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize combat log."""
        log = self.query_one(CombatLogPanel)
        log.add_log(f"Combat begins! Turn {self.turn_count}", "info")
        log.add_log(f"You face {len(self.enemies)} enemy/enemies!", "info")

        for enemy in self.enemies:
            log.add_log(f"  - {enemy.get('name', 'Unknown')} (Lvl {enemy.get('level', 1)})", "info")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle combat action button presses."""
        if not self.is_player_turn:
            return

        log = self.query_one(CombatLogPanel)

        if event.button.id == "combat-attack":
            self.perform_attack()

        elif event.button.id == "combat-abilities":
            log.add_log("Opening abilities menu...", "info")

        elif event.button.id == "combat-items":
            log.add_log("Opening items menu...", "info")

        elif event.button.id == "combat-dodge":
            self.perform_dodge()

        elif event.button.id == "combat-block":
            self.perform_block()

        elif event.button.id == "combat-flee":
            self.attempt_flee()

    def perform_attack(self) -> None:
        """Perform a basic attack."""
        log = self.query_one(CombatLogPanel)

        if not self.enemies:
            log.add_log("No enemies to attack!", "info")
            return

        # Attack first enemy
        enemy = self.enemies[0]
        enemy_display = self.query_one(f"#enemy-0", EnemyDisplay)

        damage = 15  # Calculate actual damage
        new_health = max(0, enemy.get("health", 100) - damage)

        enemy["health"] = new_health
        enemy_display.update_health(new_health, enemy.get("max_health", 100))

        log.add_log(f"You attack {enemy.get('name', 'Enemy')} for {damage} damage!", "attack")

        if new_health <= 0:
            log.add_log(f"{enemy.get('name', 'Enemy')} is defeated!", "critical")

        self.end_player_turn()

    def perform_dodge(self) -> None:
        """Perform dodge action."""
        log = self.query_one(CombatLogPanel)
        log.add_log("You prepare to dodge the next attack!", "defend")
        self.end_player_turn()

    def perform_block(self) -> None:
        """Perform block action."""
        log = self.query_one(CombatLogPanel)
        log.add_log("You raise your guard to block incoming attacks!", "defend")
        self.end_player_turn()

    def attempt_flee(self) -> None:
        """Attempt to flee from combat."""
        log = self.query_one(CombatLogPanel)

        # 50% chance to flee
        import random
        if random.random() < 0.5:
            log.add_log("You successfully flee from combat!", "info")
            if self.on_combat_end:
                self.on_combat_end({"result": "fled", "player_victory": False})
            self.app.pop_screen()
        else:
            log.add_log("You failed to escape!", "damage")
            self.end_player_turn()

    def end_player_turn(self) -> None:
        """End the player's turn and start enemy turn."""
        self.is_player_turn = False
        turn_indicator = self.query_one(TurnIndicator)
        turn_indicator.set_turn(False)

        # Simulate enemy turn
        self.set_timer(1.5, self.perform_enemy_turn)

    def perform_enemy_turn(self) -> None:
        """Perform enemy actions."""
        log = self.query_one(CombatLogPanel)

        for enemy in self.enemies:
            if enemy.get("health", 0) > 0:
                damage = 10  # Calculate enemy damage
                log.add_log(
                    f"{enemy.get('name', 'Enemy')} attacks you for {damage} damage!",
                    "damage"
                )

        # Start new turn
        self.turn_count += 1
        self.is_player_turn = True
        turn_indicator = self.query_one(TurnIndicator)
        turn_indicator.set_turn(True)
        log.add_log(f"\nTurn {self.turn_count}", "info")

    def action_quick_attack(self) -> None:
        """Quick attack with hotkey."""
        if self.is_player_turn:
            self.perform_attack()

    def action_quick_ability(self) -> None:
        """Quick ability with hotkey."""
        log = self.query_one(CombatLogPanel)
        log.add_log("Select an ability to use", "info")

    def action_quick_item(self) -> None:
        """Quick item with hotkey."""
        log = self.query_one(CombatLogPanel)
        log.add_log("Select an item to use", "info")

    def action_quick_dodge(self) -> None:
        """Quick dodge with hotkey."""
        if self.is_player_turn:
            self.perform_dodge()

    def action_quick_block(self) -> None:
        """Quick block with hotkey."""
        if self.is_player_turn:
            self.perform_block()

    def action_quick_flee(self) -> None:
        """Quick flee with hotkey."""
        self.attempt_flee()

    def action_try_flee(self) -> None:
        """Attempt to flee via escape key."""
        self.attempt_flee()
