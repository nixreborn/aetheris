"""
Character creation and viewing screen for Shards of Eternity.
Provides interfaces for character creation wizard and character sheet display.
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Grid
from textual.widgets import (
    Header, Footer, Static, Button, Label, Input, Select,
    DataTable, ProgressBar, ListView, ListItem
)
from textual.binding import Binding
from textual.validation import Function, Number, Length
from rich.table import Table
from rich.text import Text
from typing import Optional, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class StatDisplay(Static):
    """Display a single stat with value and modifier."""

    DEFAULT_CSS = """
    StatDisplay {
        height: 3;
        border: solid $primary-lighten-1;
        padding: 1;
        margin: 0 1 1 0;
    }

    .stat-value {
        text-align: center;
        text-style: bold;
        color: $accent;
    }

    .stat-modifier {
        text-align: center;
        color: $success;
    }
    """

    def __init__(self, stat_name: str, value: int, **kwargs):
        super().__init__(**kwargs)
        self.stat_name = stat_name
        self.value = value
        self.modifier = (value - 10) // 2

    def compose(self) -> ComposeResult:
        yield Label(f"[bold]{self.stat_name.upper()}[/]")
        yield Static(f"{self.value}", classes="stat-value")
        mod_sign = "+" if self.modifier >= 0 else ""
        yield Static(f"({mod_sign}{self.modifier})", classes="stat-modifier")

    def update_value(self, value: int) -> None:
        """Update the stat value."""
        self.value = value
        self.modifier = (value - 10) // 2
        value_widget = self.query(Static)[0]
        value_widget.update(f"{self.value}")
        mod_widget = self.query(Static)[1]
        mod_sign = "+" if self.modifier >= 0 else ""
        mod_widget.update(f"({mod_sign}{self.modifier})")


class CharacterCreationWizard(Container):
    """Character creation wizard with step-by-step process."""

    DEFAULT_CSS = """
    CharacterCreationWizard {
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    #wizard-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }

    #wizard-content {
        height: 1fr;
        padding: 1;
    }

    #wizard-buttons {
        height: 5;
        align: center middle;
        padding: 1;
    }

    .wizard-button {
        margin: 0 2;
        min-width: 15;
    }

    .form-label {
        margin: 1 0;
        text-style: bold;
    }

    .form-input {
        width: 100%;
        margin-bottom: 2;
    }

    #stats-grid {
        grid-size: 3;
        grid-gutter: 1;
        margin: 2 0;
    }

    .stat-input-container {
        height: 5;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_step = 1
        self.character_data = {
            "name": "",
            "race": "Human",
            "class": "Warrior",
            "faction": "Crimson Covenant",
            "stats": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }

    def compose(self) -> ComposeResult:
        yield Static("CHARACTER CREATION", id="wizard-title")

        with ScrollableContainer(id="wizard-content"):
            yield self.get_step_content()

        with Horizontal(id="wizard-buttons"):
            yield Button("Back", id="btn-back", classes="wizard-button")
            yield Button("Next", id="btn-next", classes="wizard-button", variant="primary")
            yield Button("Cancel", id="btn-cancel", classes="wizard-button", variant="error")

    def get_step_content(self) -> Container:
        """Get content for the current step."""
        if self.current_step == 1:
            return self.step_1_name()
        elif self.current_step == 2:
            return self.step_2_race()
        elif self.current_step == 3:
            return self.step_3_class()
        elif self.current_step == 4:
            return self.step_4_faction()
        elif self.current_step == 5:
            return self.step_5_stats()
        else:
            return self.step_6_summary()

    def step_1_name(self) -> Container:
        """Step 1: Name selection."""
        container = Vertical()
        container.mount(Static("Step 1: Choose Your Name", classes="form-label"))
        container.mount(Static(
            "Your name will be known across the realms. Choose wisely.",
            classes="form-label"
        ))
        container.mount(Input(
            placeholder="Enter character name (3-50 characters)",
            id="input-name",
            classes="form-input",
            value=self.character_data.get("name", "")
        ))
        return container

    def step_2_race(self) -> Container:
        """Step 2: Race selection."""
        container = Vertical()
        container.mount(Static("Step 2: Choose Your Race", classes="form-label"))

        races = [
            ("Human", "+1 to all stats - Versatile and adaptable"),
            ("Elf", "+2 DEX, +1 INT, +1 WIS - Graceful and wise"),
            ("Dwarf", "+2 CON, +1 STR, +1 WIS - Hardy and resilient"),
            ("Tiefling", "+2 CHA, +1 INT - Infernal heritage grants power"),
            ("Dragonborn", "+2 STR, +1 CHA - Draconic might and presence"),
            ("Undead", "+2 INT, -1 CON, -1 CHA - Freed from mortality's limits")
        ]

        for race, description in races:
            is_selected = race == self.character_data.get("race", "Human")
            style = "reverse" if is_selected else ""
            container.mount(Button(
                f"{race}\n{description}",
                id=f"race-{race.lower()}",
                classes=f"wizard-button {style}"
            ))

        return container

    def step_3_class(self) -> Container:
        """Step 3: Class selection."""
        container = Vertical()
        container.mount(Static("Step 3: Choose Your Class", classes="form-label"))

        classes = [
            ("Warrior", "Masters of melee combat and defense"),
            ("Sorcerer", "Wielders of powerful arcane magic"),
            ("Rogue", "Agile strikers and cunning tacticians"),
            ("Paladin", "Holy warriors blending might and magic"),
            ("Necromancer", "Dark mages commanding death itself"),
            ("Ranger", "Skilled hunters and nature's champions")
        ]

        for char_class, description in classes:
            is_selected = char_class == self.character_data.get("class", "Warrior")
            style = "reverse" if is_selected else ""
            container.mount(Button(
                f"{char_class}\n{description}",
                id=f"class-{char_class.lower()}",
                classes=f"wizard-button {style}"
            ))

        return container

    def step_4_faction(self) -> Container:
        """Step 4: Faction selection."""
        container = Vertical()
        container.mount(Static("Step 4: Choose Your Faction", classes="form-label"))

        factions = [
            ("Crimson Covenant", "Blood magic and primal power"),
            ("Aether Seekers", "Masters of arcane knowledge"),
            ("Iron Brotherhood", "Industrial might and technology"),
            ("Moonlit Circle", "Twilight magic and balance"),
            ("Shadowborn", "Stealth and shadow manipulation"),
            ("Golden Order", "Divine radiance and order")
        ]

        for faction, description in factions:
            is_selected = faction == self.character_data.get("faction", "Crimson Covenant")
            style = "reverse" if is_selected else ""
            container.mount(Button(
                f"{faction}\n{description}",
                id=f"faction-{faction.lower().replace(' ', '-')}",
                classes=f"wizard-button {style}"
            ))

        return container

    def step_5_stats(self) -> Container:
        """Step 5: Stat allocation."""
        container = Vertical()
        container.mount(Static("Step 5: Allocate Your Stats", classes="form-label"))
        container.mount(Static(
            "You have 60 points to distribute. Each stat starts at 10.\n"
            "Stats range from 3 to 18 before racial modifiers.",
            classes="form-label"
        ))

        with Grid(id="stats-grid"):
            for stat_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                stat_value = self.character_data["stats"].get(stat_name, 10)
                with Vertical(classes="stat-input-container"):
                    container.mount(Static(f"{stat_name.capitalize()}:"))
                    container.mount(Input(
                        placeholder="3-18",
                        id=f"stat-{stat_name}",
                        value=str(stat_value),
                        type="integer"
                    ))

        return container

    def step_6_summary(self) -> Container:
        """Step 6: Summary and confirmation."""
        container = Vertical()
        container.mount(Static("Step 6: Confirm Your Character", classes="form-label"))

        char = self.character_data
        summary = (
            f"[bold cyan]Name:[/] {char['name']}\n"
            f"[bold]Race:[/] {char['race']}\n"
            f"[bold]Class:[/] {char['class']}\n"
            f"[bold]Faction:[/] {char['faction']}\n\n"
            f"[bold]Stats:[/]\n"
        )

        for stat_name, value in char["stats"].items():
            modifier = (value - 10) // 2
            mod_sign = "+" if modifier >= 0 else ""
            summary += f"  {stat_name.capitalize()}: {value} ({mod_sign}{modifier})\n"

        container.mount(Static(summary))
        container.mount(Static(
            "\n[bold green]Press 'Create Character' to begin your adventure![/]",
            classes="form-label"
        ))

        return container


class CharacterSheetScreen(Screen):
    """Display detailed character sheet."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    DEFAULT_CSS = """
    CharacterSheetScreen {
        layout: vertical;
    }

    #char-sheet-container {
        layout: horizontal;
        height: 1fr;
        padding: 1;
    }

    #left-column {
        width: 50%;
        padding-right: 1;
    }

    #right-column {
        width: 50%;
        padding-left: 1;
    }

    #char-header {
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    #stats-section {
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    #stats-grid {
        grid-size: 3;
        grid-gutter: 1;
        margin: 1 0;
    }

    #resources-section {
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    #equipment-section {
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
        height: 100%;
    }

    #derived-stats-section {
        border: solid $primary;
        padding: 1;
        height: 100%;
    }

    .section-title {
        text-style: bold;
        text-align: center;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    .resource-bar {
        height: 3;
        margin-bottom: 1;
    }
    """

    def __init__(self, character_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.character_data = character_data

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="char-sheet-container"):
            with Vertical(id="left-column"):
                yield self.create_header_section()
                yield self.create_stats_section()
                yield self.create_resources_section()

            with Vertical(id="right-column"):
                yield self.create_equipment_section()
                yield self.create_derived_stats_section()

        yield Footer()

    def create_header_section(self) -> Container:
        """Create the character header section."""
        char = self.character_data
        container = Vertical(id="char-header")
        container.mount(Static("CHARACTER INFORMATION", classes="section-title"))

        info = (
            f"[bold cyan]{char.get('name', 'Unknown')}[/]\n"
            f"Level {char.get('level', 1)} {char.get('race', 'Unknown')} {char.get('class', 'Unknown')}\n"
            f"Faction: [yellow]{char.get('faction', 'Unknown')}[/]\n"
            f"Experience: {char.get('experience', 0)} / {char.get('next_level_xp', 100)}\n"
            f"Souls: [gold1]{char.get('souls', 0)}[/]"
        )

        container.mount(Static(info))
        return container

    def create_stats_section(self) -> Container:
        """Create the stats section."""
        container = Vertical(id="stats-section")
        container.mount(Static("ATTRIBUTES", classes="section-title"))

        stats_grid = Grid(id="stats-grid")
        char_stats = self.character_data.get("stats", {})

        for stat_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            value = char_stats.get(stat_name, 10)
            stats_grid.mount(StatDisplay(stat_name, value))

        container.mount(stats_grid)
        return container

    def create_resources_section(self) -> Container:
        """Create the resources section."""
        char = self.character_data
        resources = char.get("resources", {})

        container = Vertical(id="resources-section")
        container.mount(Static("RESOURCES", classes="section-title"))

        # Parse health string like "100/100"
        health = resources.get("health", "100/100")
        if isinstance(health, str) and "/" in health:
            current_hp, max_hp = map(int, health.split("/"))
        else:
            current_hp, max_hp = 100, 100

        stamina = resources.get("stamina", "100/100")
        if isinstance(stamina, str) and "/" in stamina:
            current_st, max_st = map(int, stamina.split("/"))
        else:
            current_st, max_st = 100, 100

        mana = resources.get("mana", "100/100")
        if isinstance(mana, str) and "/" in mana:
            current_mp, max_mp = map(int, mana.split("/"))
        else:
            current_mp, max_mp = 100, 100

        container.mount(self.create_resource_bar("Health", current_hp, max_hp, "red"))
        container.mount(self.create_resource_bar("Stamina", current_st, max_st, "yellow"))
        container.mount(self.create_resource_bar("Mana", current_mp, max_mp, "blue"))

        return container

    def create_resource_bar(self, label: str, current: int, maximum: int, color: str) -> Container:
        """Create a resource bar widget."""
        container = Vertical(classes="resource-bar")
        container.mount(Label(f"{label}: {current}/{maximum}"))
        bar = ProgressBar(total=maximum, show_eta=False)
        bar.update(progress=current)
        container.mount(bar)
        return container

    def create_equipment_section(self) -> Container:
        """Create the equipment section."""
        container = ScrollableContainer(id="equipment-section")
        container.mount(Static("EQUIPMENT", classes="section-title"))

        equipped = self.character_data.get("equipped_items", [])

        if equipped:
            for item in equipped:
                item_text = f"[bold]{item.get('name', 'Unknown')}[/] [{item.get('type', 'item')}]"
                if item.get('attack_bonus'):
                    item_text += f"\n  +{item['attack_bonus']} Attack"
                if item.get('defense_bonus'):
                    item_text += f"\n  +{item['defense_bonus']} Defense"
                if item.get('magic_bonus'):
                    item_text += f"\n  +{item['magic_bonus']} Magic"

                container.mount(Static(item_text + "\n"))
        else:
            container.mount(Static("[dim]No equipment[/]"))

        return container

    def create_derived_stats_section(self) -> Container:
        """Create the derived stats section."""
        container = ScrollableContainer(id="derived-stats-section")
        container.mount(Static("DERIVED STATISTICS", classes="section-title"))

        derived = self.character_data.get("derived_stats", {})
        equipment = derived.get("equipment_bonuses", {})

        stats_text = (
            f"[bold]Armor Class:[/] {derived.get('armor_class', 10)}\n"
            f"[bold]Initiative:[/] +{derived.get('initiative', 0)}\n"
            f"[bold]Attack Power:[/] {derived.get('attack_power', 0)}\n"
            f"[bold]Magic Power:[/] {derived.get('magic_power', 0)}\n\n"
            f"[bold]Equipment Bonuses:[/]\n"
            f"  Attack: +{equipment.get('attack', 0)}\n"
            f"  Defense: +{equipment.get('defense', 0)}\n"
            f"  Magic: +{equipment.get('magic', 0)}\n"
        )

        container.mount(Static(stats_text))

        return container

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class CharacterCreationScreen(Screen):
    """Screen for creating a new character."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, on_complete: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.on_complete = on_complete

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield CharacterCreationWizard(id="wizard")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle wizard button presses."""
        wizard = self.query_one(CharacterCreationWizard)

        if event.button.id == "btn-next":
            if wizard.current_step < 6:
                wizard.current_step += 1
                content_container = wizard.query_one("#wizard-content")
                content_container.remove_children()
                content_container.mount(wizard.get_step_content())
            else:
                # Create character
                if self.on_complete:
                    self.on_complete(wizard.character_data)
                self.app.pop_screen()

        elif event.button.id == "btn-back":
            if wizard.current_step > 1:
                wizard.current_step -= 1
                content_container = wizard.query_one("#wizard-content")
                content_container.remove_children()
                content_container.mount(wizard.get_step_content())

        elif event.button.id == "btn-cancel":
            self.action_cancel()

        # Handle race selection
        elif event.button.id and event.button.id.startswith("race-"):
            race = event.button.id.replace("race-", "").capitalize()
            wizard.character_data["race"] = race
            content_container = wizard.query_one("#wizard-content")
            content_container.remove_children()
            content_container.mount(wizard.get_step_content())

        # Handle class selection
        elif event.button.id and event.button.id.startswith("class-"):
            char_class = event.button.id.replace("class-", "").capitalize()
            wizard.character_data["class"] = char_class
            content_container = wizard.query_one("#wizard-content")
            content_container.remove_children()
            content_container.mount(wizard.get_step_content())

        # Handle faction selection
        elif event.button.id and event.button.id.startswith("faction-"):
            faction = event.button.id.replace("faction-", "").replace("-", " ").title()
            wizard.character_data["faction"] = faction
            content_container = wizard.query_one("#wizard-content")
            content_container.remove_children()
            content_container.mount(wizard.get_step_content())

    def action_cancel(self) -> None:
        """Cancel character creation."""
        self.app.pop_screen()
