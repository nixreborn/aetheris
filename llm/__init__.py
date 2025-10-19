"""
LLM integration module for Shards of Eternity.
Provides dynamic text generation for locations, NPCs, combat, and events.
"""
from llm.generator import (
    LLMGenerator,
    get_llm_generator,
    generate_location_description_sync,
    generate_npc_dialogue_sync,
    generate_combat_description_sync,
    generate_event_narrative_sync,
)
from llm.prompts import (
    PromptType,
    get_fallback_text,
    format_location_prompt,
    format_npc_dialogue_prompt,
    format_combat_prompt,
    format_event_prompt,
)

__all__ = [
    # Generator
    "LLMGenerator",
    "get_llm_generator",
    # Sync wrappers
    "generate_location_description_sync",
    "generate_npc_dialogue_sync",
    "generate_combat_description_sync",
    "generate_event_narrative_sync",
    # Prompts
    "PromptType",
    "get_fallback_text",
    "format_location_prompt",
    "format_npc_dialogue_prompt",
    "format_combat_prompt",
    "format_event_prompt",
]
