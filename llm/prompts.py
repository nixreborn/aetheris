"""
Prompt templates and context formatting for LLM text generation.
Contains system prompts, templates, and formatting functions for the dark fantasy Souls-like tone.
"""
from typing import Dict, Any, Optional
from enum import Enum


class PromptType(Enum):
    """Types of prompts for different scenarios."""
    LOCATION_DESCRIPTION = "location_description"
    NPC_DIALOGUE = "npc_dialogue"
    COMBAT_DESCRIPTION = "combat_description"
    EVENT_NARRATIVE = "event_narrative"


# ===========================
# System Prompts
# ===========================

SYSTEM_PROMPT_BASE = """You are a narrative generator for "Shards of Eternity", a dark fantasy multiplayer game inspired by Dark Souls and cosmic horror.

WORLD SETTING:
- The world is caught in the Aetherfall cycle, constantly shifting between realities
- Corruption spreads as reality fragments collapse
- Ancient powers and eldritch entities lurk in the darkness
- Humanity clings to survival in a dying world
- The Shards of Eternity are powerful artifacts that can reshape reality itself

TONE & STYLE:
- Dark, melancholic, and oppressive atmosphere
- Cryptic and mysterious, leaving things unsaid
- Poetic but concise - avoid excessive verbosity
- Evoke dread, wonder, and despair in equal measure
- Use vivid, sensory descriptions
- Minimal exposition - show, don't tell
- Echoes of FromSoftware's environmental storytelling

WRITING GUIDELINES:
- Keep responses under 3-4 sentences unless complexity demands more
- Use evocative, atmospheric language
- Avoid modern colloquialisms
- Favor archaic or formal speech patterns for NPCs
- Leave room for player interpretation
- Every description should hint at deeper lore"""


SYSTEM_PROMPT_LOCATION = SYSTEM_PROMPT_BASE + """

LOCATION DESCRIPTIONS:
- Capture the mood and atmosphere first
- Include sensory details (sight, sound, smell)
- Hint at history through environmental details
- Suggest danger or mystery without being explicit
- Adapt tone based on reality type:
  * Stable: Melancholic but recognizable
  * Fractured: Unsettling distortions and contradictions
  * Corrupted: Nightmarish and wrong, reality breaking down"""


SYSTEM_PROMPT_NPC = SYSTEM_PROMPT_BASE + """

NPC DIALOGUE:
- Each NPC should have a distinct voice and perspective
- Cryptic responses that reveal character and lore
- Often speak in riddles, metaphors, or fragments
- May be hostile, melancholic, mad, or enigmatic
- Dialogue should reflect their experiences and nature
- Avoid direct answers - hint and suggest
- Use archaic or formal language patterns
- Some NPCs may be corrupted and speak strangely"""


SYSTEM_PROMPT_COMBAT = SYSTEM_PROMPT_BASE + """

COMBAT DESCRIPTIONS:
- Visceral and impactful descriptions
- Quick, punchy sentences for fast pacing
- Emphasize the weight and brutality of combat
- Describe visual effects and physical impact
- Include environmental interactions when relevant
- Success should feel earned, failure should feel brutal
- Use active, powerful verbs
- Keep it concise - combat is fast"""


SYSTEM_PROMPT_EVENT = SYSTEM_PROMPT_BASE + """

EVENT NARRATIVES:
- Set the scene with atmospheric detail
- Build tension and significance
- Suggest consequences without stating them outright
- Use metaphor and symbolism
- Connect events to larger world lore
- Leave room for player agency and interpretation
- Balance epic scope with intimate detail"""


# ===========================
# Prompt Templates
# ===========================

LOCATION_DESCRIPTION_TEMPLATE = """Generate a location description for:

LOCATION: {location_name}
REALITY TYPE: {reality_type}
ADDITIONAL CONTEXT: {context}

Create an atmospheric description that captures the essence of this place and its current state of reality. Include sensory details and environmental storytelling."""


NPC_DIALOGUE_TEMPLATE = """Generate NPC dialogue for:

NPC: {npc_name}
NPC BACKGROUND: {npc_background}
CONTEXT: {context}
PLAYER ACTION: {player_action}

Create a response that fits the NPC's character and the situation. The dialogue should be cryptic, atmospheric, and true to the dark fantasy tone."""


COMBAT_DESCRIPTION_TEMPLATE = """Generate a combat description for:

ATTACKER: {attacker}
DEFENDER: {defender}
ACTION: {action}
RESULT: {result}
DAMAGE: {damage}
SPECIAL EFFECTS: {special_effects}

Create a visceral, impactful description of this combat action. Keep it concise but evocative."""


EVENT_NARRATIVE_TEMPLATE = """Generate an event narrative for:

EVENT TYPE: {event_type}
LOCATION: {location}
PARTICIPANTS: {participants}
KEY DETAILS: {details}
CONTEXT: {context}

Create an atmospheric narrative that captures the significance and mood of this event."""


# ===========================
# Context Formatting Functions
# ===========================

def format_location_prompt(
    location_name: str,
    reality_type: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Format a location description prompt.

    Args:
        location_name: Name of the location
        reality_type: Type of reality (stable, fractured, corrupted)
        context: Additional context information

    Returns:
        Dictionary with system and user prompts
    """
    context_str = ""
    if context:
        context_items = []
        if "description" in context:
            context_items.append(f"Base description: {context['description']}")
        if "features" in context:
            context_items.append(f"Notable features: {', '.join(context['features'])}")
        if "inhabitants" in context:
            context_items.append(f"Inhabitants: {', '.join(context['inhabitants'])}")
        if "corruption_level" in context:
            context_items.append(f"Corruption level: {context['corruption_level']}")
        context_str = "\n".join(context_items) if context_items else "None"
    else:
        context_str = "None"

    return {
        "system": SYSTEM_PROMPT_LOCATION,
        "user": LOCATION_DESCRIPTION_TEMPLATE.format(
            location_name=location_name,
            reality_type=reality_type,
            context=context_str
        )
    }


def format_npc_dialogue_prompt(
    npc_name: str,
    context: str,
    player_action: str,
    npc_background: Optional[str] = None
) -> Dict[str, str]:
    """
    Format an NPC dialogue prompt.

    Args:
        npc_name: Name of the NPC
        context: Current situation/context
        player_action: What the player just did or said
        npc_background: Optional background info about the NPC

    Returns:
        Dictionary with system and user prompts
    """
    if not npc_background:
        npc_background = "A mysterious figure encountered in the world"

    return {
        "system": SYSTEM_PROMPT_NPC,
        "user": NPC_DIALOGUE_TEMPLATE.format(
            npc_name=npc_name,
            npc_background=npc_background,
            context=context,
            player_action=player_action
        )
    }


def format_combat_prompt(
    attacker: str,
    defender: str,
    action: str,
    result: str,
    damage: Optional[int] = None,
    special_effects: Optional[str] = None
) -> Dict[str, str]:
    """
    Format a combat description prompt.

    Args:
        attacker: Name/description of attacker
        defender: Name/description of defender
        action: The action being performed
        result: Outcome (hit, miss, critical, blocked, etc.)
        damage: Optional damage amount
        special_effects: Optional special effects or conditions

    Returns:
        Dictionary with system and user prompts
    """
    damage_str = f"{damage} damage" if damage is not None else "Unknown damage"
    effects_str = special_effects if special_effects else "None"

    return {
        "system": SYSTEM_PROMPT_COMBAT,
        "user": COMBAT_DESCRIPTION_TEMPLATE.format(
            attacker=attacker,
            defender=defender,
            action=action,
            result=result,
            damage=damage_str,
            special_effects=effects_str
        )
    }


def format_event_prompt(
    event_type: str,
    context: Dict[str, Any]
) -> Dict[str, str]:
    """
    Format an event narrative prompt.

    Args:
        event_type: Type of event (shard_collected, aetherfall, boss_defeated, etc.)
        context: Dictionary with event details

    Returns:
        Dictionary with system and user prompts
    """
    location = context.get("location", "Unknown location")
    participants = context.get("participants", ["Unknown"])
    details = context.get("details", {})
    additional_context = context.get("context", "")

    # Format participants list
    if isinstance(participants, list):
        participants_str = ", ".join(participants)
    else:
        participants_str = str(participants)

    # Format details
    details_items = []
    for key, value in details.items():
        details_items.append(f"{key}: {value}")
    details_str = "\n".join(details_items) if details_items else "None"

    return {
        "system": SYSTEM_PROMPT_EVENT,
        "user": EVENT_NARRATIVE_TEMPLATE.format(
            event_type=event_type,
            location=location,
            participants=participants_str,
            details=details_str,
            context=additional_context
        )
    }


# ===========================
# Fallback Text
# ===========================

FALLBACK_LOCATION_DESCRIPTIONS = {
    "default": "A place of shadow and mystery, shrouded in the dying light.",
    "stable": "The world holds together here, if barely. Reality clings to familiar forms.",
    "fractured": "Space warps and bends. What was solid becomes uncertain.",
    "corrupted": "The air itself writhes with wrongness. Reality has abandoned this place."
}


FALLBACK_NPC_DIALOGUES = [
    "...",
    "The words escape me, traveler.",
    "Silence falls heavy here.",
    "I have nothing to offer you.",
    "Another lost soul, wandering.",
    "Speak your piece and be gone.",
]


FALLBACK_COMBAT_DESCRIPTIONS = {
    "hit": "The blow lands with brutal force.",
    "miss": "The strike cuts only air.",
    "critical": "A devastating strike tears through defenses.",
    "blocked": "Steel meets steel with a harsh clang.",
    "dodged": "They slip away like smoke.",
    "parried": "The attack is turned aside with practiced skill."
}


FALLBACK_EVENT_NARRATIVES = {
    "shard_collected": "Another fragment of eternity claimed. The cycle continues.",
    "aetherfall": "Reality shudders. The world remakes itself once more.",
    "boss_defeated": "The great beast falls. Silence reclaims the battlefield.",
    "player_death": "Darkness claims another soul.",
    "reality_shift": "The world twists. Nothing is as it was.",
    "default": "Something significant has occurred in the world."
}


def get_fallback_text(prompt_type: PromptType, key: Optional[str] = None) -> str:
    """
    Get fallback text when LLM is unavailable.

    Args:
        prompt_type: Type of prompt/content needed
        key: Optional specific key for lookups

    Returns:
        Fallback text string
    """
    if prompt_type == PromptType.LOCATION_DESCRIPTION:
        return FALLBACK_LOCATION_DESCRIPTIONS.get(
            key or "default",
            FALLBACK_LOCATION_DESCRIPTIONS["default"]
        )
    elif prompt_type == PromptType.NPC_DIALOGUE:
        import random
        return random.choice(FALLBACK_NPC_DIALOGUES)
    elif prompt_type == PromptType.COMBAT_DESCRIPTION:
        return FALLBACK_COMBAT_DESCRIPTIONS.get(
            key or "hit",
            FALLBACK_COMBAT_DESCRIPTIONS["hit"]
        )
    elif prompt_type == PromptType.EVENT_NARRATIVE:
        return FALLBACK_EVENT_NARRATIVES.get(
            key or "default",
            FALLBACK_EVENT_NARRATIVES["default"]
        )
    else:
        return "The world continues, silent and mysterious."
