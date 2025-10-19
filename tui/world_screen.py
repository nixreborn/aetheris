"""
World map and travel screen for Shards of Eternity.
Provides location navigation, travel options, and world state information.
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Grid
from textual.widgets import (
    Header, Footer, Static, Button, Label, ListView, ListItem,
    DataTable, ProgressBar
)
from textual.binding import Binding
from rich.text import Text
from rich.table import Table
from typing import Optional, Dict, Any, List, Callable
import logging

logger = logging.getLogger(__name__)


class LocationCard(Static):
    """A card displaying location information."""

    DEFAULT_CSS = """
    LocationCard {
        border: solid $primary;
        padding: 1;
        margin: 1;
        height: auto;
    }

    .location-name {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    .location-type {
        text-align: center;
        color: $accent;
        margin-bottom: 1;
    }

    .location-description {
        margin: 1 0;
    }

    .location-details {
        margin-top: 1;
        padding: 1;
        border: solid $primary-lighten-1;
    }

    .location-travel-btn {
        width: 100%;
        margin-top: 1;
    }

    .current-location {
        border: solid $success;
        background: $success-darken-3;
    }

    .danger-high {
        border: solid $error;
    }

    .danger-medium {
        border: solid $warning;
    }

    .danger-low {
        border: solid $success;
    }
    """

    def __init__(
        self,
        location_data: Dict[str, Any],
        is_current: bool = False,
        on_travel: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.location_data = location_data
        self.is_current = is_current
        self.on_travel = on_travel

        # Add danger class
        danger = location_data.get("danger_level", 1)
        if danger >= 7:
            self.add_class("danger-high")
        elif danger >= 4:
            self.add_class("danger-medium")
        else:
            self.add_class("danger-low")

        if is_current:
            self.add_class("current-location")

    def compose(self) -> ComposeResult:
        loc = self.location_data

        name = loc.get("name", "Unknown Location")
        if self.is_current:
            name += " [CURRENT]"

        yield Static(name, classes="location-name")
        yield Static(
            f"{loc.get('zone_type', 'area').title()} - Danger Level {loc.get('danger_level', 1)}",
            classes="location-type"
        )
        yield Static(
            loc.get("description", "A mysterious location shrouded in uncertainty."),
            classes="location-description"
        )

        with Vertical(classes="location-details"):
            faction = loc.get("faction_controlled", None)
            if faction:
                yield Static(f"[yellow]Controlled by:[/] {faction}")

            is_safe = loc.get("is_safe_zone", False)
            safe_text = "[green]Safe Zone[/]" if is_safe else "[red]Dangerous Area[/]"
            yield Static(f"[bold]Status:[/] {safe_text}")

            # Show connected locations
            connected = loc.get("connected_locations", [])
            if connected:
                conn_text = ", ".join(connected) if isinstance(connected, list) else connected
                yield Static(f"[dim]Connects to:[/] {conn_text}")

        if not self.is_current:
            yield Button("Travel Here", classes="location-travel-btn", variant="primary")


class ShardInfoPanel(Static):
    """Panel showing Crystal Shard distribution."""

    DEFAULT_CSS = """
    ShardInfoPanel {
        border: solid $accent;
        padding: 1;
        height: 100%;
    }

    .panel-title {
        text-align: center;
        text-style: bold;
        background: $accent;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #shard-table {
        margin: 1 0;
    }

    .shard-count {
        margin: 1 0;
        padding: 1;
        border: solid $primary-lighten-1;
    }
    """

    def __init__(self, shard_data: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.shard_data = shard_data or {}

    def compose(self) -> ComposeResult:
        yield Static("CRYSTAL SHARDS", classes="panel-title")

        # Shard distribution
        with Vertical(classes="shard-count"):
            total = 12
            claimed = self.shard_data.get("claimed", 0)
            unclaimed = total - claimed

            yield Static(f"[bold]Total Shards:[/] {total}")
            yield Static(f"[green]Claimed:[/] {claimed}")
            yield Static(f"[yellow]Unclaimed:[/] {unclaimed}")

        # Faction distribution
        yield Static("\n[bold]Faction Control:[/]")

        faction_counts = self.shard_data.get("faction_distribution", {})

        if faction_counts:
            for faction, count in faction_counts.items():
                if count > 0:
                    yield Static(f"  {faction}: {count} shard(s)")
        else:
            yield Static("[dim]  No shards claimed yet[/]")


class RealityStatePanel(Static):
    """Panel showing current reality state."""

    DEFAULT_CSS = """
    RealityStatePanel {
        border: solid $accent;
        padding: 1;
        height: 100%;
    }

    .panel-title {
        text-align: center;
        text-style: bold;
        background: $accent;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    .reality-info {
        margin: 1 0;
        padding: 1;
        border: solid $primary-lighten-1;
    }

    .stability-bar {
        height: 3;
        margin: 1 0;
    }
    """

    def __init__(self, reality_data: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.reality_data = reality_data or {
            "type": "Neutral",
            "stability": 100,
            "aetherfall_count": 0
        }

    def compose(self) -> ComposeResult:
        yield Static("REALITY STATE", classes="panel-title")

        with Vertical(classes="reality-info"):
            reality_type = self.reality_data.get("type", "Neutral")
            stability = self.reality_data.get("stability", 100)
            aetherfall = self.reality_data.get("aetherfall_count", 0)

            yield Static(f"[bold cyan]Current Reality:[/] {reality_type}")
            yield Static(f"[bold]Aetherfall Count:[/] {aetherfall}")

        with Vertical(classes="stability-bar"):
            yield Label(f"Reality Stability: {stability}%")
            bar = ProgressBar(total=100, show_eta=False)
            bar.update(progress=stability)
            yield bar


class NearbyPlayersPanel(Static):
    """Panel showing nearby players in the same location."""

    DEFAULT_CSS = """
    NearbyPlayersPanel {
        border: solid $success;
        padding: 1;
        height: 100%;
    }

    .panel-title {
        text-align: center;
        text-style: bold;
        background: $success;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    .player-entry {
        margin: 1 0;
        padding: 1;
        border: solid $primary-lighten-1;
    }
    """

    def __init__(self, players: Optional[List[Dict[str, Any]]] = None, **kwargs):
        super().__init__(**kwargs)
        self.players = players or []

    def compose(self) -> ComposeResult:
        yield Static("NEARBY PLAYERS", classes="panel-title")

        if self.players:
            for player in self.players:
                yield Static(
                    f"[bold]{player.get('name', 'Unknown')}[/]\n"
                    f"Lvl {player.get('level', 1)} {player.get('race', '')} {player.get('class', '')}\n"
                    f"[yellow]{player.get('faction', '')}[/]",
                    classes="player-entry"
                )
        else:
            yield Static("[dim]No other players nearby[/]", classes="player-entry")


class WorldMapPanel(Static):
    """ASCII-style world map display."""

    DEFAULT_CSS = """
    WorldMapPanel {
        border: solid $primary;
        padding: 1;
        height: 100%;
    }

    .panel-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #map-display {
        height: 100%;
        font-family: monospace;
    }
    """

    def __init__(self, current_location: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.current_location = current_location

    def compose(self) -> ComposeResult:
        yield Static("WORLD MAP", classes="panel-title")

        # Simple ASCII map
        map_art = """
        TPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW
        Q          SHARDS OF ETERNITY              Q
        Q                                          Q
        Q    [Mountains]     [Storm]               Q
        Q         ^             ~                  Q
        Q                                          Q
        Q   [Town]      [Forest]      [Ruins]      Q
        Q     #            `                      Q
        Q                                          Q
        Q           [YOU]                          Q
        Q             @                            Q
        Q                                          Q
        Q  [Volcano]              [Abyss]          Q
        Q     R                     K              Q
        Q                                          Q
        ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]

        Legend:
        @ - Your Location    # - Town/City
        ^ - Mountains        ` - Forest
        R - Volcano          K - Water/Abyss
        ~ - Shard Location    - Ruins/Dungeon
        """

        yield Static(map_art, id="map-display")


class WorldScreen(Screen):
    """Main world and travel screen."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("m", "toggle_map", "Toggle Map"),
        Binding("s", "show_shards", "Shards"),
        Binding("r", "show_reality", "Reality"),
        Binding("p", "show_players", "Players"),
    ]

    DEFAULT_CSS = """
    WorldScreen {
        layout: vertical;
    }

    #world-container {
        layout: horizontal;
        height: 1fr;
        padding: 1;
    }

    #left-world-column {
        width: 60%;
        padding-right: 1;
    }

    #right-world-column {
        width: 40%;
        padding-left: 1;
    }

    #locations-container {
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    .locations-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }

    #info-panels {
        layout: vertical;
        height: 100%;
    }

    .info-panel {
        height: 33%;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        current_location: str = "Starting Town",
        locations: Optional[List[Dict[str, Any]]] = None,
        on_travel: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.current_location = current_location
        self.locations = locations or self._get_default_locations()
        self.on_travel = on_travel
        self.show_map_view = False

    def _get_default_locations(self) -> List[Dict[str, Any]]:
        """Return default locations for display."""
        return [
            {
                "name": "Starting Town",
                "zone_type": "town",
                "description": "A peaceful settlement where adventurers gather before their journeys.",
                "danger_level": 1,
                "is_safe_zone": True,
                "faction_controlled": None,
                "connected_locations": ["Dark Forest", "Mountain Pass"]
            },
            {
                "name": "Dark Forest",
                "zone_type": "wilderness",
                "description": "Ancient trees loom overhead, their branches twisted by unknown magic.",
                "danger_level": 3,
                "is_safe_zone": False,
                "faction_controlled": "Moonlit Circle",
                "connected_locations": ["Starting Town", "Cursed Ruins"]
            },
            {
                "name": "Mountain Pass",
                "zone_type": "wilderness",
                "description": "A treacherous path winding through towering peaks.",
                "danger_level": 5,
                "is_safe_zone": False,
                "faction_controlled": "Iron Brotherhood",
                "connected_locations": ["Starting Town", "Titan's Spine Mountains"]
            },
            {
                "name": "Cursed Ruins",
                "zone_type": "dungeon",
                "description": "The remnants of a civilization destroyed by the first Aetherfall.",
                "danger_level": 7,
                "is_safe_zone": False,
                "faction_controlled": "Shadowborn",
                "connected_locations": ["Dark Forest"]
            },
            {
                "name": "Ember Volcano",
                "zone_type": "dungeon",
                "description": "A massive volcano where the Phoenix Flame shard awaits its challenger.",
                "danger_level": 10,
                "is_safe_zone": False,
                "faction_controlled": "Crimson Covenant",
                "connected_locations": ["Mountain Pass"],
                "has_shard": True,
                "shard_name": "Phoenix Flame"
            },
            {
                "name": "Celestial Cathedral",
                "zone_type": "faction_hq",
                "description": "The golden headquarters of the Golden Order, radiating holy light.",
                "danger_level": 2,
                "is_safe_zone": True,
                "faction_controlled": "Golden Order",
                "connected_locations": ["Starting Town"]
            }
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="world-container"):
            # Left: Locations list or map
            with Vertical(id="left-world-column"):
                with ScrollableContainer(id="locations-container"):
                    if self.show_map_view:
                        yield WorldMapPanel(self.current_location)
                    else:
                        yield Static("LOCATIONS", classes="locations-title")
                        for location in self.locations:
                            is_current = location.get("name") == self.current_location
                            yield LocationCard(
                                location,
                                is_current=is_current,
                                on_travel=self.on_travel
                            )

            # Right: Info panels
            with Vertical(id="right-world-column"):
                with Vertical(id="info-panels"):
                    yield ShardInfoPanel(
                        {
                            "claimed": 3,
                            "faction_distribution": {
                                "Crimson Covenant": 1,
                                "Aether Seekers": 1,
                                "Iron Brotherhood": 1
                            }
                        },
                        classes="info-panel"
                    )
                    yield RealityStatePanel(
                        {
                            "type": "Neutral",
                            "stability": 85,
                            "aetherfall_count": 0
                        },
                        classes="info-panel"
                    )
                    yield NearbyPlayersPanel(
                        [
                            {
                                "name": "Adventurer1",
                                "level": 5,
                                "race": "Elf",
                                "class": "Ranger",
                                "faction": "Moonlit Circle"
                            }
                        ],
                        classes="info-panel"
                    )

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle travel button presses."""
        # Find which location card was clicked
        location_card = event.button.parent
        if isinstance(location_card, LocationCard):
            location_name = location_card.location_data.get("name")

            if self.on_travel:
                self.on_travel(location_name)
            else:
                # Default behavior: update current location
                self.current_location = location_name
                self.refresh_locations()

    def refresh_locations(self) -> None:
        """Refresh the locations display."""
        container = self.query_one("#locations-container")
        container.remove_children()

        if self.show_map_view:
            container.mount(WorldMapPanel(self.current_location))
        else:
            container.mount(Static("LOCATIONS", classes="locations-title"))
            for location in self.locations:
                is_current = location.get("name") == self.current_location
                container.mount(
                    LocationCard(
                        location,
                        is_current=is_current,
                        on_travel=self.on_travel
                    )
                )

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()

    def action_toggle_map(self) -> None:
        """Toggle between list and map view."""
        self.show_map_view = not self.show_map_view
        self.refresh_locations()

    def action_show_shards(self) -> None:
        """Focus on shard information."""
        shard_panel = self.query_one(ShardInfoPanel)
        shard_panel.focus()

    def action_show_reality(self) -> None:
        """Focus on reality state."""
        reality_panel = self.query_one(RealityStatePanel)
        reality_panel.focus()

    def action_show_players(self) -> None:
        """Focus on nearby players."""
        players_panel = self.query_one(NearbyPlayersPanel)
        players_panel.focus()
