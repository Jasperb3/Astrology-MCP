"""
Input validation service for astrological data.

This module provides validation functions for chart requests,
coordinates, dates, and other astrological inputs.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from app.config import HOUSE_SYSTEMS, DEFAULT_PLANETS, EXTENDED_OBJECTS
from app.utils.exceptions import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ValidationService:
    """Service for validating astrological inputs."""
    
    @staticmethod
    def validate_datetime(date_time: str) -> bool:
        """Validate datetime format."""
        try:
            # Try to parse ISO format
            datetime.fromisoformat(date_time.replace('Z', '+00:00'))
            return True
        except ValueError:
            raise ValidationError(f"Invalid datetime format: {date_time}. Expected ISO format (YYYY-MM-DD HH:MM:SS)")
    
    @staticmethod
    def validate_coordinates(latitude: Union[str, float], longitude: Union[str, float]) -> bool:
        """Validate geographic coordinates."""
        def validate_single_coordinate(coord: Union[str, float], coord_type: str) -> bool:
            if isinstance(coord, (int, float)):
                # Decimal degrees
                if coord_type == "latitude" and not -90 <= coord <= 90:
                    raise ValidationError(f"Latitude must be between -90 and 90 degrees: {coord}")
                elif coord_type == "longitude" and not -180 <= coord <= 180:
                    raise ValidationError(f"Longitude must be between -180 and 180 degrees: {coord}")
                return True
            
            elif isinstance(coord, str):
                # DMS format like "32n43" or "117w09"
                pattern = r'^(\d+(?:\.\d+)?)[nsewNSEW](\d+(?:\.\d+)?)?$'
                if not re.match(pattern, coord):
                    raise ValidationError(f"Invalid coordinate format: {coord}. Expected format like '32n43' or decimal degrees")
                
                # Extract numeric part and direction
                direction = coord[-1].lower()
                numeric_part = coord[:-1]
                
                try:
                    value = float(numeric_part)
                except ValueError:
                    raise ValidationError(f"Invalid numeric value in coordinate: {coord}")
                
                # Validate ranges based on direction
                if direction in ['n', 's'] and not 0 <= value <= 90:
                    raise ValidationError(f"Latitude value out of range (0-90): {value}")
                elif direction in ['e', 'w'] and not 0 <= value <= 180:
                    raise ValidationError(f"Longitude value out of range (0-180): {value}")
                
                return True
            
            else:
                raise ValidationError(f"Coordinate must be string or number: {type(coord)}")
        
        validate_single_coordinate(latitude, "latitude")
        validate_single_coordinate(longitude, "longitude")
        return True
    
    @staticmethod
    def validate_house_system(house_system: str) -> bool:
        """Validate house system."""
        if house_system not in HOUSE_SYSTEMS:
            raise ValidationError(
                f"Invalid house system: {house_system}. "
                f"Supported systems: {', '.join(HOUSE_SYSTEMS)}"
            )
        return True
    
    @staticmethod
    def validate_objects(objects: List[str], allow_extended: bool = False) -> bool:
        """Validate astrological objects list."""
        valid_objects = EXTENDED_OBJECTS if allow_extended else DEFAULT_PLANETS
        
        for obj in objects:
            if obj not in valid_objects:
                raise ValidationError(
                    f"Invalid object: {obj}. "
                    f"Supported objects: {', '.join(valid_objects)}"
                )
        return True
    
    @staticmethod
    def validate_timezone(timezone: Optional[str]) -> bool:
        """Validate timezone identifier."""
        if timezone is None:
            return True
        
        # Basic timezone validation
        # In a full implementation, you might use pytz to validate
        if not isinstance(timezone, str) or len(timezone) == 0:
            raise ValidationError("Timezone must be a non-empty string")
        
        # Common timezone patterns
        valid_patterns = [
            r'^[A-Z]{3,4}$',  # UTC, GMT, EST, etc.
            r'^[+-]\d{2}:?\d{2}$',  # +05:30, -0800, etc.
            r'^[A-Za-z_]+/[A-Za-z_]+$',  # America/New_York, etc.
        ]
        
        if not any(re.match(pattern, timezone) for pattern in valid_patterns):
            logger.warning("Timezone format not recognized", timezone=timezone)
        
        return True
    
    @staticmethod
    def validate_aspect_orbs(aspect_orbs: Optional[Dict[str, float]]) -> bool:
        """Validate aspect orbs dictionary."""
        if aspect_orbs is None:
            return True
        
        if not isinstance(aspect_orbs, dict):
            raise ValidationError("Aspect orbs must be a dictionary")
        
        valid_aspects = [
            "conjunction", "opposition", "trine", "square", "sextile",
            "quincunx", "semisextile", "semisquare", "sesquisquare"
        ]
        
        for aspect, orb in aspect_orbs.items():
            if aspect not in valid_aspects:
                raise ValidationError(
                    f"Invalid aspect type: {aspect}. "
                    f"Supported aspects: {', '.join(valid_aspects)}"
                )
            
            if not isinstance(orb, (int, float)) or orb < 0 or orb > 30:
                raise ValidationError(f"Invalid orb value for {aspect}: {orb}. Must be between 0 and 30 degrees")
        
        return True
    
    @staticmethod
    def validate_chart_data(chart_data: Dict[str, Any]) -> bool:
        """Validate chart data structure."""
        required_fields = ["chart_type", "date_time", "coordinates", "planets", "houses"]
        
        for field in required_fields:
            if field not in chart_data:
                raise ValidationError(f"Missing required field in chart data: {field}")
        
        # Validate chart type
        valid_chart_types = ["natal", "progressed", "solar_return", "composite", "synastry", "transits"]
        if chart_data["chart_type"] not in valid_chart_types:
            raise ValidationError(
                f"Invalid chart type: {chart_data['chart_type']}. "
                f"Supported types: {', '.join(valid_chart_types)}"
            )
        
        # Validate datetime
        ValidationService.validate_datetime(chart_data["date_time"])
        
        # Validate coordinates
        coords = chart_data["coordinates"]
        if not isinstance(coords, dict) or "latitude" not in coords or "longitude" not in coords:
            raise ValidationError("Invalid coordinates structure")
        
        ValidationService.validate_coordinates(coords["latitude"], coords["longitude"])
        
        # Validate planets list
        if not isinstance(chart_data["planets"], list):
            raise ValidationError("Planets must be a list")
        
        # Validate houses list
        if not isinstance(chart_data["houses"], list):
            raise ValidationError("Houses must be a list")
        
        return True
    
    @staticmethod
    def validate_year(year: int) -> bool:
        """Validate year for solar returns, progressions, etc."""
        current_year = datetime.now().year
        
        if not isinstance(year, int):
            raise ValidationError("Year must be an integer")
        
        if year < 1800 or year > current_year + 100:
            raise ValidationError(
                f"Year out of reasonable range: {year}. "
                f"Must be between 1800 and {current_year + 100}"
            )
        
        return True
    
    @staticmethod
    def validate_interpretation_request(
        chart_data: Dict[str, Any],
        interpretation_type: str,
        detail_level: str
    ) -> bool:
        """Validate interpretation request parameters."""
        # Validate chart data
        ValidationService.validate_chart_data(chart_data)
        
        # Validate interpretation type
        valid_types = ["natal", "aspects", "transits", "synastry", "progression"]
        if interpretation_type not in valid_types:
            raise ValidationError(
                f"Invalid interpretation type: {interpretation_type}. "
                f"Supported types: {', '.join(valid_types)}"
            )
        
        # Validate detail level
        valid_levels = ["basic", "medium", "detailed"]
        if detail_level not in valid_levels:
            raise ValidationError(
                f"Invalid detail level: {detail_level}. "
                f"Supported levels: {', '.join(valid_levels)}"
            )
        
        return True
    
    @staticmethod
    def sanitize_input(value: Any) -> Any:
        """Sanitize input values to prevent injection attacks."""
        if isinstance(value, str):
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '&', '"', "'", '`', '\x00']
            for char in dangerous_chars:
                value = value.replace(char, '')
            
            # Limit string length
            if len(value) > 1000:
                raise ValidationError("Input string too long (max 1000 characters)")
            
            return value.strip()
        
        elif isinstance(value, dict):
            return {k: ValidationService.sanitize_input(v) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [ValidationService.sanitize_input(item) for item in value]
        
        else:
            return value
    
    @staticmethod
    def validate_mcp_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Validate arguments for specific MCP tools."""
        # Tool-specific validation
        validators = {
            "generate_natal_chart": ValidationService._validate_natal_chart_args,
            "generate_progressed_chart": ValidationService._validate_progressed_chart_args,
            "generate_solar_return": ValidationService._validate_solar_return_args,
            "generate_composite_chart": ValidationService._validate_composite_chart_args,
            "calculate_synastry": ValidationService._validate_synastry_args,
            "get_transits": ValidationService._validate_transits_args,
            "interpret_aspects": ValidationService._validate_interpret_aspects_args,
            "calculate_dignities": ValidationService._validate_dignities_args
        }
        
        validator = validators.get(tool_name)
        if validator:
            return validator(arguments)
        
        logger.warning("No specific validator for tool", tool_name=tool_name)
        return True
    
    @staticmethod
    def _validate_natal_chart_args(args: Dict[str, Any]) -> bool:
        """Validate natal chart generation arguments."""
        # Required fields
        required = ["date_time", "latitude", "longitude"]
        for field in required:
            if field not in args:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate each field
        ValidationService.validate_datetime(args["date_time"])
        ValidationService.validate_coordinates(args["latitude"], args["longitude"])
        
        if "timezone" in args:
            ValidationService.validate_timezone(args["timezone"])
        
        if "house_system" in args:
            ValidationService.validate_house_system(args["house_system"])
        
        if "objects" in args:
            ValidationService.validate_objects(args["objects"], allow_extended=True)
        
        return True
    
    @staticmethod
    def _validate_progressed_chart_args(args: Dict[str, Any]) -> bool:
        """Validate progressed chart generation arguments."""
        required = ["natal_chart", "progression_date"]
        for field in required:
            if field not in args:
                raise ValidationError(f"Missing required field: {field}")
        
        ValidationService.validate_chart_data(args["natal_chart"])
        ValidationService.validate_datetime(args["progression_date"])
        
        if "house_system" in args:
            ValidationService.validate_house_system(args["house_system"])
        
        return True
    
    @staticmethod
    def _validate_solar_return_args(args: Dict[str, Any]) -> bool:
        """Validate solar return generation arguments."""
        required = ["birth_data", "return_year"]
        for field in required:
            if field not in args:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate birth data structure
        birth_data = args["birth_data"]
        if not isinstance(birth_data, dict):
            raise ValidationError("Birth data must be an object")
        
        ValidationService._validate_natal_chart_args(birth_data)
        ValidationService.validate_year(args["return_year"])
        
        if "return_location" in args:
            loc = args["return_location"]
            ValidationService.validate_coordinates(loc["latitude"], loc["longitude"])
        
        return True
    
    @staticmethod
    def _validate_composite_chart_args(args: Dict[str, Any]) -> bool:
        """Validate composite chart generation arguments."""
        required = ["person1", "person2"]
        for field in required:
            if field not in args:
                raise ValidationError(f"Missing required field: {field}")
        
        ValidationService._validate_natal_chart_args(args["person1"])
        ValidationService._validate_natal_chart_args(args["person2"])
        
        if "house_system" in args:
            ValidationService.validate_house_system(args["house_system"])
        
        return True
    
    @staticmethod
    def _validate_synastry_args(args: Dict[str, Any]) -> bool:
        """Validate synastry calculation arguments."""
        required = ["person1", "person2"]
        for field in required:
            if field not in args:
                raise ValidationError(f"Missing required field: {field}")
        
        ValidationService._validate_natal_chart_args(args["person1"])
        ValidationService._validate_natal_chart_args(args["person2"])
        
        if "aspect_orbs" in args:
            ValidationService.validate_aspect_orbs(args["aspect_orbs"])
        
        return True
    
    @staticmethod
    def _validate_transits_args(args: Dict[str, Any]) -> bool:
        """Validate transits calculation arguments."""
        required = ["natal_chart", "transit_date"]
        for field in required:
            if field not in args:
                raise ValidationError(f"Missing required field: {field}")
        
        ValidationService.validate_chart_data(args["natal_chart"])
        ValidationService.validate_datetime(args["transit_date"])
        
        if "objects" in args:
            ValidationService.validate_objects(args["objects"], allow_extended=True)
        
        return True
    
    @staticmethod
    def _validate_interpret_aspects_args(args: Dict[str, Any]) -> bool:
        """Validate aspect interpretation arguments."""
        if "chart_data" not in args:
            raise ValidationError("Missing required field: chart_data")
        
        ValidationService.validate_chart_data(args["chart_data"])
        
        if "detail_level" in args:
            valid_levels = ["basic", "medium", "detailed"]
            if args["detail_level"] not in valid_levels:
                raise ValidationError(f"Invalid detail level: {args['detail_level']}")
        
        return True
    
    @staticmethod
    def _validate_dignities_args(args: Dict[str, Any]) -> bool:
        """Validate dignity calculation arguments."""
        if "chart_data" not in args:
            raise ValidationError("Missing required field: chart_data")
        
        ValidationService.validate_chart_data(args["chart_data"])
        return True