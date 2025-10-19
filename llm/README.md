# LLM Integration Module

Comprehensive LLM integration for dynamic text generation in Shards of Eternity. Supports multiple providers with graceful fallbacks and async/await patterns.

## Features

- **Multi-Provider Support**: OpenAI, Anthropic, and local LLM models
- **Async/Await**: Non-blocking API calls for smooth gameplay
- **Graceful Fallbacks**: Pre-written fallback text when LLM is unavailable
- **Caching**: Intelligent caching to reduce API costs
- **Dark Fantasy Tone**: Souls-like prompts and system instructions
- **Error Handling**: Robust error management with detailed logging
- **Batch Generation**: Parallel generation for multiple requests

## Files

- **generator.py**: Main `LLMGenerator` class with provider management and generation methods
- **prompts.py**: Prompt templates, system prompts, and fallback text
- **providers.py**: (Reserved for future provider-specific implementations)
- **example_usage.py**: Example code demonstrating all features

## Installation

### Required Packages

```bash
# For OpenAI (and local models with OpenAI-compatible APIs)
pip install openai

# For Anthropic
pip install anthropic
```

### Configuration

Add to your `.env` file:

```env
# Enable/disable LLM
LLM_ENABLED=true

# Provider: openai, anthropic, or local
LLM_PROVIDER=openai

# Model name
LLM_MODEL=gpt-4-turbo-preview

# API Keys
LLM_API_KEY=your-api-key-here
# Or use provider-specific keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# For local models
LLM_BASE_URL=http://localhost:8000/v1

# Generation parameters
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.8
```

## Usage

### Async API (Recommended)

```python
from llm import get_llm_generator

async def generate_content():
    generator = get_llm_generator()

    # Location description
    desc = await generator.generate_location_description(
        location_name="The Shattered Cathedral",
        reality_type="corrupted",
        context={
            "features": ["cracked spires", "void rifts"],
            "corruption_level": "high"
        }
    )

    # NPC dialogue
    dialogue = await generator.generate_npc_dialogue(
        npc_name="The Blind Seer",
        context="Player seeks knowledge",
        player_action="asks about the Shards",
        npc_background="Ancient oracle"
    )

    # Combat description
    combat = await generator.generate_combat_description(
        attacker="Corrupted Knight",
        defender="Player",
        action="overhead slash",
        result="critical",
        damage=45
    )

    # Event narrative
    narrative = await generator.generate_event_narrative(
        event_type="shard_collected",
        context={
            "location": "The Abyssal Depths",
            "participants": ["Player"],
            "details": {"shard_type": "Shard of Time"}
        }
    )
```

### Synchronous API

```python
from llm import (
    generate_location_description_sync,
    generate_npc_dialogue_sync,
    generate_combat_description_sync,
    generate_event_narrative_sync
)

# Use these in non-async contexts
desc = generate_location_description_sync(
    "The Shattered Cathedral",
    "corrupted"
)
```

### Batch Generation

```python
async def batch_generate():
    generator = get_llm_generator()

    requests = [
        {
            "type": "location",
            "location_name": "The Eternal Flame",
            "reality_type": "stable"
        },
        {
            "type": "combat",
            "attacker": "Player",
            "defender": "Shadow Beast",
            "action": "parry",
            "result": "hit"
        }
    ]

    results = await generator.generate_multiple_descriptions(requests)
```

## API Reference

### LLMGenerator Class

#### Methods

**`async generate_location_description(location_name, reality_type, context=None, use_cache=True)`**
- Generate atmospheric location descriptions
- `reality_type`: "stable", "fractured", or "corrupted"
- `context`: Optional dict with features, inhabitants, corruption_level, etc.
- Returns: Description string (generated or fallback)

**`async generate_npc_dialogue(npc_name, context, player_action, npc_background=None, use_cache=False)`**
- Generate cryptic, atmospheric NPC dialogue
- `context`: Current situation
- `player_action`: What the player did/said
- `npc_background`: Optional NPC backstory
- Returns: Dialogue string (generated or fallback)

**`async generate_combat_description(attacker, defender, action, result, damage=None, special_effects=None, use_cache=False)`**
- Generate visceral combat descriptions
- `result`: "hit", "miss", "critical", "blocked", "dodged", "parried"
- `damage`: Optional damage amount
- `special_effects`: Optional effect description
- Returns: Combat description (generated or fallback)

**`async generate_event_narrative(event_type, context, use_cache=True)`**
- Generate narratives for significant events
- `event_type`: "shard_collected", "aetherfall", "boss_defeated", etc.
- `context`: Dict with location, participants, details, context
- Returns: Narrative string (generated or fallback)

**`async generate_multiple_descriptions(requests)`**
- Batch generate multiple descriptions in parallel
- `requests`: List of request dicts with 'type' and parameters
- Returns: List of results in same order

**`async test_connection()`**
- Test connection to LLM provider
- Returns: True if successful, False otherwise

**`get_stats()`**
- Get usage statistics
- Returns: Dict with enabled, provider, model, request_count, cache_size

**`set_enabled(enabled)`**
- Enable or disable LLM generation

**`clear_cache()`**
- Clear the generation cache

## Prompt System

### Reality Types

The system adapts tone based on reality type:

- **Stable**: Melancholic but recognizable, familiar forms
- **Fractured**: Unsettling distortions, contradictions, unstable
- **Corrupted**: Nightmarish, wrong, reality breaking down

### Tone Guidelines

All generated text follows these principles:

- Dark, melancholic, oppressive atmosphere
- Cryptic and mysterious
- Poetic but concise (3-4 sentences typically)
- Evokes dread, wonder, and despair
- Vivid sensory descriptions
- Show, don't tell
- FromSoftware-style environmental storytelling

### Fallback Text

When LLM is disabled or fails, the module provides curated fallback text:

- Location descriptions for each reality type
- Generic but atmospheric NPC dialogues
- Combat descriptions for each result type
- Event narratives for major event types

## Provider Setup

### OpenAI

```python
# .env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-...
```

Supported models:
- `gpt-4-turbo-preview`
- `gpt-4`
- `gpt-3.5-turbo`

### Anthropic

```python
# .env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-...
```

Supported models:
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

### Local Models

For local LLMs with OpenAI-compatible APIs (e.g., LM Studio, Ollama, vLLM):

```python
# .env
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=mistral-7b-instruct
```

## Performance

### Caching

- Location descriptions are cached by default
- Event narratives are cached by event type
- NPC dialogue and combat are not cached (for variety)
- Cache uses FIFO eviction with max size of 100 entries

### Batch Processing

Use `generate_multiple_descriptions()` for parallel generation:
- Reduces latency for multiple requests
- Handles errors per-request with fallbacks
- Maintains request order in results

### Rate Limiting

The module tracks request count but doesn't enforce limits. For production:
- Monitor `generator.get_stats()["request_count"]`
- Implement rate limiting at the application level
- Consider caching more aggressively

## Error Handling

The module handles errors gracefully:

1. **Provider Initialization Errors**: Logged with clear error messages
2. **API Call Failures**: Returns `None`, then uses fallback text
3. **Missing Dependencies**: Clear error messages about required packages
4. **Invalid Configurations**: Validates settings and provides warnings

All errors are logged using Python's `logging` module.

## Testing

Run the example:

```bash
python -m llm.example_usage
```

This demonstrates:
- Connection testing
- All generation methods
- Batch processing
- Statistics tracking

## Best Practices

1. **Use Async When Possible**: Avoid blocking the game loop
2. **Enable Caching**: For location descriptions and events
3. **Handle Fallbacks**: Always have good fallback text
4. **Monitor Costs**: Track request counts with `get_stats()`
5. **Test Connection**: Use `test_connection()` at startup
6. **Batch Requests**: Use batch generation for multiple items
7. **Configure Temperature**: Lower (0.6-0.7) for consistency, higher (0.8-0.9) for variety

## Troubleshooting

### LLM Not Working

1. Check `.env` configuration
2. Verify API key is valid
3. Test connection: `await generator.test_connection()`
4. Check logs for error messages
5. Ensure required packages are installed

### Poor Quality Output

1. Adjust `LLM_TEMPERATURE` (0.6-0.9 recommended)
2. Try different models
3. Check prompt templates in `prompts.py`
4. Verify `LLM_MAX_TOKENS` is sufficient (300-500 recommended)

### High Costs

1. Enable caching for more content types
2. Reduce `LLM_MAX_TOKENS`
3. Use cheaper models (e.g., GPT-3.5-turbo)
4. Consider local models
5. Monitor with `get_stats()`

## Future Enhancements

Potential improvements:

- [ ] Fine-tuned models for better tone matching
- [ ] Streaming responses for real-time generation
- [ ] More sophisticated caching with TTL
- [ ] Rate limiting built into the module
- [ ] Prompt versioning and A/B testing
- [ ] User-customizable tone settings
- [ ] Multi-language support
- [ ] Context memory for longer dialogues

## License

Part of Shards of Eternity game project.
