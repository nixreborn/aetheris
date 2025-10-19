# LLM Module Quick Start Guide

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your `.env` file:
```env
# Basic configuration
LLM_ENABLED=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-your-key-here

# Optional: Adjust generation parameters
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.8
```

## Quick Usage Examples

### Async Usage (Recommended)

```python
from llm import get_llm_generator
import asyncio

async def main():
    generator = get_llm_generator()

    # Generate location description
    description = await generator.generate_location_description(
        location_name="The Shattered Cathedral",
        reality_type="corrupted"
    )
    print(description)

asyncio.run(main())
```

### Synchronous Usage

```python
from llm import generate_location_description_sync

# Use in non-async code
description = generate_location_description_sync(
    "The Shattered Cathedral",
    "corrupted"
)
print(description)
```

### All Generation Methods

```python
from llm import get_llm_generator
import asyncio

async def examples():
    generator = get_llm_generator()

    # 1. Location Description
    location = await generator.generate_location_description(
        location_name="The Eternal Flame",
        reality_type="stable",
        context={"features": ["sacred fire", "ancient shrine"]}
    )

    # 2. NPC Dialogue
    dialogue = await generator.generate_npc_dialogue(
        npc_name="The Blind Seer",
        context="Player seeks knowledge",
        player_action="asks about the Shards",
        npc_background="Ancient oracle who witnessed the first Aetherfall"
    )

    # 3. Combat Description
    combat = await generator.generate_combat_description(
        attacker="Corrupted Knight",
        defender="Player",
        action="overhead slash",
        result="critical",
        damage=45,
        special_effects="void energy trails"
    )

    # 4. Event Narrative
    event = await generator.generate_event_narrative(
        event_type="shard_collected",
        context={
            "location": "The Abyssal Depths",
            "participants": ["Valeria"],
            "details": {"shard_type": "Shard of Time"}
        }
    )

asyncio.run(examples())
```

## Provider Configuration

### OpenAI (Default)
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview  # or gpt-4, gpt-3.5-turbo
OPENAI_API_KEY=sk-...
```

### Anthropic
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-...
```

### Local Models
```env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=mistral-7b-instruct
```

## Fallback Mode

If LLM is disabled or fails, the module automatically uses fallback text:

```python
from llm import get_llm_generator

async def safe_generation():
    generator = get_llm_generator()

    # Even if API fails, you get atmospheric fallback text
    description = await generator.generate_location_description(
        "Unknown Location",
        "corrupted"
    )
    # Returns: "The air itself writhes with wrongness. Reality has abandoned this place."
```

## Testing

Test your setup:

```bash
# Test prompts module (no API required)
python llm/test_prompts.py

# Test with your API configuration
python llm/example_usage.py
```

## Reality Types

The module supports three reality types with different tones:

- **`stable`**: Melancholic but recognizable, familiar forms
- **`fractured`**: Unsettling distortions, contradictions
- **`corrupted`**: Nightmarish, wrong, reality breaking down

## Combat Results

Supported combat result types:

- `hit` - Normal successful attack
- `miss` - Attack fails to connect
- `critical` - Devastating critical hit
- `blocked` - Defender blocks the attack
- `dodged` - Defender evades the attack
- `parried` - Defender parries and deflects

## Event Types

Common event types:

- `shard_collected` - Player collects a Shard of Eternity
- `aetherfall` - Reality reset/world transformation
- `boss_defeated` - Major enemy defeated
- `player_death` - Player character dies
- `reality_shift` - Reality type changes
- `faction_event` - Faction-related occurrence

## Tips

1. **Cache Management**: Location and event descriptions are cached by default
2. **Batch Generation**: Use `generate_multiple_descriptions()` for parallel requests
3. **Error Handling**: Module handles errors gracefully with fallbacks
4. **Cost Control**: Monitor with `generator.get_stats()["request_count"]`
5. **Testing**: Test connection with `await generator.test_connection()`

## Common Patterns

### Game Loop Integration

```python
from llm import get_llm_generator

class GameWorld:
    def __init__(self):
        self.llm = get_llm_generator()

    async def enter_location(self, location_name, reality_type):
        description = await self.llm.generate_location_description(
            location_name,
            reality_type
        )
        self.display_text(description)

    async def npc_interact(self, npc, player_action):
        dialogue = await self.llm.generate_npc_dialogue(
            npc.name,
            self.get_context(),
            player_action,
            npc.background
        )
        self.display_dialogue(npc.name, dialogue)
```

### Combat Integration

```python
async def process_attack(attacker, defender, action):
    result, damage = calculate_combat(attacker, defender, action)

    description = await generator.generate_combat_description(
        attacker=attacker.name,
        defender=defender.name,
        action=action.name,
        result=result,
        damage=damage
    )

    display_combat_text(description)
```

### Event Broadcasting

```python
async def broadcast_event(event_type, context):
    narrative = await generator.generate_event_narrative(
        event_type,
        context
    )

    # Send to all players
    for player in active_players:
        player.send_message(narrative)
```

## Troubleshooting

**LLM not generating text?**
- Check `.env` configuration
- Verify API key is valid
- Test with: `await generator.test_connection()`
- Check logs for errors

**Getting fallback text only?**
- Ensure `LLM_ENABLED=true`
- Verify provider and API key
- Check network connectivity

**High API costs?**
- Enable caching: `use_cache=True`
- Use cheaper models (gpt-3.5-turbo)
- Consider local models
- Monitor: `generator.get_stats()`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [example_usage.py](example_usage.py) for more examples
- Explore [prompts.py](prompts.py) to customize tone and style
- Run tests with `python test_prompts.py`
