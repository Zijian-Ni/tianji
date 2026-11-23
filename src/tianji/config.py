"""
Configuration for tianji.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    api_key: str = field(default="", repr=False)
    provider: str = "openai"
    model: str = "gpt-4o"
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class TianjiConfig:
    """Global configuration for tianji library."""

    # LLM settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""), repr=False)
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("TIANJI_LLM_MODEL", "gpt-4o"))
    llm_temperature: float = 0.7

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    cors_origins: list[str] = field(default_factory=list)

    # Calendar settings
    use_solar_terms_for_month: bool = True  # Use solar terms (节气) for month boundaries

    @property
    def llm(self) -> LLMConfig:
        return LLMConfig(api_key=self.openai_api_key, model=self.openai_model,
                         base_url=self.openai_base_url or None, temperature=self.llm_temperature)

    @classmethod
    def from_env(cls) -> "TianjiConfig":
        """Create config from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("OPENAI_BASE_URL", ""),
            openai_model=os.getenv("TIANJI_LLM_MODEL", "gpt-4o"),
            api_host=os.getenv("TIANJI_API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("TIANJI_API_PORT", "8000")),
        )


# Global singleton
_config: TianjiConfig | None = None


def get_config() -> TianjiConfig:
    """Get the global config (creates from env if needed)."""
    global _config
    if _config is None:
        _config = TianjiConfig.from_env()
    return _config


def set_config(config: TianjiConfig) -> None:
    """Set the global config."""
    global _config
    _config = config
