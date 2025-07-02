"""
Chart generation service using the Immanuel astrology library.

This module provides high-level services for generating various types
of astrological charts and performing calculations.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
import re

from app.config import get_settings
from app.models.astrology import (
    ChartData,
    NatalChartRequest,
    ProgressedChartRequest,
    SolarReturnRequest,
    CompositeChartRequest,
    SynastryRequest,
    TransitsRequest,
    PlanetPosition,
    House,
    Aspect,
    DignityScore,
    SynastryAnalysis,
    Interpretation
)
from app.utils.logging import get_logger
from app.utils.exceptions import ChartGenerationError, ValidationError

logger = get_logger(__name__)


class ChartService:
    """Service for generating astrological charts using Immanuel."""
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self._validate_immanuel_import()
    
    def _validate_immanuel_import(self) -> None:
        """Validate that Immanuel library is available."""
        try:
            import immanuel
            logger.info("Immanuel library loaded successfully", version=getattr(immanuel, '__version__', 'unknown'))
        except ImportError as e:
            logger.error("Failed to import Immanuel library", error=str(e))
            raise ChartGenerationError(
                "Immanuel astrology library is not available",
                details={"import_error": str(e)}
            )
    
    async def generate_natal_chart(self, request: NatalChartRequest) -> ChartData:
        """Generate a natal chart."""
        try:
            import immanuel
            from immanuel import charts
            from immanuel.const import chart_types
            
            logger.info("Generating natal chart", date_time=request.date_time)
            
            # Convert coordinates
            lat, lon = self._convert_coordinates(request.coordinates.latitude, request.coordinates.longitude)
            
            # Create chart
            native = charts.Subject(
                date_time=request.date_time,
                latitude=lat,
                longitude=lon,
                time_is_utc=request.timezone is None
            )
            
            chart = charts.Chart(
                subject=native,
                chart_type=chart_types.NATAL,
                house_system=request.house_system or self.settings.default_house_system
            )
            
            # Convert to our format
            chart_data = await self._convert_immanuel_chart(chart, "natal", request)
            
            logger.info("Natal chart generated successfully")
            return chart_data
            
        except Exception as e:
            logger.error("Failed to generate natal chart", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to generate natal chart: {str(e)}")
    
    async def generate_progressed_chart(self, request: ProgressedChartRequest) -> ChartData:
        """Generate a progressed chart."""
        try:
            import immanuel
            from immanuel import charts
            from immanuel.const import chart_types
            
            logger.info("Generating progressed chart", progression_date=request.progression_date)
            
            # Extract natal data from request
            natal_data = request.natal_chart
            lat, lon = self._convert_coordinates(request.coordinates.latitude, request.coordinates.longitude)
            
            # Create subjects
            native = charts.Subject(
                date_time=natal_data.get("date_time", request.date_time),
                latitude=lat,
                longitude=lon
            )
            
            progressed = charts.Subject(
                date_time=request.progression_date,
                latitude=lat,
                longitude=lon
            )
            
            chart = charts.Chart(
                subject=native,
                chart_type=chart_types.PROGRESSED,
                progressed_date=request.progression_date,
                house_system=request.house_system or self.settings.default_house_system
            )
            
            chart_data = await self._convert_immanuel_chart(chart, "progressed", request)
            
            logger.info("Progressed chart generated successfully")
            return chart_data
            
        except Exception as e:
            logger.error("Failed to generate progressed chart", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to generate progressed chart: {str(e)}")
    
    async def generate_solar_return(self, request: SolarReturnRequest) -> ChartData:
        """Generate a solar return chart."""
        try:
            import immanuel
            from immanuel import charts
            from immanuel.const import chart_types
            
            logger.info("Generating solar return chart", return_year=request.return_year)
            
            # Use birth location unless return location specified
            if request.return_location:
                lat, lon = self._convert_coordinates(
                    request.return_location.latitude, 
                    request.return_location.longitude
                )
            else:
                lat, lon = self._convert_coordinates(
                    request.coordinates.latitude, 
                    request.coordinates.longitude
                )
            
            # Create solar return date
            birth_data = request.birth_data
            solar_return_date = f"{request.return_year}-{birth_data.date_time[5:10]} {birth_data.date_time[11:]}"
            
            native = charts.Subject(
                date_time=solar_return_date,
                latitude=lat,
                longitude=lon
            )
            
            chart = charts.Chart(
                subject=native,
                chart_type=chart_types.SOLAR_RETURN,
                house_system=request.house_system or self.settings.default_house_system
            )
            
            chart_data = await self._convert_immanuel_chart(chart, "solar_return", request)
            
            logger.info("Solar return chart generated successfully")
            return chart_data
            
        except Exception as e:
            logger.error("Failed to generate solar return chart", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to generate solar return chart: {str(e)}")
    
    async def generate_composite_chart(self, request: CompositeChartRequest) -> ChartData:
        """Generate a composite chart."""
        try:
            import immanuel
            from immanuel import charts
            from immanuel.const import chart_types
            
            logger.info("Generating composite chart")
            
            # Convert coordinates for both people
            lat1, lon1 = self._convert_coordinates(
                request.person1.coordinates.latitude,
                request.person1.coordinates.longitude
            )
            lat2, lon2 = self._convert_coordinates(
                request.person2.coordinates.latitude,
                request.person2.coordinates.longitude
            )
            
            # Create subjects
            person1 = charts.Subject(
                date_time=request.person1.date_time,
                latitude=lat1,
                longitude=lon1
            )
            
            person2 = charts.Subject(
                date_time=request.person2.date_time,
                latitude=lat2,
                longitude=lon2
            )
            
            chart = charts.Chart(
                subject=person1,
                partner=person2,
                chart_type=chart_types.COMPOSITE,
                house_system=request.house_system or self.settings.default_house_system
            )
            
            chart_data = await self._convert_immanuel_chart(chart, "composite", request)
            
            logger.info("Composite chart generated successfully")
            return chart_data
            
        except Exception as e:
            logger.error("Failed to generate composite chart", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to generate composite chart: {str(e)}")
    
    async def calculate_synastry(self, request: SynastryRequest) -> SynastryAnalysis:
        """Calculate synastry between two charts."""
        try:
            logger.info("Calculating synastry")
            
            # Generate both natal charts
            chart1_req = NatalChartRequest(**request.person1.model_dump())
            chart2_req = NatalChartRequest(**request.person2.model_dump())
            
            chart1 = await self.generate_natal_chart(chart1_req)
            chart2 = await self.generate_natal_chart(chart2_req)
            
            # Calculate interaspects
            interaspects = await self._calculate_interaspects(chart1, chart2, request.aspect_orbs)
            
            # Generate composite chart
            composite_req = CompositeChartRequest(person1=request.person1, person2=request.person2)
            composite_chart = await self.generate_composite_chart(composite_req)
            
            # Calculate compatibility score (simplified)
            compatibility_score = self._calculate_compatibility_score(interaspects)
            
            synastry = SynastryAnalysis(
                person1_chart=chart1,
                person2_chart=chart2,
                interaspects=interaspects,
                composite_chart=composite_chart,
                compatibility_score=compatibility_score
            )
            
            logger.info("Synastry calculated successfully", compatibility_score=compatibility_score)
            return synastry
            
        except Exception as e:
            logger.error("Failed to calculate synastry", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to calculate synastry: {str(e)}")
    
    async def get_transits(self, request: TransitsRequest) -> List[Aspect]:
        """Get current transits to a natal chart."""
        try:
            import immanuel
            from immanuel import charts
            from immanuel.const import chart_types
            
            logger.info("Calculating transits", transit_date=request.transit_date)
            
            # Create transit chart
            natal_data = request.natal_chart
            
            # Create subjects - simplified approach
            transit_subject = charts.Subject(
                date_time=request.transit_date,
                latitude=0,  # Transits are calculated geocentrically
                longitude=0
            )
            
            chart = charts.Chart(
                subject=transit_subject,
                chart_type=chart_types.NATAL,
                house_system=self.settings.default_house_system
            )
            
            # Calculate aspects between transit planets and natal planets
            transits = await self._calculate_transit_aspects(natal_data, chart)
            
            logger.info("Transits calculated successfully", count=len(transits))
            return transits
            
        except Exception as e:
            logger.error("Failed to calculate transits", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to calculate transits: {str(e)}")
    
    async def calculate_dignities(self, chart_data: ChartData) -> List[DignityScore]:
        """Calculate essential dignities for planets."""
        try:
            logger.info("Calculating dignities")
            
            dignities = []
            
            # Essential dignity scoring system
            for planet in chart_data.planets:
                score = self._calculate_planet_dignity(planet)
                dignities.append(score)
            
            logger.info("Dignities calculated successfully", count=len(dignities))
            return dignities
            
        except Exception as e:
            logger.error("Failed to calculate dignities", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to calculate dignities: {str(e)}")
    
    async def interpret_aspects(self, chart_data: ChartData, detail_level: str = "medium") -> Interpretation:
        """Generate aspect interpretations."""
        try:
            logger.info("Interpreting aspects", detail_level=detail_level)
            
            interpretations = []
            keywords = []
            
            for aspect in chart_data.aspects:
                interpretation = self._interpret_single_aspect(aspect, detail_level)
                interpretations.append(interpretation)
                keywords.extend(self._get_aspect_keywords(aspect))
            
            result = Interpretation(
                interpretation_type="aspects",
                summary=f"Analysis of {len(chart_data.aspects)} aspects in the chart",
                detailed_analysis=interpretations,
                keywords=list(set(keywords))
            )
            
            logger.info("Aspects interpreted successfully")
            return result
            
        except Exception as e:
            logger.error("Failed to interpret aspects", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to interpret aspects: {str(e)}")
    
    def _convert_coordinates(self, lat: Union[str, float], lon: Union[str, float]) -> tuple[float, float]:
        """Convert coordinates to decimal degrees."""
        def parse_coordinate(coord: Union[str, float]) -> float:
            if isinstance(coord, (int, float)):
                return float(coord)

            if isinstance(coord, str):
                coord_str = coord.strip().lower()

                # Format like "32n43" or "117w09"
                match = re.fullmatch(r"(\d+)([nswe])(\d+)", coord_str)
                if match:
                    degrees = float(match.group(1))
                    direction = match.group(2)
                    minutes = float(match.group(3))
                    value = degrees + minutes / 60.0
                    if direction in ["s", "w"]:
                        value = -value
                    return value

                # Fall back to plain float string
                try:
                    return float(coord_str)
                except ValueError:
                    pass

            raise ValidationError(f"Invalid coordinate format: {coord}")
        
        return parse_coordinate(lat), parse_coordinate(lon)
    
    async def _convert_immanuel_chart(self, chart: Any, chart_type: str, request: Any) -> ChartData:
        """Convert Immanuel chart to our ChartData format."""
        try:
            planets = []
            houses = []
            aspects = []
            
            # Convert planets
            if hasattr(chart, 'objects') and chart.objects:
                for name, obj in chart.objects.items():
                    if hasattr(obj, 'longitude'):
                        planet = PlanetPosition(
                            name=name,
                            longitude=float(obj.longitude),
                            latitude=getattr(obj, 'latitude', 0.0),
                            distance=getattr(obj, 'distance', 0.0),
                            speed=getattr(obj, 'speed', 0.0),
                            sign=getattr(obj, 'sign', {}).get('name', '') if hasattr(obj, 'sign') else '',
                            house=getattr(obj, 'house', {}).get('number', None) if hasattr(obj, 'house') else None
                        )
                        planets.append(planet)
            
            # Convert houses
            if hasattr(chart, 'houses') and chart.houses:
                for number, house in chart.houses.items():
                    if hasattr(house, 'longitude'):
                        house_obj = House(
                            number=int(number),
                            cusp=float(house.longitude),
                            sign=getattr(house, 'sign', {}).get('name', '') if hasattr(house, 'sign') else ''
                        )
                        houses.append(house_obj)
            
            # Convert aspects
            if hasattr(chart, 'aspects') and chart.aspects:
                for aspect_data in chart.aspects:
                    if hasattr(aspect_data, 'active') and hasattr(aspect_data, 'passive'):
                        aspect = Aspect(
                            planet1=getattr(aspect_data.active, 'name', 'unknown'),
                            planet2=getattr(aspect_data.passive, 'name', 'unknown'),
                            aspect_type=getattr(aspect_data, 'type', {}).get('name', 'unknown'),
                            orb=float(getattr(aspect_data, 'orb', 0)),
                            exact_orb=float(getattr(aspect_data, 'orb', 0)),
                            applying=getattr(aspect_data, 'applying', False),
                            separating=getattr(aspect_data, 'separating', False)
                        )
                        aspects.append(aspect)
            
            # Create chart data
            chart_data = ChartData(
                chart_type=chart_type,
                date_time=request.date_time,
                coordinates=request.coordinates,
                timezone=getattr(request, 'timezone', '') or 'UTC',
                house_system=getattr(request, 'house_system', '') or self.settings.default_house_system,
                planets=planets,
                houses=houses,
                aspects=aspects,
                metadata={
                    "generated_at": datetime.utcnow().isoformat(),
                    "immanuel_version": getattr(__import__('immanuel'), '__version__', 'unknown')
                }
            )
            
            return chart_data
            
        except Exception as e:
            logger.error("Failed to convert Immanuel chart", error=str(e), exc_info=True)
            raise ChartGenerationError(f"Failed to convert chart data: {str(e)}")
    
    async def _calculate_interaspects(self, chart1: ChartData, chart2: ChartData, custom_orbs: Optional[Dict[str, float]]) -> List[Aspect]:
        """Calculate aspects between two charts."""
        from app.config import ASPECT_ORBS
        
        interaspects = []
        orbs = {**ASPECT_ORBS, **(custom_orbs or {})}
        
        for planet1 in chart1.planets:
            for planet2 in chart2.planets:
                aspect = self._calculate_aspect(planet1, planet2, orbs)
                if aspect:
                    interaspects.append(aspect)
        
        return interaspects
    
    async def _calculate_transit_aspects(self, natal_data: Dict[str, Any], transit_chart: Any) -> List[Aspect]:
        """Calculate aspects between transiting and natal planets."""
        # Simplified transit calculation
        # In a full implementation, this would extract planetary positions
        # from both charts and calculate aspects
        return []
    
    def _calculate_aspect(self, planet1: PlanetPosition, planet2: PlanetPosition, orbs: Dict[str, float]) -> Optional[Aspect]:
        """Calculate aspect between two planets."""
        diff = abs(planet1.longitude - planet2.longitude)
        if diff > 180:
            diff = 360 - diff
        
        # Check for major aspects
        aspects_to_check = [
            (0, "conjunction"),
            (60, "sextile"),
            (90, "square"),
            (120, "trine"),
            (180, "opposition")
        ]
        
        for degrees, aspect_name in aspects_to_check:
            orb = orbs.get(aspect_name, 8.0)
            if abs(diff - degrees) <= orb:
                return Aspect(
                    planet1=planet1.name,
                    planet2=planet2.name,
                    aspect_type=aspect_name,
                    orb=abs(diff - degrees),
                    exact_orb=degrees,
                    applying=planet1.speed > planet2.speed,
                    separating=planet1.speed < planet2.speed
                )
        
        return None
    
    def _calculate_compatibility_score(self, aspects: List[Aspect]) -> float:
        """Calculate a simple compatibility score based on aspects."""
        if not aspects:
            return 0.0
        
        harmonious = ["trine", "sextile", "conjunction"]
        challenging = ["square", "opposition"]
        
        positive_score = sum(1 for aspect in aspects if aspect.aspect_type in harmonious)
        negative_score = sum(1 for aspect in aspects if aspect.aspect_type in challenging)
        
        total_aspects = len(aspects)
        if total_aspects == 0:
            return 0.0
        
        # Simple scoring: (positive - negative) / total, normalized to 0-100
        raw_score = (positive_score - negative_score) / total_aspects
        return max(0, min(100, (raw_score + 1) * 50))
    
    def _calculate_planet_dignity(self, planet: PlanetPosition) -> DignityScore:
        """Calculate essential dignity score for a planet."""
        # Simplified dignity calculation
        # In a full implementation, this would check rulership, exaltation, etc.
        
        dignity_map = {
            "sun": {"leo": 5, "aries": 4},
            "moon": {"cancer": 5, "taurus": 4},
            "mercury": {"gemini": 5, "virgo": 5},
            "venus": {"taurus": 5, "libra": 5},
            "mars": {"aries": 5, "scorpio": 5},
            "jupiter": {"sagittarius": 5, "pisces": 5},
            "saturn": {"capricorn": 5, "aquarius": 5}
        }
        
        planet_dignities = dignity_map.get(planet.name.lower(), {})
        sign_score = planet_dignities.get(planet.sign.lower(), 0)
        
        return DignityScore(
            planet=planet.name,
            sign=planet.sign,
            house=planet.house or 1,
            ruler=sign_score if sign_score == 5 else 0,
            exalted=4 if sign_score == 4 else 0,
            total_score=sign_score
        )
    
    def _interpret_single_aspect(self, aspect: Aspect, detail_level: str) -> str:
        """Generate interpretation for a single aspect."""
        basic_interpretations = {
            "conjunction": f"{aspect.planet1} conjunct {aspect.planet2}: Unified energy and focus",
            "sextile": f"{aspect.planet1} sextile {aspect.planet2}: Harmonious opportunity for growth",
            "square": f"{aspect.planet1} square {aspect.planet2}: Dynamic tension requiring resolution",
            "trine": f"{aspect.planet1} trine {aspect.planet2}: Natural flow and ease",
            "opposition": f"{aspect.planet1} opposite {aspect.planet2}: Need for balance and integration"
        }
        
        return basic_interpretations.get(aspect.aspect_type, f"{aspect.planet1} {aspect.aspect_type} {aspect.planet2}")
    
    def _get_aspect_keywords(self, aspect: Aspect) -> List[str]:
        """Get keywords for an aspect."""
        keyword_map = {
            "conjunction": ["unity", "focus", "intensity"],
            "sextile": ["opportunity", "harmony", "cooperation"],
            "square": ["challenge", "tension", "growth"],
            "trine": ["ease", "flow", "talent"],
            "opposition": ["balance", "awareness", "integration"]
        }
        
        return keyword_map.get(aspect.aspect_type, ["aspect"])