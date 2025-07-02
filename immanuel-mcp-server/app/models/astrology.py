"""
Astrological data models for chart generation and interpretation.

This module defines Pydantic models for astrological data structures,
including charts, aspects, planets, houses, and interpretations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, validator


class GeographicCoordinate(BaseModel):
    """Geographic coordinate representation."""
    model_config = ConfigDict(extra="forbid")
    
    latitude: Union[str, float] = Field(..., description="Latitude in decimal degrees or DMS format")
    longitude: Union[str, float] = Field(..., description="Longitude in decimal degrees or DMS format")
    
    @validator('latitude', 'longitude', pre=True)
    def validate_coordinates(cls, v: Union[str, float]) -> Union[str, float]:
        """Validate coordinate formats."""
        if isinstance(v, str):
            # Validate DMS format (e.g., "32n43" or "117w09")
            if not (v[-1].lower() in 'nsew' and v[:-1].replace('.', '').isdigit()):
                raise ValueError(f"Invalid coordinate format: {v}")
        elif isinstance(v, (int, float)):
            # Validate decimal degrees
            if not -180 <= v <= 180:
                raise ValueError(f"Coordinate out of range: {v}")
        return v


class ChartRequest(BaseModel):
    """Base chart generation request."""
    model_config = ConfigDict(extra="forbid")
    
    date_time: str = Field(..., description="ISO format datetime: YYYY-MM-DD HH:MM:SS")
    coordinates: GeographicCoordinate
    timezone: Optional[str] = Field(None, description="Timezone identifier (e.g., 'America/New_York')")
    house_system: Optional[str] = Field("placidus", description="House system to use")
    objects: Optional[List[str]] = Field(None, description="List of objects to include")
    
    @validator('date_time')
    def validate_datetime(cls, v: str) -> str:
        """Validate datetime format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}")
        return v


class NatalChartRequest(ChartRequest):
    """Natal chart generation request."""
    pass


class ProgressedChartRequest(ChartRequest):
    """Progressed chart generation request."""
    natal_chart: Dict[str, Any] = Field(..., description="Reference natal chart data")
    progression_date: str = Field(..., description="Date for progression")


class SolarReturnRequest(ChartRequest):
    """Solar return chart generation request."""
    birth_data: ChartRequest = Field(..., description="Original birth data")
    return_year: int = Field(..., description="Year for solar return")
    return_location: Optional[GeographicCoordinate] = Field(None, description="Location for solar return")


class CompositeChartRequest(BaseModel):
    """Composite chart generation request."""
    model_config = ConfigDict(extra="forbid")
    
    person1: ChartRequest
    person2: ChartRequest
    house_system: Optional[str] = Field("placidus", description="House system to use")


class SynastryRequest(BaseModel):
    """Synastry analysis request."""
    model_config = ConfigDict(extra="forbid")
    
    person1: ChartRequest
    person2: ChartRequest
    aspect_orbs: Optional[Dict[str, float]] = Field(None, description="Custom aspect orbs")


class TransitsRequest(BaseModel):
    """Transit analysis request."""
    model_config = ConfigDict(extra="forbid")
    
    natal_chart: Dict[str, Any] = Field(..., description="Reference natal chart")
    transit_date: str = Field(..., description="Date for transit analysis")
    objects: Optional[List[str]] = Field(None, description="Transiting objects to include")


class PlanetPosition(BaseModel):
    """Planet position data."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    longitude: float
    latitude: float
    distance: float
    speed: float
    sign: str
    house: Optional[int] = None
    dignities: Optional[Dict[str, Any]] = None


class House(BaseModel):
    """House data."""
    model_config = ConfigDict(extra="forbid")
    
    number: int
    cusp: float
    sign: str
    ruler: Optional[str] = None


class Aspect(BaseModel):
    """Aspect between two points."""
    model_config = ConfigDict(extra="forbid")
    
    planet1: str
    planet2: str
    aspect_type: str
    orb: float
    exact_orb: float
    applying: bool
    separating: bool
    interpretation: Optional[str] = None


class ChartData(BaseModel):
    """Complete chart data structure."""
    model_config = ConfigDict(extra="forbid")
    
    chart_type: str
    date_time: str
    coordinates: GeographicCoordinate
    timezone: str
    house_system: str
    planets: List[PlanetPosition]
    houses: List[House]
    aspects: List[Aspect]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProgressedChart(ChartData):
    """Progressed chart data."""
    natal_chart_id: Optional[str] = None
    progression_date: str = Field(..., description="Date of progression")
    natal_to_progressed_aspects: List[Aspect] = Field(default_factory=list)


class SolarReturnChart(ChartData):
    """Solar return chart data."""
    birth_chart_id: Optional[str] = None
    return_year: int = Field(..., description="Solar return year")
    solar_return_to_natal_aspects: List[Aspect] = Field(default_factory=list)


class CompositeChart(ChartData):
    """Composite chart data."""
    person1_id: Optional[str] = None
    person2_id: Optional[str] = None
    midpoint_method: str = Field(default="arithmetic", description="Midpoint calculation method")


class SynastryAnalysis(BaseModel):
    """Synastry analysis results."""
    model_config = ConfigDict(extra="forbid")
    
    person1_chart: ChartData
    person2_chart: ChartData
    interaspects: List[Aspect]
    composite_chart: Optional[CompositeChart] = None
    compatibility_score: Optional[float] = None
    interpretation: Optional[str] = None


class DignityScore(BaseModel):
    """Essential dignity score for a planet."""
    model_config = ConfigDict(extra="forbid")
    
    planet: str
    sign: str
    house: int
    ruler: int = 0
    exalted: int = 0
    triplicity: int = 0
    term: int = 0
    face: int = 0
    detriment: int = 0
    fall: int = 0
    total_score: int = 0


class InterpretationRequest(BaseModel):
    """Request for astrological interpretation."""
    model_config = ConfigDict(extra="forbid")
    
    chart_data: ChartData
    interpretation_type: str = Field(..., description="Type of interpretation requested")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")
    detail_level: Optional[str] = Field("medium", description="Level of detail: basic, medium, detailed")


class Interpretation(BaseModel):
    """Astrological interpretation result."""
    model_config = ConfigDict(extra="forbid")
    
    interpretation_type: str
    summary: str
    detailed_analysis: List[str]
    keywords: List[str]
    recommendations: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HouseMeaning(BaseModel):
    """House meaning and interpretation."""
    model_config = ConfigDict(extra="forbid")
    
    number: int
    name: str
    keywords: List[str]
    description: str
    ruling_sign: str
    natural_ruler: str


class PlanetMeaning(BaseModel):
    """Planet meaning and interpretation."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    symbol: str
    keywords: List[str]
    description: str
    rules: List[str]
    exaltation: Optional[str] = None
    detriment: List[str] = Field(default_factory=list)
    fall: Optional[str] = None


class SignMeaning(BaseModel):
    """Zodiac sign meaning and interpretation."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    symbol: str
    element: str
    modality: str
    ruler: str
    exaltation_ruler: Optional[str] = None
    keywords: List[str]
    description: str


class AspectPattern(BaseModel):
    """Aspect pattern definition."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    type: str
    orb: float
    nature: str  # harmonious, challenging, neutral
    keywords: List[str]
    description: str