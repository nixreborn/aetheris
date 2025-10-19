# LLM Integration Examples for Game Systems

This document shows how to integrate the LLM module with various game systems in Shards of Eternity.

## Table of Contents

1. [World/Location Integration](#worldlocation-integration)
2. [NPC System Integration](#npc-system-integration)
3. [Combat System Integration](#combat-system-integration)
4. [Event System Integration](#event-system-integration)
5. [TUI/Display Integration](#tuidisplay-integration)

---

## World/Location Integration

### Basic Location Entry

```python
# In world/locations.py or similar

from llm import get_llm_generator
from dataclasses import dataclass
from typing import Optional

@dataclass
class Location:
    name: str
    base_description: str
    features: list[str]
    reality_type: str  # stable, fractured, corrupted

class WorldManager:
    def __init__(self):
        self.llm = get_llm_generator()

    async def get_location_description(self, location: Location) -> str:
        """Get dynamic description for a location."""
        context = {
            "description": location.base_description,
            "features": location.features,
            "reality_type": location.reality_type
        }

        description = await self.llm.generate_location_description(
            location_name=location.name,
            reality_type=location.reality_type,
            context=context
        )

        return description

    async def player_enters_location(self, player, location: Location):
        """Handle player entering a new location."""
        description = await self.get_location_description(location)

        # Display to player
        await player.send_message(f"\n=== {location.name} ===")
        await player.send_message(description)
        await player.send_message("")
```

### Reality Shift Events

```python
async def handle_reality_shift(self, location: Location, old_type: str, new_type: str):
    """Generate description when reality shifts."""
    # Update location
    location.reality_type = new_type

    # Generate new description
    description = await self.llm.generate_location_description(
        location_name=location.name,
        reality_type=new_type,
        context={
            "features": location.features,
            "previous_reality": old_type
        }
    )

    # Generate event narrative
    event_narrative = await self.llm.generate_event_narrative(
        event_type="reality_shift",
        context={
            "location": location.name,
            "old_reality": old_type,
            "new_reality": new_type,
            "participants": [p.name for p in self.get_players_in_location(location)]
        }
    )

    # Broadcast to all players in location
    for player in self.get_players_in_location(location):
        await player.send_message(f"\n{event_narrative}\n")
        await player.send_message(description)
```

---

## NPC System Integration

### NPC Dialogue System

```python
# In characters/npc.py or similar

from llm import get_llm_generator
from dataclasses import dataclass
from typing import Optional

@dataclass
class NPC:
    name: str
    background: str
    personality: str
    state: str  # friendly, hostile, neutral, mad

class NPCManager:
    def __init__(self):
        self.llm = get_llm_generator()

    async def generate_greeting(self, npc: NPC, player) -> str:
        """Generate NPC greeting when player approaches."""
        context = f"{npc.name} sees {player.name} approach. Current state: {npc.state}"

        dialogue = await self.llm.generate_npc_dialogue(
            npc_name=npc.name,
            context=context,
            player_action="approaches",
            npc_background=f"{npc.background}. Personality: {npc.personality}"
        )

        return dialogue

    async def handle_player_question(
        self,
        npc: NPC,
        player,
        question: str
    ) -> str:
        """Handle player asking NPC a question."""
        context = (
            f"Location: {player.current_location}. "
            f"NPC's state: {npc.state}. "
            f"Previous interactions: {self.get_interaction_count(player, npc)}"
        )

        dialogue = await self.llm.generate_npc_dialogue(
            npc_name=npc.name,
            context=context,
            player_action=f"asks: '{question}'",
            npc_background=npc.background
        )

        # Track interaction
        self.record_interaction(player, npc)

        return dialogue

    async def handle_player_action(
        self,
        npc: NPC,
        player,
        action: str,
        action_context: str
    ) -> str:
        """Handle any player action toward NPC."""
        dialogue = await self.llm.generate_npc_dialogue(
            npc_name=npc.name,
            context=action_context,
            player_action=action,
            npc_background=npc.background
        )

        return dialogue
```

### Dynamic NPC Responses

```python
class InteractiveNPC:
    """NPC that generates dynamic responses."""

    def __init__(self, name: str, background: str):
        self.name = name
        self.background = background
        self.llm = get_llm_generator()
        self.conversation_history = []

    async def respond(self, player_input: str, game_context: dict) -> str:
        """Generate response to player input."""
        # Build context from history and current state
        context_parts = [
            f"Location: {game_context.get('location', 'Unknown')}",
            f"Time: {game_context.get('time', 'Unknown')}",
        ]

        if self.conversation_history:
            recent = self.conversation_history[-3:]  # Last 3 exchanges
            context_parts.append(
                f"Recent conversation: {'; '.join(recent)}"
            )

        context = " | ".join(context_parts)

        # Generate response
        response = await self.llm.generate_npc_dialogue(
            npc_name=self.name,
            context=context,
            player_action=player_input,
            npc_background=self.background
        )

        # Track conversation
        self.conversation_history.append(
            f"Player: {player_input} | {self.name}: {response}"
        )

        return response
```

---

## Combat System Integration

### Combat Action Descriptions

```python
# In combat/system.py or similar

from llm import get_llm_generator
from dataclasses import dataclass
from typing import Optional

@dataclass
class CombatAction:
    attacker_name: str
    defender_name: str
    action_type: str  # attack, defend, ability, etc.
    result: str  # hit, miss, critical, blocked, dodged, parried
    damage: Optional[int] = None
    special_effects: Optional[str] = None

class CombatSystem:
    def __init__(self):
        self.llm = get_llm_generator()

    async def describe_action(self, action: CombatAction) -> str:
        """Generate description for a combat action."""
        description = await self.llm.generate_combat_description(
            attacker=action.attacker_name,
            defender=action.defender_name,
            action=action.action_type,
            result=action.result,
            damage=action.damage,
            special_effects=action.special_effects
        )

        return description

    async def process_attack(
        self,
        attacker,
        defender,
        attack_type: str
    ) -> tuple[str, int]:
        """Process attack and generate description."""
        # Calculate combat result
        result, damage, effects = self.calculate_attack(
            attacker, defender, attack_type
        )

        # Generate description
        description = await self.describe_action(
            CombatAction(
                attacker_name=attacker.name,
                defender_name=defender.name,
                action_type=attack_type,
                result=result,
                damage=damage,
                special_effects=effects
            )
        )

        # Apply damage
        if damage > 0:
            defender.take_damage(damage)

        return description, damage
```

### Ability Usage Descriptions

```python
async def use_ability(self, user, target, ability) -> str:
    """Use ability and generate description."""
    # Determine effect
    result = self.calculate_ability_effect(user, target, ability)

    # Build special effects description
    effects = [ability.visual_effect]
    if ability.status_effect:
        effects.append(f"inflicts {ability.status_effect}")

    # Generate description
    description = await self.llm.generate_combat_description(
        attacker=user.name,
        defender=target.name,
        action=f"uses {ability.name}",
        result="hit" if result.success else "miss",
        damage=result.damage,
        special_effects=", ".join(effects)
    )

    return description
```

### Combat Sequence

```python
async def run_combat_turn(self, combatant, target, action) -> list[str]:
    """Run a full combat turn with descriptions."""
    descriptions = []

    # Main action
    main_desc = await self.process_attack(combatant, target, action)
    descriptions.append(main_desc)

    # Counter-attack if applicable
    if self.can_counter(target):
        counter_desc = await self.process_attack(
            target, combatant, "counter-attack"
        )
        descriptions.append(counter_desc)

    # Death check
    if target.is_dead():
        death_event = await self.llm.generate_event_narrative(
            event_type="enemy_defeated" if target.is_enemy else "player_death",
            context={
                "location": combatant.location,
                "participants": [combatant.name, target.name],
                "details": {"final_blow": action}
            }
        )
        descriptions.append(death_event)

    return descriptions
```

---

## Event System Integration

### Major Event Handling

```python
# In world/events.py or similar

from llm import get_llm_generator

class EventManager:
    def __init__(self):
        self.llm = get_llm_generator()

    async def broadcast_shard_collected(
        self,
        player_name: str,
        shard_name: str,
        location: str,
        total_shards: int,
        threshold: int
    ):
        """Broadcast shard collection to all players."""
        narrative = await self.llm.generate_event_narrative(
            event_type="shard_collected",
            context={
                "location": location,
                "participants": [player_name],
                "details": {
                    "shard_name": shard_name,
                    "total_collected": total_shards,
                    "threshold": threshold,
                    "remaining": threshold - total_shards
                },
                "context": f"{player_name} claims {shard_name}"
            }
        )

        # Broadcast to all online players
        await self.broadcast_to_all(narrative)

    async def trigger_aetherfall(self, trigger_player: str):
        """Trigger the Aetherfall world reset event."""
        narrative = await self.llm.generate_event_narrative(
            event_type="aetherfall",
            context={
                "location": "The Entire World",
                "participants": [trigger_player, "all players"],
                "details": {
                    "trigger": trigger_player,
                    "affected_areas": "all locations"
                },
                "context": "The threshold has been reached. Reality reshapes itself."
            }
        )

        # Major broadcast
        await self.broadcast_to_all("\n" + "="*60)
        await self.broadcast_to_all(narrative)
        await self.broadcast_to_all("="*60 + "\n")

        # Execute world reset
        await self.execute_world_reset()
```

### Boss Defeat Events

```python
async def handle_boss_defeat(
    self,
    boss_name: str,
    players: list[str],
    location: str
):
    """Generate narrative for boss defeat."""
    narrative = await self.llm.generate_event_narrative(
        event_type="boss_defeated",
        context={
            "location": location,
            "participants": players,
            "details": {
                "boss_name": boss_name,
                "party_size": len(players)
            },
            "context": f"The legendary {boss_name} has fallen"
        }
    )

    # Send to participants
    for player in players:
        await player.send_message(f"\n{narrative}\n")

    # World announcement
    announcement = f"{boss_name} has been defeated by {', '.join(players)}!"
    await self.broadcast_to_all(announcement)
```

---

## TUI/Display Integration

### Main Game Screen

```python
# In tui/world_screen.py or similar

from textual.app import ComposeResult
from textual.widgets import Static, RichLog
from llm import get_llm_generator

class WorldScreen:
    def __init__(self):
        self.llm = get_llm_generator()
        self.message_log = RichLog()

    async def display_location(self, location):
        """Display location with LLM-generated description."""
        # Generate description
        description = await self.llm.generate_location_description(
            location.name,
            location.reality_type,
            context={
                "features": location.features,
                "corruption_level": location.corruption_level
            }
        )

        # Display in TUI
        self.message_log.write(f"\n[bold cyan]=== {location.name} ===[/bold cyan]")
        self.message_log.write(f"[italic]{description}[/italic]")
        self.message_log.write("")

    async def display_npc_dialogue(self, npc_name: str, dialogue: str):
        """Display NPC dialogue in TUI."""
        self.message_log.write(
            f"\n[bold yellow]{npc_name}:[/bold yellow] [italic]{dialogue}[/italic]\n"
        )

    async def display_combat_action(self, description: str):
        """Display combat action in TUI."""
        self.message_log.write(f"[bold red]{description}[/bold red]")
```

### Batch Loading Locations

```python
async def preload_location_descriptions(self, locations: list):
    """Preload descriptions for multiple locations."""
    # Build batch requests
    requests = [
        {
            "type": "location",
            "location_name": loc.name,
            "reality_type": loc.reality_type,
            "context": {"features": loc.features}
        }
        for loc in locations
    ]

    # Generate in parallel
    descriptions = await self.llm.generate_multiple_descriptions(requests)

    # Cache results
    self.location_cache = dict(zip(
        [loc.name for loc in locations],
        descriptions
    ))
```

---

## Best Practices

### 1. Error Handling

```python
async def safe_generate(self, *args, **kwargs):
    """Safely generate with error handling."""
    try:
        result = await self.llm.generate_location_description(*args, **kwargs)
        return result
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        # Return generic fallback
        return "The world continues, silent and mysterious."
```

### 2. Caching Strategy

```python
class CachedWorldManager:
    def __init__(self):
        self.llm = get_llm_generator()
        self.description_cache = {}

    async def get_location_description(self, location_id: str, reality_type: str):
        """Get location description with caching."""
        cache_key = f"{location_id}:{reality_type}"

        if cache_key in self.description_cache:
            return self.description_cache[cache_key]

        # Generate and cache
        description = await self.llm.generate_location_description(
            location_id,
            reality_type,
            use_cache=True  # Also use LLM's internal cache
        )

        self.description_cache[cache_key] = description
        return description
```

### 3. Performance Optimization

```python
async def optimize_batch_generation(self, items: list):
    """Optimize by batching related requests."""
    # Separate items by type
    locations = [i for i in items if i.type == "location"]
    npcs = [i for i in items if i.type == "npc"]

    # Build batch request
    requests = []
    for loc in locations:
        requests.append({
            "type": "location",
            "location_name": loc.name,
            "reality_type": loc.reality_type
        })

    # Generate all at once
    results = await self.llm.generate_multiple_descriptions(requests)
    return results
```

### 4. Context Building

```python
def build_rich_context(self, location, player) -> dict:
    """Build rich context for better generation."""
    return {
        "description": location.base_description,
        "features": location.features,
        "inhabitants": [npc.name for npc in location.npcs],
        "corruption_level": location.corruption_level,
        "player_progress": player.get_progress_in_location(location),
        "time_of_day": self.world.time_of_day,
        "weather": location.current_weather,
        "recent_events": self.get_recent_events(location)
    }
```

---

## Complete Example: Player Action Flow

```python
async def handle_player_examine(self, player, target: str):
    """Complete flow for player examining something."""

    if target in self.locations:
        # Examining a location
        location = self.locations[target]
        description = await self.llm.generate_location_description(
            location.name,
            location.reality_type,
            context=self.build_rich_context(location, player)
        )
        await player.send_message(description)

    elif target in self.npcs:
        # Examining an NPC triggers dialogue
        npc = self.npcs[target]
        dialogue = await self.llm.generate_npc_dialogue(
            npc.name,
            context=f"Player examines {npc.name}",
            player_action="examines closely",
            npc_background=npc.background
        )
        await player.send_message(f"{npc.name}: {dialogue}")

    else:
        await player.send_message("You see nothing special.")
```

This comprehensive integration guide should help you seamlessly incorporate the LLM module into all major game systems!
