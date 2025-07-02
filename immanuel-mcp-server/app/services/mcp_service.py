"""
MCP protocol service for handling MCP-specific operations.

This module provides services for MCP protocol handling, including
tool management, resource management, and prompt handling.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from app.config import get_settings, MCP_CAPABILITIES, CHART_TYPES, HOUSE_SYSTEMS
from app.models.mcp import (
    ServerCapabilities,
    Tool,
    Resource,
    Prompt,
    PromptArgument,
    PromptMessage,
    ToolResult,
    MCPProtocolVersion
)
from app.utils.logging import get_logger
from app.utils.exceptions import (
    ToolNotFoundError,
    ResourceNotFoundError,
    PromptNotFoundError,
    MCPProtocolError
)

logger = get_logger(__name__)


class MCPService:
    """Service for handling MCP protocol operations."""
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self._tools: Dict[str, Tool] = {}
        self._resources: Dict[str, Resource] = {}
        self._prompts: Dict[str, Prompt] = {}
        self._initialize_mcp_data()
    
    def _initialize_mcp_data(self) -> None:
        """Initialize MCP tools, resources, and prompts."""
        self._setup_tools()
        self._setup_resources()
        self._setup_prompts()
    
    def _setup_tools(self) -> None:
        """Set up available MCP tools."""
        tools_definitions = [
            {
                "name": "generate_natal_chart",
                "description": "Generate a natal (birth) chart with planets, houses, and aspects",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "date_time": {
                            "type": "string",
                            "description": "ISO format datetime: YYYY-MM-DD HH:MM:SS"
                        },
                        "latitude": {
                            "type": ["string", "number"],
                            "description": "Latitude in decimal degrees or DMS format (e.g., '32n43' or 32.71667)"
                        },
                        "longitude": {
                            "type": ["string", "number"],
                            "description": "Longitude in decimal degrees or DMS format (e.g., '117w09' or -117.15)"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone identifier (optional, will auto-detect if not provided)"
                        },
                        "house_system": {
                            "type": "string",
                            "description": "House system to use",
                            "enum": HOUSE_SYSTEMS,
                            "default": "placidus"
                        },
                        "objects": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of objects to include (optional, uses defaults if not provided)"
                        }
                    },
                    "required": ["date_time", "latitude", "longitude"]
                }
            },
            {
                "name": "generate_progressed_chart",
                "description": "Generate a progressed chart for a specific date",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "natal_chart": {
                            "type": "object",
                            "description": "Reference natal chart data"
                        },
                        "progression_date": {
                            "type": "string",
                            "description": "Date for progression (ISO format)"
                        },
                        "house_system": {
                            "type": "string",
                            "enum": HOUSE_SYSTEMS,
                            "default": "placidus"
                        }
                    },
                    "required": ["natal_chart", "progression_date"]
                }
            },
            {
                "name": "generate_solar_return",
                "description": "Generate a solar return chart for a specific year",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "birth_data": {
                            "type": "object",
                            "description": "Original birth data"
                        },
                        "return_year": {
                            "type": "integer",
                            "description": "Year for solar return"
                        },
                        "return_location": {
                            "type": "object",
                            "description": "Location for solar return (optional, uses birth location if not provided)",
                            "properties": {
                                "latitude": {"type": ["string", "number"]},
                                "longitude": {"type": ["string", "number"]}
                            }
                        }
                    },
                    "required": ["birth_data", "return_year"]
                }
            },
            {
                "name": "generate_composite_chart",
                "description": "Generate a composite chart from two natal charts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "person1": {
                            "type": "object",
                            "description": "First person's birth data"
                        },
                        "person2": {
                            "type": "object",
                            "description": "Second person's birth data"
                        },
                        "house_system": {
                            "type": "string",
                            "enum": HOUSE_SYSTEMS,
                            "default": "placidus"
                        }
                    },
                    "required": ["person1", "person2"]
                }
            },
            {
                "name": "calculate_synastry",
                "description": "Calculate synastry aspects between two natal charts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "person1": {
                            "type": "object",
                            "description": "First person's birth data"
                        },
                        "person2": {
                            "type": "object",
                            "description": "Second person's birth data"
                        },
                        "aspect_orbs": {
                            "type": "object",
                            "description": "Custom aspect orbs (optional)",
                            "properties": {
                                "conjunction": {"type": "number"},
                                "opposition": {"type": "number"},
                                "trine": {"type": "number"},
                                "square": {"type": "number"},
                                "sextile": {"type": "number"}
                            }
                        }
                    },
                    "required": ["person1", "person2"]
                }
            },
            {
                "name": "get_transits",
                "description": "Get current transits to a natal chart",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "natal_chart": {
                            "type": "object",
                            "description": "Reference natal chart"
                        },
                        "transit_date": {
                            "type": "string",
                            "description": "Date for transit analysis (ISO format)"
                        },
                        "objects": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Transiting objects to include (optional)"
                        }
                    },
                    "required": ["natal_chart", "transit_date"]
                }
            },
            {
                "name": "interpret_aspects",
                "description": "Get interpretations for chart aspects",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chart_data": {
                            "type": "object",
                            "description": "Chart data containing aspects"
                        },
                        "aspect_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific aspect types to interpret (optional)"
                        },
                        "detail_level": {
                            "type": "string",
                            "enum": ["basic", "medium", "detailed"],
                            "default": "medium"
                        }
                    },
                    "required": ["chart_data"]
                }
            },
            {
                "name": "calculate_dignities",
                "description": "Calculate essential dignities for planets",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chart_data": {
                            "type": "object",
                            "description": "Chart data with planet positions"
                        }
                    },
                    "required": ["chart_data"]
                }
            }
        ]
        
        for tool_def in tools_definitions:
            tool = Tool(**tool_def)
            self._tools[tool.name] = tool
    
    def _setup_resources(self) -> None:
        """Set up available MCP resources."""
        resources_definitions = [
            {
                "uri": "astrological_objects",
                "name": "Astrological Objects",
                "description": "List of planets, asteroids, and points available for chart calculation",
                "mimeType": "application/json"
            },
            {
                "uri": "house_systems",
                "name": "House Systems", 
                "description": "Available house systems for chart calculation",
                "mimeType": "application/json"
            },
            {
                "uri": "aspect_patterns",
                "name": "Aspect Patterns",
                "description": "Supported aspect types and default orbs",
                "mimeType": "application/json"
            },
            {
                "uri": "sign_meanings",
                "name": "Zodiac Sign Meanings",
                "description": "Interpretations and symbolism for zodiac signs",
                "mimeType": "application/json"
            },
            {
                "uri": "planet_meanings",
                "name": "Planet Meanings",
                "description": "Planetary symbolism and keywords",
                "mimeType": "application/json"
            },
            {
                "uri": "house_meanings",
                "name": "House Meanings",
                "description": "Astrological house interpretations",
                "mimeType": "application/json"
            }
        ]
        
        for resource_def in resources_definitions:
            resource = Resource(**resource_def)
            self._resources[resource.uri] = resource
    
    def _setup_prompts(self) -> None:
        """Set up available MCP prompts."""
        prompts_definitions = [
            {
                "name": "natal_chart_interpretation",
                "description": "Generate a comprehensive natal chart interpretation",
                "arguments": [
                    PromptArgument(name="chart_data", description="Complete natal chart data", required=True),
                    PromptArgument(name="focus_areas", description="Areas to emphasize (optional)", required=False),
                    PromptArgument(name="detail_level", description="Level of detail: basic, medium, detailed", required=False)
                ]
            },
            {
                "name": "transit_report",
                "description": "Generate a transit report for current planetary movements",
                "arguments": [
                    PromptArgument(name="natal_chart", description="Reference natal chart", required=True),
                    PromptArgument(name="transit_data", description="Current transit data", required=True),
                    PromptArgument(name="time_period", description="Time period for the report", required=False)
                ]
            },
            {
                "name": "compatibility_analysis",
                "description": "Generate a relationship compatibility analysis",
                "arguments": [
                    PromptArgument(name="synastry_data", description="Synastry analysis data", required=True),
                    PromptArgument(name="relationship_type", description="Type of relationship being analyzed", required=False)
                ]
            },
            {
                "name": "progression_forecast",
                "description": "Generate a progressed chart analysis and forecast",
                "arguments": [
                    PromptArgument(name="progressed_chart", description="Progressed chart data", required=True),
                    PromptArgument(name="natal_chart", description="Reference natal chart", required=True),
                    PromptArgument(name="time_frame", description="Time frame for the forecast", required=False)
                ]
            }
        ]
        
        for prompt_def in prompts_definitions:
            prompt = Prompt(**prompt_def)
            self._prompts[prompt.name] = prompt
    
    def get_server_capabilities(self) -> ServerCapabilities:
        """Get server capabilities for MCP initialization."""
        return ServerCapabilities(**MCP_CAPABILITIES)
    
    def list_tools(self, cursor: Optional[str] = None) -> List[Tool]:
        """List available tools."""
        return list(self._tools.values())
    
    def get_tool(self, name: str) -> Tool:
        """Get a specific tool by name."""
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]
    
    def list_resources(self, cursor: Optional[str] = None) -> List[Resource]:
        """List available resources."""
        return list(self._resources.values())
    
    def get_resource_content(self, uri: str) -> Dict[str, Any]:
        """Get content for a specific resource."""
        if uri not in self._resources:
            raise ResourceNotFoundError(uri)
        
        # Return resource-specific content
        content_map = {
            "astrological_objects": self._get_astrological_objects_content(),
            "house_systems": self._get_house_systems_content(),
            "aspect_patterns": self._get_aspect_patterns_content(),
            "sign_meanings": self._get_sign_meanings_content(),
            "planet_meanings": self._get_planet_meanings_content(),
            "house_meanings": self._get_house_meanings_content()
        }
        
        return content_map.get(uri, {})
    
    def list_prompts(self, cursor: Optional[str] = None) -> List[Prompt]:
        """List available prompts."""
        return list(self._prompts.values())
    
    def get_prompt_content(self, name: str, arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Get formatted prompt content."""
        if name not in self._prompts:
            raise PromptNotFoundError(name)
        
        # Generate prompt content based on name and arguments
        prompt_generators = {
            "natal_chart_interpretation": self._generate_natal_interpretation_prompt,
            "transit_report": self._generate_transit_report_prompt,
            "compatibility_analysis": self._generate_compatibility_prompt,
            "progression_forecast": self._generate_progression_prompt
        }
        
        generator = prompt_generators.get(name)
        if not generator:
            raise MCPProtocolError(f"Prompt generator not implemented for: {name}")
        
        return generator(arguments)
    
    def _get_astrological_objects_content(self) -> Dict[str, Any]:
        """Get astrological objects content."""
        return {
            "planets": ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"],
            "asteroids": ["chiron", "ceres", "pallas", "juno", "vesta"],
            "points": ["north_node", "south_node", "lilith", "part_of_fortune", "vertex"],
            "luminaries": ["sun", "moon"],
            "personal_planets": ["sun", "moon", "mercury", "venus", "mars"],
            "social_planets": ["jupiter", "saturn"],
            "outer_planets": ["uranus", "neptune", "pluto"]
        }
    
    def _get_house_systems_content(self) -> Dict[str, Any]:
        """Get house systems content."""
        return {
            "systems": HOUSE_SYSTEMS,
            "descriptions": {
                "placidus": "Most popular system, uses time-based division",
                "koch": "Birthplace system, focuses on birthplace coordinates",
                "equal": "Equal 30-degree houses from Ascendant",
                "whole_sign": "Entire signs as houses, ancient system"
            }
        }
    
    def _get_aspect_patterns_content(self) -> Dict[str, Any]:
        """Get aspect patterns content."""
        from app.config import ASPECT_ORBS
        return {
            "major_aspects": {
                "conjunction": {"degrees": 0, "orb": ASPECT_ORBS["conjunction"], "nature": "neutral"},
                "opposition": {"degrees": 180, "orb": ASPECT_ORBS["opposition"], "nature": "challenging"},
                "trine": {"degrees": 120, "orb": ASPECT_ORBS["trine"], "nature": "harmonious"},
                "square": {"degrees": 90, "orb": ASPECT_ORBS["square"], "nature": "challenging"},
                "sextile": {"degrees": 60, "orb": ASPECT_ORBS["sextile"], "nature": "harmonious"}
            },
            "minor_aspects": {
                "quincunx": {"degrees": 150, "orb": ASPECT_ORBS["quincunx"], "nature": "challenging"},
                "semisextile": {"degrees": 30, "orb": ASPECT_ORBS["semisextile"], "nature": "neutral"}
            }
        }
    
    def _get_sign_meanings_content(self) -> Dict[str, Any]:
        """Get zodiac sign meanings content."""
        return {
            "signs": {
                "aries": {"element": "fire", "modality": "cardinal", "ruler": "mars", "keywords": ["initiative", "courage", "leadership"]},
                "taurus": {"element": "earth", "modality": "fixed", "ruler": "venus", "keywords": ["stability", "luxury", "persistence"]},
                "gemini": {"element": "air", "modality": "mutable", "ruler": "mercury", "keywords": ["communication", "curiosity", "versatility"]},
                "cancer": {"element": "water", "modality": "cardinal", "ruler": "moon", "keywords": ["nurturing", "intuition", "family"]},
                "leo": {"element": "fire", "modality": "fixed", "ruler": "sun", "keywords": ["creativity", "leadership", "drama"]},
                "virgo": {"element": "earth", "modality": "mutable", "ruler": "mercury", "keywords": ["service", "analysis", "perfectionism"]},
                "libra": {"element": "air", "modality": "cardinal", "ruler": "venus", "keywords": ["balance", "harmony", "relationships"]},
                "scorpio": {"element": "water", "modality": "fixed", "ruler": "pluto", "keywords": ["transformation", "intensity", "mystery"]},
                "sagittarius": {"element": "fire", "modality": "mutable", "ruler": "jupiter", "keywords": ["philosophy", "adventure", "truth"]},
                "capricorn": {"element": "earth", "modality": "cardinal", "ruler": "saturn", "keywords": ["ambition", "structure", "authority"]},
                "aquarius": {"element": "air", "modality": "fixed", "ruler": "uranus", "keywords": ["innovation", "humanity", "independence"]},
                "pisces": {"element": "water", "modality": "mutable", "ruler": "neptune", "keywords": ["compassion", "spirituality", "imagination"]}
            }
        }
    
    def _get_planet_meanings_content(self) -> Dict[str, Any]:
        """Get planet meanings content."""
        return {
            "planets": {
                "sun": {"keywords": ["identity", "ego", "vitality"], "rules": ["leo"]},
                "moon": {"keywords": ["emotions", "instincts", "nurturing"], "rules": ["cancer"]},
                "mercury": {"keywords": ["communication", "thinking", "learning"], "rules": ["gemini", "virgo"]},
                "venus": {"keywords": ["love", "beauty", "values"], "rules": ["taurus", "libra"]},
                "mars": {"keywords": ["action", "desire", "courage"], "rules": ["aries"]},
                "jupiter": {"keywords": ["expansion", "wisdom", "luck"], "rules": ["sagittarius"]},
                "saturn": {"keywords": ["discipline", "structure", "lessons"], "rules": ["capricorn"]},
                "uranus": {"keywords": ["innovation", "rebellion", "change"], "rules": ["aquarius"]},
                "neptune": {"keywords": ["spirituality", "illusion", "compassion"], "rules": ["pisces"]},
                "pluto": {"keywords": ["transformation", "power", "rebirth"], "rules": ["scorpio"]}
            }
        }
    
    def _get_house_meanings_content(self) -> Dict[str, Any]:
        """Get house meanings content."""
        return {
            "houses": {
                "1": {"name": "Ascendant", "keywords": ["identity", "appearance", "first impressions"]},
                "2": {"name": "Possessions", "keywords": ["money", "values", "self-worth"]},
                "3": {"name": "Communication", "keywords": ["siblings", "learning", "short trips"]},
                "4": {"name": "Home", "keywords": ["family", "roots", "security"]},
                "5": {"name": "Creativity", "keywords": ["children", "romance", "self-expression"]},
                "6": {"name": "Service", "keywords": ["work", "health", "daily routine"]},
                "7": {"name": "Partnerships", "keywords": ["marriage", "open enemies", "cooperation"]},
                "8": {"name": "Transformation", "keywords": ["death", "other's money", "occult"]},
                "9": {"name": "Philosophy", "keywords": ["higher learning", "long trips", "beliefs"]},
                "10": {"name": "Career", "keywords": ["reputation", "authority", "public image"]},
                "11": {"name": "Friends", "keywords": ["groups", "hopes", "social causes"]},
                "12": {"name": "Unconscious", "keywords": ["spirituality", "hidden enemies", "sacrifice"]}
            }
        }
    
    def _generate_natal_interpretation_prompt(self, arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Generate natal chart interpretation prompt."""
        chart_data = arguments.get("chart_data", {})
        focus_areas = arguments.get("focus_areas", [])
        detail_level = arguments.get("detail_level", "medium")
        
        content = f"""Generate a comprehensive natal chart interpretation based on the following chart data.

Chart Data: {chart_data}

Focus Areas: {focus_areas if focus_areas else "General interpretation covering all major areas"}
Detail Level: {detail_level}

Please provide:
1. Overall personality overview
2. Key planetary placements and their meanings
3. Important aspects and their influences
4. House emphasis and life themes
5. Potential challenges and strengths
6. Life purpose and karmic lessons

Structure the interpretation in a clear, accessible way while maintaining astrological accuracy."""
        
        return [
            PromptMessage(
                role="user",
                content={"type": "text", "text": content}
            )
        ]
    
    def _generate_transit_report_prompt(self, arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Generate transit report prompt."""
        natal_chart = arguments.get("natal_chart", {})
        transit_data = arguments.get("transit_data", {})
        time_period = arguments.get("time_period", "current")
        
        content = f"""Generate a transit report for the specified time period.

Natal Chart: {natal_chart}
Transit Data: {transit_data}
Time Period: {time_period}

Please provide:
1. Overview of current planetary transits
2. Most significant transiting aspects
3. Areas of life being activated
4. Opportunities and challenges
5. Timing and duration of key transits
6. Practical advice for navigating the period

Focus on the most impactful transits and provide actionable guidance."""
        
        return [
            PromptMessage(
                role="user",
                content={"type": "text", "text": content}
            )
        ]
    
    def _generate_compatibility_prompt(self, arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Generate compatibility analysis prompt."""
        synastry_data = arguments.get("synastry_data", {})
        relationship_type = arguments.get("relationship_type", "romantic")
        
        content = f"""Generate a relationship compatibility analysis based on synastry data.

Synastry Data: {synastry_data}
Relationship Type: {relationship_type}

Please provide:
1. Overall compatibility assessment
2. Strongest connection points
3. Potential challenges and conflicts
4. Communication styles and needs
5. Long-term potential
6. Advice for harmony and growth

Consider both harmonious and challenging aspects, providing a balanced perspective."""
        
        return [
            PromptMessage(
                role="user",
                content={"type": "text", "text": content}
            )
        ]
    
    def _generate_progression_prompt(self, arguments: Dict[str, Any]) -> List[PromptMessage]:
        """Generate progression forecast prompt."""
        progressed_chart = arguments.get("progressed_chart", {})
        natal_chart = arguments.get("natal_chart", {})
        time_frame = arguments.get("time_frame", "year ahead")
        
        content = f"""Generate a progressed chart analysis and forecast.

Progressed Chart: {progressed_chart}
Natal Chart: {natal_chart}
Time Frame: {time_frame}

Please provide:
1. Key progressed planetary movements
2. New aspects forming or separating
3. Evolving life themes and priorities
4. Personal growth opportunities
5. Challenges and lessons ahead
6. Timeline of significant developments

Focus on the most meaningful progressions and their implications for personal development."""
        
        return [
            PromptMessage(
                role="user",
                content={"type": "text", "text": content}
            )
        ]