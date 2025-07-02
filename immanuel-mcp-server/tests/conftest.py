"""
Pytest configuration and fixtures for the Immanuel MCP Server tests.

This module provides common test fixtures and configuration
for the test suite.
"""

import pytest
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings
from app.services.mcp_service import MCPService
from app.services.chart_service import ChartService
from app.services.validation import ValidationService


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def test_settings() -> Dict[str, Any]:
    """Test configuration settings."""
    return {
        "environment": "testing",
        "debug": True,
        "log_level": "DEBUG",
        "mcp_server_name": "test-immanuel",
        "mcp_server_version": "1.0.0-test",
        "default_house_system": "placidus",
        "default_objects": "sun,moon,mercury,venus,mars",
        "enable_asteroids": False
    }


@pytest.fixture
def mock_immanuel() -> Generator[MagicMock, None, None]:
    """Mock the Immanuel library for testing."""
    with pytest.mock.patch('immanuel') as mock:
        # Mock chart creation
        mock_chart = MagicMock()
        mock_chart.objects = {
            'sun': MagicMock(
                longitude=120.5,
                latitude=0.0,
                distance=1.0,
                speed=1.0,
                sign=MagicMock(name='leo'),
                house=MagicMock(number=5)
            ),
            'moon': MagicMock(
                longitude=45.3,
                latitude=5.2,
                distance=0.002,
                speed=13.2,
                sign=MagicMock(name='taurus'),
                house=MagicMock(number=2)
            )
        }
        
        mock_chart.houses = {
            1: MagicMock(longitude=0.0, sign=MagicMock(name='aries')),
            2: MagicMock(longitude=30.0, sign=MagicMock(name='taurus')),
            3: MagicMock(longitude=60.0, sign=MagicMock(name='gemini'))
        }
        
        mock_chart.aspects = [
            MagicMock(
                active=MagicMock(name='sun'),
                passive=MagicMock(name='moon'),
                type=MagicMock(name='trine'),
                orb=2.5,
                applying=True,
                separating=False
            )
        ]
        
        # Mock charts module
        mock.charts.Chart.return_value = mock_chart
        mock.charts.Subject = MagicMock
        
        # Mock chart types
        mock.const.chart_types.NATAL = 'natal'
        mock.const.chart_types.PROGRESSED = 'progressed'
        mock.const.chart_types.SOLAR_RETURN = 'solar_return'
        mock.const.chart_types.COMPOSITE = 'composite'
        
        yield mock


@pytest.fixture
def sample_natal_request() -> Dict[str, Any]:
    """Sample natal chart request data."""
    return {
        "date_time": "1990-05-15 14:30:00",
        "latitude": "32n43",
        "longitude": "117w09",
        "timezone": "America/Los_Angeles",
        "house_system": "placidus",
        "objects": ["sun", "moon", "mercury", "venus", "mars"]
    }


@pytest.fixture
def sample_chart_data() -> Dict[str, Any]:
    """Sample chart data for testing."""
    return {
        "chart_type": "natal",
        "date_time": "1990-05-15 14:30:00",
        "coordinates": {
            "latitude": "32n43",
            "longitude": "117w09"
        },
        "timezone": "America/Los_Angeles",
        "house_system": "placidus",
        "planets": [
            {
                "name": "sun",
                "longitude": 120.5,
                "latitude": 0.0,
                "distance": 1.0,
                "speed": 1.0,
                "sign": "leo",
                "house": 5
            },
            {
                "name": "moon",
                "longitude": 45.3,
                "latitude": 5.2,
                "distance": 0.002,
                "speed": 13.2,
                "sign": "taurus",
                "house": 2
            }
        ],
        "houses": [
            {"number": 1, "cusp": 0.0, "sign": "aries"},
            {"number": 2, "cusp": 30.0, "sign": "taurus"},
            {"number": 3, "cusp": 60.0, "sign": "gemini"}
        ],
        "aspects": [
            {
                "planet1": "sun",
                "planet2": "moon",
                "aspect_type": "trine",
                "orb": 2.5,
                "exact_orb": 120.0,
                "applying": True,
                "separating": False
            }
        ],
        "metadata": {
            "generated_at": "2024-01-01T12:00:00"
        }
    }


@pytest.fixture
def mcp_service() -> MCPService:
    """Create an MCP service instance for testing."""
    return MCPService()


@pytest.fixture
def chart_service() -> ChartService:
    """Create a chart service instance for testing."""
    return ChartService()


@pytest.fixture
def validation_service() -> ValidationService:
    """Create a validation service instance for testing."""
    return ValidationService()


@pytest.fixture
def mock_chart_service() -> Generator[AsyncMock, None, None]:
    """Mock chart service for testing."""
    with pytest.mock.patch('app.services.chart_service.ChartService') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_mcp_initialize_request() -> Dict[str, Any]:
    """Sample MCP initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "experimental": {},
            "roots": [],
            "sampling": {}
        },
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }


@pytest.fixture
def sample_tool_call_request() -> Dict[str, Any]:
    """Sample MCP tool call request."""
    return {
        "name": "generate_natal_chart",
        "arguments": {
            "date_time": "1990-05-15 14:30:00",
            "latitude": "32n43",
            "longitude": "117w09",
            "house_system": "placidus"
        }
    }


@pytest.fixture
def sample_synastry_request() -> Dict[str, Any]:
    """Sample synastry request data."""
    return {
        "person1": {
            "date_time": "1990-05-15 14:30:00",
            "coordinates": {
                "latitude": "32n43",
                "longitude": "117w09"
            },
            "timezone": "America/Los_Angeles"
        },
        "person2": {
            "date_time": "1992-08-22 10:15:00",
            "coordinates": {
                "latitude": "40n45",
                "longitude": "73w59"
            },
            "timezone": "America/New_York"
        }
    }


@pytest.fixture
def sample_transit_request() -> Dict[str, Any]:
    """Sample transit request data."""
    return {
        "natal_chart": {
            "chart_type": "natal",
            "date_time": "1990-05-15 14:30:00",
            "coordinates": {
                "latitude": "32n43",
                "longitude": "117w09"
            },
            "timezone": "America/Los_Angeles",
            "house_system": "placidus",
            "planets": [],
            "houses": [],
            "aspects": [],
            "metadata": {}
        },
        "transit_date": "2024-01-01 12:00:00"
    }


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow