"""
Configuration settings for Shards of Eternity.
Loads settings from environment variables and .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal, Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    # ===========================
    # LLM Configuration
    # ===========================
    llm_enabled: bool = Field(default=True, description="Enable LLM text generation")
    llm_provider: Literal["openai", "anthropic", "local"] = Field(
        default="openai",
        description="LLM provider to use"
    )
    llm_model: str = Field(
        default="gpt-4-turbo-preview",
        description="Model name/identifier"
    )
    llm_api_key: Optional[str] = Field(default=None, description="Primary LLM API key")
    llm_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for local LLM server"
    )
    llm_max_tokens: int = Field(default=500, description="Maximum tokens per generation")
    llm_temperature: float = Field(default=0.8, description="LLM temperature (creativity)")

    # Alternative API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")

    # ===========================
    # Network Configuration
    # ===========================
    master_server_host: str = Field(default="localhost", description="Master server host")
    master_server_port: int = Field(default=8888, description="Master server port")
    master_server_url: str = Field(
        default="http://localhost:8888",
        description="Full master server URL"
    )

    # P2P Configuration
    p2p_port: int = Field(default=9000, description="Peer-to-peer connection port")
    p2p_max_connections: int = Field(
        default=10,
        description="Maximum P2P connections"
    )
    p2p_encryption: bool = Field(default=True, description="Enable P2P encryption")

    # ===========================
    # Database Configuration
    # ===========================
    database_type: Literal["sqlite", "postgresql"] = Field(
        default="sqlite",
        description="Database type"
    )
    database_path: Path = Field(
        default=Path("./shards_of_eternity.db"),
        description="SQLite database path"
    )
    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL"
    )

    # ===========================
    # Game Configuration
    # ===========================
    max_players_per_area: int = Field(
        default=20,
        description="Maximum players in one area"
    )
    autosave_interval: int = Field(
        default=300,
        description="Autosave interval in seconds"
    )
    world_reset_threshold: int = Field(
        default=12,
        description="Number of shards needed to trigger Aetherfall"
    )
    debug_mode: bool = Field(default=False, description="Enable debug mode")

    # ===========================
    # Security & Admin
    # ===========================
    admin_token: str = Field(
        default="change_me_in_production",
        description="Admin authentication token"
    )
    encryption_key: Optional[str] = Field(
        default=None,
        description="Encryption key (auto-generated if empty)"
    )
    session_secret: str = Field(
        default="change_me_in_production",
        description="Session secret key"
    )

    # ===========================
    # Logging
    # ===========================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_file: Path = Field(
        default=Path("./logs/shards.log"),
        description="Log file path"
    )

    @property
    def database_connection_string(self) -> str:
        """Get the appropriate database connection string."""
        if self.database_type == "sqlite":
            return f"sqlite:///{self.database_path}"
        elif self.database_type == "postgresql" and self.database_url:
            return self.database_url
        else:
            raise ValueError("Invalid database configuration")

    @property
    def active_llm_api_key(self) -> Optional[str]:
        """Get the active LLM API key based on provider."""
        if self.llm_api_key:
            return self.llm_api_key

        if self.llm_provider == "openai":
            return self.openai_api_key
        elif self.llm_provider == "anthropic":
            return self.anthropic_api_key

        return None


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
