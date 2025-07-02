"""
Configuration management for the Immanuel MCP Server.

This module handles environment variables, settings, and configuration
for different deployment environments.
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment Configuration
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server Configuration  
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # MCP Configuration
    mcp_server_name: str = Field(default="immanuel-astrology", env="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="1.0.0", env="MCP_SERVER_VERSION")
    mcp_protocol_version: str = Field(default="2024-11-05", env="MCP_PROTOCOL_VERSION")
    
    # Astrology Configuration
    default_house_system: str = Field(default="placidus", env="DEFAULT_HOUSE_SYSTEM")
    default_objects: str = Field(
        default="sun,moon,mercury,venus,mars,jupiter,saturn,uranus,neptune,pluto",
        env="DEFAULT_OBJECTS"
    )
    default_aspect_orb: float = Field(default=8.0, env="DEFAULT_ASPECT_ORB")
    enable_asteroids: bool = Field(default=False, env="ENABLE_ASTEROIDS")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def default_objects_list(self) -> List[str]:
        """Get default objects as a list."""
        return [obj.strip() for obj in self.default_objects.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Available house systems
HOUSE_SYSTEMS = [
    "placidus", "koch", "porphyrius", "regiomontanus", "campanus",
    "equal", "whole_sign", "alcabitus", "krusinski", "morinus"
]

# Default astrological objects
DEFAULT_PLANETS = [
    "sun", "moon", "mercury", "venus", "mars", "jupiter", 
    "saturn", "uranus", "neptune", "pluto"
]

# Extended objects including asteroids and points
EXTENDED_OBJECTS = DEFAULT_PLANETS + [
    "north_node", "south_node", "chiron", "lilith", "ceres",
    "pallas", "juno", "vesta", "part_of_fortune", "vertex"
]

# Aspect types and default orbs
ASPECT_ORBS = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "trine": 8.0,
    "square": 8.0,
    "sextile": 6.0,
    "quincunx": 3.0,
    "semisextile": 3.0,
    "semisquare": 2.0,
    "sesquisquare": 2.0,
    "quintile": 2.0,
    "biquintile": 2.0
}

# MCP server capabilities
MCP_CAPABILITIES = {
    "experimental": {},
    "logging": {},
    "prompts": {"listChanged": True},
    "resources": {"subscribe": True},
    "tools": {"listChanged": True}
}

# Supported chart types
CHART_TYPES = [
    "natal",
    "progressed",
    "solar_return",
    "composite",
    "synastry",
    "transits"
]