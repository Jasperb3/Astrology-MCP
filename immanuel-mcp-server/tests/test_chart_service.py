"""
Tests for the chart service functionality.

This module tests chart generation, calculations, and conversions
using the Immanuel astrology library.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict

from app.services.chart_service import ChartService
from app.models.astrology import (
    NatalChartRequest,
    ProgressedChartRequest,
    SolarReturnRequest,
    CompositeChartRequest,
    SynastryRequest,
    TransitsRequest,
    GeographicCoordinate,
    ChartData
)
from app.utils.exceptions import ChartGenerationError, ValidationError


@pytest.mark.unit
class TestChartService:
    """Test chart service functionality."""
    
    def test_init_validates_immanuel_import(self, mock_immanuel: MagicMock) -> None:
        """Test that ChartService validates Immanuel import on initialization."""
        service = ChartService()
        assert service is not None
    
    def test_init_fails_without_immanuel(self) -> None:
        """Test that ChartService fails without Immanuel library."""
        with patch('app.services.chart_service.import_immanuel', side_effect=ImportError("No module named 'immanuel'")):
            with pytest.raises(ChartGenerationError) as exc_info:
                ChartService()
            assert "Immanuel astrology library is not available" in str(exc_info.value)
    
    def test_convert_coordinates_decimal_degrees(self, chart_service: ChartService) -> None:
        """Test coordinate conversion from decimal degrees."""
        lat, lon = chart_service._convert_coordinates(32.71667, -117.15)
        assert lat == 32.71667
        assert lon == -117.15
    
    def test_convert_coordinates_dms_format(self, chart_service: ChartService) -> None:
        """Test coordinate conversion from DMS format."""
        lat, lon = chart_service._convert_coordinates("32n43", "117w09")
        assert lat == pytest.approx(32 + 43 / 60.0)
        assert lon == pytest.approx(-(117 + 9 / 60.0))
    
    def test_convert_coordinates_invalid_format(self, chart_service: ChartService) -> None:
        """Test coordinate conversion with invalid format."""
        with pytest.raises(ValidationError):
            chart_service._convert_coordinates("invalid", "format")
    
    @pytest.mark.asyncio
    async def test_generate_natal_chart_success(
        self, 
        chart_service: ChartService, 
        sample_natal_request: Dict[str, Any],
        mock_immanuel: MagicMock
    ) -> None:
        """Test successful natal chart generation."""
        request = NatalChartRequest(**sample_natal_request)
        
        with patch.object(chart_service, '_convert_immanuel_chart') as mock_convert:
            mock_chart_data = ChartData(
                chart_type="natal",
                date_time=request.date_time,
                coordinates=request.coordinates,
                timezone="America/Los_Angeles",
                house_system="placidus",
                planets=[],
                houses=[],
                aspects=[],
                metadata={}
            )
            mock_convert.return_value = mock_chart_data
            
            result = await chart_service.generate_natal_chart(request)
            
            assert result.chart_type == "natal"
            assert result.date_time == request.date_time
            mock_convert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_natal_chart_immanuel_error(
        self, 
        chart_service: ChartService, 
        sample_natal_request: Dict[str, Any],
        mock_immanuel: MagicMock
    ) -> None:
        """Test natal chart generation with Immanuel error."""
        request = NatalChartRequest(**sample_natal_request)
        
        mock_immanuel.charts.Chart.side_effect = Exception("Immanuel error")
        
        with pytest.raises(ChartGenerationError) as exc_info:
            await chart_service.generate_natal_chart(request)
        
        assert "Failed to generate natal chart" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_progressed_chart_success(
        self, 
        chart_service: ChartService,
        sample_chart_data: Dict[str, Any],
        mock_immanuel: MagicMock
    ) -> None:
        """Test successful progressed chart generation."""
        request = ProgressedChartRequest(
            natal_chart=sample_chart_data,
            progression_date="2024-05-15 14:30:00",
            date_time=sample_chart_data["date_time"],
            coordinates=GeographicCoordinate(**sample_chart_data["coordinates"])
        )
        
        with patch.object(chart_service, '_convert_immanuel_chart') as mock_convert:
            mock_chart_data = ChartData(
                chart_type="progressed",
                date_time=request.date_time,
                coordinates=request.coordinates,
                timezone="UTC",
                house_system="placidus",
                planets=[],
                houses=[],
                aspects=[],
                metadata={}
            )
            mock_convert.return_value = mock_chart_data
            
            result = await chart_service.generate_progressed_chart(request)
            
            assert result.chart_type == "progressed"
            mock_convert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_solar_return_success(
        self, 
        chart_service: ChartService,
        mock_immanuel: MagicMock
    ) -> None:
        """Test successful solar return chart generation."""
        birth_data = NatalChartRequest(
            date_time="1990-05-15 14:30:00",
            coordinates=GeographicCoordinate(latitude="32n43", longitude="117w09")
        )
        
        request = SolarReturnRequest(
            birth_data=birth_data,
            return_year=2024,
            date_time="2024-05-15 14:30:00",
            coordinates=GeographicCoordinate(latitude="32n43", longitude="117w09")
        )
        
        with patch.object(chart_service, '_convert_immanuel_chart') as mock_convert:
            mock_chart_data = ChartData(
                chart_type="solar_return",
                date_time=request.date_time,
                coordinates=request.coordinates,
                timezone="UTC",
                house_system="placidus",
                planets=[],
                houses=[],
                aspects=[],
                metadata={}
            )
            mock_convert.return_value = mock_chart_data
            
            result = await chart_service.generate_solar_return(request)
            
            assert result.chart_type == "solar_return"
            mock_convert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_composite_chart_success(
        self, 
        chart_service: ChartService,
        mock_immanuel: MagicMock
    ) -> None:
        """Test successful composite chart generation."""
        person1 = NatalChartRequest(
            date_time="1990-05-15 14:30:00",
            coordinates=GeographicCoordinate(latitude="32n43", longitude="117w09")
        )
        person2 = NatalChartRequest(
            date_time="1992-08-22 10:15:00",
            coordinates=GeographicCoordinate(latitude="40n45", longitude="73w59")
        )
        
        request = CompositeChartRequest(person1=person1, person2=person2)
        
        with patch.object(chart_service, '_convert_immanuel_chart') as mock_convert:
            mock_chart_data = ChartData(
                chart_type="composite",
                date_time="1991-06-18 12:22:30",  # Midpoint
                coordinates=GeographicCoordinate(latitude=36.0, longitude=-95.0),
                timezone="UTC",
                house_system="placidus",
                planets=[],
                houses=[],
                aspects=[],
                metadata={}
            )
            mock_convert.return_value = mock_chart_data
            
            result = await chart_service.generate_composite_chart(request)
            
            assert result.chart_type == "composite"
            mock_convert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_synastry_success(
        self, 
        chart_service: ChartService,
        sample_synastry_request: Dict[str, Any],
        mock_immanuel: MagicMock
    ) -> None:
        """Test successful synastry calculation."""
        request = SynastryRequest(**sample_synastry_request)
        
        with patch.object(chart_service, 'generate_natal_chart') as mock_natal, \
             patch.object(chart_service, 'generate_composite_chart') as mock_composite, \
             patch.object(chart_service, '_calculate_interaspects') as mock_aspects, \
             patch.object(chart_service, '_calculate_compatibility_score') as mock_score:
            
            # Mock chart data
            mock_chart = ChartData(
                chart_type="natal",
                date_time="1990-05-15 14:30:00",
                coordinates=GeographicCoordinate(latitude="32n43", longitude="117w09"),
                timezone="UTC",
                house_system="placidus",
                planets=[],
                houses=[],
                aspects=[],
                metadata={}
            )
            
            mock_natal.return_value = mock_chart
            mock_composite.return_value = mock_chart
            mock_aspects.return_value = []
            mock_score.return_value = 75.0
            
            result = await chart_service.calculate_synastry(request)
            
            assert result.person1_chart is not None
            assert result.person2_chart is not None
            assert result.compatibility_score == 75.0
    
    @pytest.mark.asyncio
    async def test_get_transits_success(
        self, 
        chart_service: ChartService,
        sample_transit_request: Dict[str, Any],
        mock_immanuel: MagicMock
    ) -> None:
        """Test successful transit calculation."""
        request = TransitsRequest(**sample_transit_request)
        
        with patch.object(chart_service, '_calculate_transit_aspects') as mock_transits:
            mock_transits.return_value = []
            
            result = await chart_service.get_transits(request)
            
            assert isinstance(result, list)
            mock_transits.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_dignities_success(
        self, 
        chart_service: ChartService,
        sample_chart_data: Dict[str, Any]
    ) -> None:
        """Test successful dignity calculation."""
        chart_data = ChartData(**sample_chart_data)
        
        result = await chart_service.calculate_dignities(chart_data)
        
        assert isinstance(result, list)
        assert len(result) == len(chart_data.planets)
        
        for dignity in result:
            assert hasattr(dignity, 'planet')
            assert hasattr(dignity, 'total_score')
    
    @pytest.mark.asyncio
    async def test_interpret_aspects_success(
        self, 
        chart_service: ChartService,
        sample_chart_data: Dict[str, Any]
    ) -> None:
        """Test successful aspect interpretation."""
        chart_data = ChartData(**sample_chart_data)
        
        result = await chart_service.interpret_aspects(chart_data, "medium")
        
        assert result.interpretation_type == "aspects"
        assert isinstance(result.detailed_analysis, list)
        assert isinstance(result.keywords, list)
    
    def test_calculate_aspect_conjunction(self, chart_service: ChartService) -> None:
        """Test aspect calculation for conjunction."""
        from app.models.astrology import PlanetPosition
        from app.config import ASPECT_ORBS
        
        planet1 = PlanetPosition(
            name="sun", longitude=120.0, latitude=0.0,
            distance=1.0, speed=1.0, sign="leo"
        )
        planet2 = PlanetPosition(
            name="moon", longitude=125.0, latitude=0.0,
            distance=0.002, speed=13.0, sign="leo"
        )
        
        aspect = chart_service._calculate_aspect(planet1, planet2, ASPECT_ORBS)
        
        assert aspect is not None
        assert aspect.aspect_type == "conjunction"
        assert aspect.orb == 5.0
    
    def test_calculate_aspect_no_aspect(self, chart_service: ChartService) -> None:
        """Test aspect calculation when no aspect is formed."""
        from app.models.astrology import PlanetPosition
        from app.config import ASPECT_ORBS
        
        planet1 = PlanetPosition(
            name="sun", longitude=0.0, latitude=0.0,
            distance=1.0, speed=1.0, sign="aries"
        )
        planet2 = PlanetPosition(
            name="moon", longitude=45.0, latitude=0.0,
            distance=0.002, speed=13.0, sign="taurus"
        )
        
        aspect = chart_service._calculate_aspect(planet1, planet2, ASPECT_ORBS)
        
        # 45 degrees should not form a major aspect
        assert aspect is None
    
    def test_calculate_compatibility_score_positive(self, chart_service: ChartService) -> None:
        """Test compatibility score calculation with positive aspects."""
        from app.models.astrology import Aspect
        
        aspects = [
            Aspect(
                planet1="sun", planet2="moon", aspect_type="trine",
                orb=2.0, exact_orb=120.0, applying=True, separating=False
            ),
            Aspect(
                planet1="venus", planet2="mars", aspect_type="sextile",
                orb=1.5, exact_orb=60.0, applying=True, separating=False
            )
        ]
        
        score = chart_service._calculate_compatibility_score(aspects)
        
        assert score > 50.0  # Should be positive
    
    def test_calculate_compatibility_score_negative(self, chart_service: ChartService) -> None:
        """Test compatibility score calculation with challenging aspects."""
        from app.models.astrology import Aspect
        
        aspects = [
            Aspect(
                planet1="sun", planet2="saturn", aspect_type="square",
                orb=2.0, exact_orb=90.0, applying=True, separating=False
            ),
            Aspect(
                planet1="moon", planet2="mars", aspect_type="opposition",
                orb=1.5, exact_orb=180.0, applying=True, separating=False
            )
        ]
        
        score = chart_service._calculate_compatibility_score(aspects)
        
        assert score < 50.0  # Should be negative
    
    def test_calculate_planet_dignity_ruler(self, chart_service: ChartService) -> None:
        """Test dignity calculation for planet in its rulership."""
        from app.models.astrology import PlanetPosition
        
        planet = PlanetPosition(
            name="sun", longitude=120.0, latitude=0.0,
            distance=1.0, speed=1.0, sign="leo", house=5
        )
        
        dignity = chart_service._calculate_planet_dignity(planet)
        
        assert dignity.planet == "sun"
        assert dignity.sign == "leo"
        assert dignity.total_score > 0  # Sun rules Leo
    
    def test_calculate_planet_dignity_no_dignity(self, chart_service: ChartService) -> None:
        """Test dignity calculation for planet with no special dignity."""
        from app.models.astrology import PlanetPosition
        
        planet = PlanetPosition(
            name="mercury", longitude=120.0, latitude=0.0,
            distance=1.0, speed=1.0, sign="leo", house=5
        )
        
        dignity = chart_service._calculate_planet_dignity(planet)
        
        assert dignity.planet == "mercury"
        assert dignity.sign == "leo"
        assert dignity.total_score == 0  # Mercury doesn't rule Leo