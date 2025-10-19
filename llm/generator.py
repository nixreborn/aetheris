"""
LLM Generator module for dynamic text generation.
Supports multiple providers (OpenAI, Anthropic, local models) with graceful fallbacks.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

from config.settings import get_settings
from llm.prompts import (
    format_location_prompt,
    format_npc_dialogue_prompt,
    format_combat_prompt,
    format_event_prompt,
    get_fallback_text,
    PromptType
)


logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class LLMGenerator:
    """
    Main LLM text generation class.
    Handles multiple providers, graceful degradation, and fallback text.
    """

    def __init__(self):
        """Initialize the LLM generator with settings."""
        self.settings = get_settings()
        self.enabled = self.settings.llm_enabled
        self.provider = LLMProvider(self.settings.llm_provider)
        self.model = self.settings.llm_model
        self.api_key = self.settings.active_llm_api_key
        self.base_url = self.settings.llm_base_url
        self.max_tokens = self.settings.llm_max_tokens
        self.temperature = self.settings.llm_temperature

        # Provider clients (initialized lazily)
        self._openai_client = None
        self._anthropic_client = None
        self._local_client = None

        # Rate limiting and caching
        self._request_count = 0
        self._cache: Dict[str, str] = {}
        self._cache_max_size = 100

        logger.info(
            f"LLMGenerator initialized: enabled={self.enabled}, "
            f"provider={self.provider.value}, model={self.model}"
        )

    # ===========================
    # Provider Client Management
    # ===========================

    def _get_openai_client(self):
        """Get or create OpenAI client."""
        if self._openai_client is None:
            try:
                import openai
                self._openai_client = openai.AsyncOpenAI(
                    api_key=self.api_key
                )
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.error("OpenAI package not installed. Install with: pip install openai")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise
        return self._openai_client

    def _get_anthropic_client(self):
        """Get or create Anthropic client."""
        if self._anthropic_client is None:
            try:
                import anthropic
                self._anthropic_client = anthropic.AsyncAnthropic(
                    api_key=self.api_key
                )
                logger.info("Anthropic client initialized")
            except ImportError:
                logger.error("Anthropic package not installed. Install with: pip install anthropic")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                raise
        return self._anthropic_client

    def _get_local_client(self):
        """Get or create local LLM client."""
        if self._local_client is None:
            try:
                import openai  # Local models often use OpenAI-compatible API
                self._local_client = openai.AsyncOpenAI(
                    api_key=self.api_key or "not-needed",
                    base_url=self.base_url or "http://localhost:8000/v1"
                )
                logger.info(f"Local LLM client initialized: {self.base_url}")
            except ImportError:
                logger.error("OpenAI package required for local models. Install with: pip install openai")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize local LLM client: {e}")
                raise
        return self._local_client

    # ===========================
    # Core Generation Methods
    # ===========================

    async def _generate_with_openai(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:
        """
        Generate text using OpenAI API.

        Args:
            system_prompt: System prompt for context
            user_prompt: User prompt with specific request

        Returns:
            Generated text or None on failure
        """
        try:
            client = self._get_openai_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            self._request_count += 1
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return None

    async def _generate_with_anthropic(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:
        """
        Generate text using Anthropic API.

        Args:
            system_prompt: System prompt for context
            user_prompt: User prompt with specific request

        Returns:
            Generated text or None on failure
        """
        try:
            client = self._get_anthropic_client()
            message = await client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            self._request_count += 1
            return message.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            return None

    async def _generate_with_local(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:
        """
        Generate text using local LLM API.

        Args:
            system_prompt: System prompt for context
            user_prompt: User prompt with specific request

        Returns:
            Generated text or None on failure
        """
        try:
            client = self._get_local_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            self._request_count += 1
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            return None

    async def _generate(
        self,
        system_prompt: str,
        user_prompt: str,
        cache_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate text using the configured provider.

        Args:
            system_prompt: System prompt for context
            user_prompt: User prompt with specific request
            cache_key: Optional cache key to avoid duplicate requests

        Returns:
            Generated text or None on failure
        """
        if not self.enabled:
            logger.debug("LLM generation disabled in settings")
            return None

        # Check cache
        if cache_key and cache_key in self._cache:
            logger.debug(f"Cache hit for key: {cache_key}")
            return self._cache[cache_key]

        # Generate based on provider
        result = None
        try:
            if self.provider == LLMProvider.OPENAI:
                result = await self._generate_with_openai(system_prompt, user_prompt)
            elif self.provider == LLMProvider.ANTHROPIC:
                result = await self._generate_with_anthropic(system_prompt, user_prompt)
            elif self.provider == LLMProvider.LOCAL:
                result = await self._generate_with_local(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"Generation failed with provider {self.provider.value}: {e}")
            return None

        # Cache successful results
        if result and cache_key:
            self._add_to_cache(cache_key, result)

        return result

    def _add_to_cache(self, key: str, value: str):
        """Add item to cache with size management."""
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = value

    def _make_cache_key(self, *args) -> str:
        """Create a cache key from arguments."""
        return "|".join(str(arg) for arg in args)

    # ===========================
    # Public API Methods
    # ===========================

    async def generate_location_description(
        self,
        location_name: str,
        reality_type: str,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> str:
        """
        Generate a description for a location.

        Args:
            location_name: Name of the location
            reality_type: Type of reality (stable, fractured, corrupted)
            context: Optional additional context
            use_cache: Whether to use caching

        Returns:
            Generated or fallback description
        """
        prompts = format_location_prompt(location_name, reality_type, context)
        cache_key = self._make_cache_key(
            "location", location_name, reality_type
        ) if use_cache else None

        result = await self._generate(
            prompts["system"],
            prompts["user"],
            cache_key
        )

        if result:
            return result
        else:
            logger.debug(f"Using fallback for location: {location_name}")
            return get_fallback_text(PromptType.LOCATION_DESCRIPTION, reality_type)

    async def generate_npc_dialogue(
        self,
        npc_name: str,
        context: str,
        player_action: str,
        npc_background: Optional[str] = None,
        use_cache: bool = False  # Dialogue usually shouldn't be cached
    ) -> str:
        """
        Generate NPC dialogue.

        Args:
            npc_name: Name of the NPC
            context: Current situation/context
            player_action: What the player just did or said
            npc_background: Optional background info about the NPC
            use_cache: Whether to use caching (usually False for dialogue)

        Returns:
            Generated or fallback dialogue
        """
        prompts = format_npc_dialogue_prompt(
            npc_name, context, player_action, npc_background
        )
        cache_key = self._make_cache_key(
            "npc", npc_name, context, player_action
        ) if use_cache else None

        result = await self._generate(
            prompts["system"],
            prompts["user"],
            cache_key
        )

        if result:
            return result
        else:
            logger.debug(f"Using fallback for NPC dialogue: {npc_name}")
            return get_fallback_text(PromptType.NPC_DIALOGUE)

    async def generate_combat_description(
        self,
        attacker: str,
        defender: str,
        action: str,
        result: str,
        damage: Optional[int] = None,
        special_effects: Optional[str] = None,
        use_cache: bool = False
    ) -> str:
        """
        Generate a combat action description.

        Args:
            attacker: Name/description of attacker
            defender: Name/description of defender
            action: The action being performed
            result: Outcome (hit, miss, critical, blocked, etc.)
            damage: Optional damage amount
            special_effects: Optional special effects or conditions
            use_cache: Whether to use caching

        Returns:
            Generated or fallback combat description
        """
        prompts = format_combat_prompt(
            attacker, defender, action, result, damage, special_effects
        )

        # Combat descriptions could be cached by action type
        cache_key = self._make_cache_key(
            "combat", action, result
        ) if use_cache else None

        result_text = await self._generate(
            prompts["system"],
            prompts["user"],
            cache_key
        )

        if result_text:
            return result_text
        else:
            logger.debug(f"Using fallback for combat: {action} -> {result}")
            return get_fallback_text(PromptType.COMBAT_DESCRIPTION, result)

    async def generate_event_narrative(
        self,
        event_type: str,
        context: Dict[str, Any],
        use_cache: bool = True
    ) -> str:
        """
        Generate a narrative for a significant event.

        Args:
            event_type: Type of event (shard_collected, aetherfall, etc.)
            context: Dictionary with event details
            use_cache: Whether to use caching

        Returns:
            Generated or fallback event narrative
        """
        prompts = format_event_prompt(event_type, context)
        cache_key = self._make_cache_key(
            "event", event_type
        ) if use_cache else None

        result = await self._generate(
            prompts["system"],
            prompts["user"],
            cache_key
        )

        if result:
            return result
        else:
            logger.debug(f"Using fallback for event: {event_type}")
            return get_fallback_text(PromptType.EVENT_NARRATIVE, event_type)

    # ===========================
    # Batch Generation
    # ===========================

    async def generate_multiple_descriptions(
        self,
        requests: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate multiple descriptions in parallel.

        Args:
            requests: List of request dictionaries with 'type' and required params

        Returns:
            List of generated descriptions (in same order as requests)
        """
        tasks = []
        for req in requests:
            req_type = req.get("type")
            if req_type == "location":
                task = self.generate_location_description(
                    req["location_name"],
                    req["reality_type"],
                    req.get("context")
                )
            elif req_type == "npc":
                task = self.generate_npc_dialogue(
                    req["npc_name"],
                    req["context"],
                    req["player_action"],
                    req.get("npc_background")
                )
            elif req_type == "combat":
                task = self.generate_combat_description(
                    req["attacker"],
                    req["defender"],
                    req["action"],
                    req["result"],
                    req.get("damage"),
                    req.get("special_effects")
                )
            elif req_type == "event":
                task = self.generate_event_narrative(
                    req["event_type"],
                    req["context"]
                )
            else:
                logger.warning(f"Unknown request type: {req_type}")
                task = asyncio.create_task(asyncio.sleep(0))  # No-op task

            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to fallback text
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch request {i} failed: {result}")
                final_results.append(get_fallback_text(PromptType.LOCATION_DESCRIPTION))
            else:
                final_results.append(result)

        return final_results

    # ===========================
    # Utility Methods
    # ===========================

    def clear_cache(self):
        """Clear the generation cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about LLM usage.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "enabled": self.enabled,
            "provider": self.provider.value,
            "model": self.model,
            "request_count": self._request_count,
            "cache_size": len(self._cache),
            "cache_max_size": self._cache_max_size
        }

    def set_enabled(self, enabled: bool):
        """Enable or disable LLM generation."""
        self.enabled = enabled
        logger.info(f"LLM generation {'enabled' if enabled else 'disabled'}")

    async def test_connection(self) -> bool:
        """
        Test the connection to the LLM provider.

        Returns:
            True if connection successful, False otherwise
        """
        test_prompts = {
            "system": "You are a helpful assistant.",
            "user": "Say 'Hello' and nothing else."
        }

        try:
            result = await self._generate(
                test_prompts["system"],
                test_prompts["user"]
            )
            if result:
                logger.info(f"LLM connection test successful: {result[:50]}...")
                return True
            else:
                logger.warning("LLM connection test failed: no result returned")
                return False
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False


# ===========================
# Global Instance
# ===========================

_generator_instance: Optional[LLMGenerator] = None


def get_llm_generator() -> LLMGenerator:
    """
    Get or create the global LLM generator instance.

    Returns:
        The global LLMGenerator instance
    """
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = LLMGenerator()
    return _generator_instance


# ===========================
# Synchronous Wrapper Functions
# ===========================

def generate_location_description_sync(
    location_name: str,
    reality_type: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Synchronous wrapper for location description generation.
    Uses asyncio.run() to execute async function.
    """
    generator = get_llm_generator()
    return asyncio.run(
        generator.generate_location_description(location_name, reality_type, context)
    )


def generate_npc_dialogue_sync(
    npc_name: str,
    context: str,
    player_action: str,
    npc_background: Optional[str] = None
) -> str:
    """
    Synchronous wrapper for NPC dialogue generation.
    Uses asyncio.run() to execute async function.
    """
    generator = get_llm_generator()
    return asyncio.run(
        generator.generate_npc_dialogue(npc_name, context, player_action, npc_background)
    )


def generate_combat_description_sync(
    attacker: str,
    defender: str,
    action: str,
    result: str,
    damage: Optional[int] = None,
    special_effects: Optional[str] = None
) -> str:
    """
    Synchronous wrapper for combat description generation.
    Uses asyncio.run() to execute async function.
    """
    generator = get_llm_generator()
    return asyncio.run(
        generator.generate_combat_description(
            attacker, defender, action, result, damage, special_effects
        )
    )


def generate_event_narrative_sync(
    event_type: str,
    context: Dict[str, Any]
) -> str:
    """
    Synchronous wrapper for event narrative generation.
    Uses asyncio.run() to execute async function.
    """
    generator = get_llm_generator()
    return asyncio.run(
        generator.generate_event_narrative(event_type, context)
    )
