"""
Integration tests for the Immanuel MCP Server.

This module tests the complete integration between MCP protocol,
chart generation, and API endpoints.
"""

import pytest
from typing import Any, Dict
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient


@pytest.mark.integration
class TestFullIntegration:
    """Test complete integration scenarios."""
    
    def test_full_natal_chart_workflow(
        self, 
        test_client: TestClient,
        sample_mcp_initialize_request: Dict[str, Any],
        mock_immanuel: MagicMock
    ) -> None:
        """Test complete workflow from initialization to natal chart generation."""
        # Step 1: Initialize MCP
        init_response = test_client.post("/mcp/initialize", json=sample_mcp_initialize_request)
        assert init_response.status_code == 200
        
        # Step 2: List tools
        tools_response = test_client.post("/mcp/tools/list", json={})
        assert tools_response.status_code == 200
        tools_data = tools_response.json()
        
        # Verify natal chart tool is available
        tool_names = [tool["name"] for tool in tools_data["tools"]]
        assert "generate_natal_chart" in tool_names
        
        # Step 3: Call natal chart tool
        with patch('app.services.chart_service.ChartService._convert_immanuel_chart') as mock_convert:
            mock_chart_data = {
                "chart_type": "natal",
                "date_time": "1990-05-15 14:30:00",
                "coordinates": {"latitude": "32n43", "longitude": "117w09"},
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
                    }
                ],
                "houses": [
                    {"number": 1, "cusp": 0.0, "sign": "aries"}
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
                "metadata": {"generated_at": "2024-01-01T12:00:00"}
            }
            
            from app.models.astrology import ChartData
            mock_convert.return_value = ChartData(**mock_chart_data)
            
            tool_call_request = {
                "name": "generate_natal_chart",
                "arguments": {
                    "date_time": "1990-05-15 14:30:00",
                    "latitude": "32n43",
                    "longitude": "117w09",
                    "timezone": "America/Los_Angeles",
                    "house_system": "placidus"
                }
            }
            
            tool_response = test_client.post("/mcp/tools/call", json=tool_call_request)
            assert tool_response.status_code == 200
            
            result_data = tool_response.json()
            assert result_data["result"]["isError"] is False
            assert "data" in result_data["result"]["content"][0]
    
    def test_full_synastry_workflow(
        self, 
        test_client: TestClient,
        sample_synastry_request: Dict[str, Any],
        mock_immanuel: MagicMock
    ) -> None:
        """Test complete synastry analysis workflow."""
        with patch('app.services.chart_service.ChartService.generate_natal_chart') as mock_natal, \
             patch('app.services.chart_service.ChartService.generate_composite_chart') as mock_composite, \
             patch('app.services.chart_service.ChartService._calculate_interaspects') as mock_aspects, \
             patch('app.services.chart_service.ChartService._calculate_compatibility_score') as mock_score:
            
            # Mock chart data
            from app.models.astrology import ChartData, GeographicCoordinate
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
            mock_score.return_value = 85.0
            
            tool_call_request = {
                "name": "calculate_synastry",
                "arguments": sample_synastry_request
            }
            
            response = test_client.post("/mcp/tools/call", json=tool_call_request)
            assert response.status_code == 200
            
            result_data = response.json()
            assert result_data["result"]["isError"] is False
    
    def test_resource_access_workflow(self, test_client: TestClient) -> None:
        """Test complete resource access workflow."""
        # Step 1: List resources
        resources_response = test_client.post("/mcp/resources/list", json={})
        assert resources_response.status_code == 200
        
        resources_data = resources_response.json()
        resource_uris = [resource["uri"] for resource in resources_data["resources"]]
        
        # Step 2: Access each resource
        for uri in resource_uris:
            read_request = {"uri": uri}
            read_response = test_client.post("/mcp/resources/read", json=read_request)
            assert read_response.status_code == 200
            
            read_data = read_response.json()
            assert "contents" in read_data
            assert len(read_data["contents"]) > 0
    
    def test_prompt_generation_workflow(self, test_client: TestClient) -> None:
        """Test complete prompt generation workflow."""
        # Step 1: List prompts
        prompts_response = test_client.post("/mcp/prompts/list", json={})
        assert prompts_response.status_code == 200
        
        prompts_data = prompts_response.json()
        prompt_names = [prompt["name"] for prompt in prompts_data["prompts"]]
        
        # Step 2: Generate prompts
        for prompt_name in prompt_names:
            prompt_request = {
                "name": prompt_name,
                "arguments": self._get_sample_prompt_arguments(prompt_name)
            }
            
            prompt_response = test_client.post("/mcp/prompts/get", json=prompt_request)
            assert prompt_response.status_code == 200
            
            prompt_data = prompt_response.json()
            assert "messages" in prompt_data
            assert len(prompt_data["messages"]) > 0
    
    def test_jsonrpc_full_workflow(self, test_client: TestClient) -> None:
        """Test complete JSON-RPC workflow."""
        # Test multiple JSON-RPC calls
        requests = [
            {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "tools/list",
                "params": {}
            },
            {
                "jsonrpc": "2.0",
                "id": "2",
                "method": "resources/list",
                "params": {}
            },
            {
                "jsonrpc": "2.0",
                "id": "3",
                "method": "prompts/list",
                "params": {}
            }
        ]
        
        for request in requests:
            response = test_client.post("/mcp/jsonrpc", json=request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["jsonrpc"] == "2.0"
            assert data["id"] == request["id"]
            assert "result" in data
    
    def test_error_handling_integration(self, test_client: TestClient) -> None:
        """Test error handling across the integration."""
        # Test invalid tool call
        invalid_tool_request = {
            "name": "invalid_tool",
            "arguments": {}
        }
        
        response = test_client.post("/mcp/tools/call", json=invalid_tool_request)
        assert response.status_code == 200
        
        result_data = response.json()
        assert result_data["result"]["isError"] is True
        
        # Test invalid resource
        invalid_resource_request = {"uri": "invalid_resource"}
        
        response = test_client.post("/mcp/resources/read", json=invalid_resource_request)
        assert response.status_code == 404
        
        # Test invalid prompt
        invalid_prompt_request = {
            "name": "invalid_prompt",
            "arguments": {}
        }
        
        response = test_client.post("/mcp/prompts/get", json=invalid_prompt_request)
        assert response.status_code == 404
    
    def test_validation_integration(self, test_client: TestClient) -> None:
        """Test input validation across the integration."""
        # Test invalid natal chart data
        invalid_chart_request = {
            "name": "generate_natal_chart",
            "arguments": {
                "date_time": "invalid-date",
                "latitude": "invalid-lat",
                "longitude": "invalid-lon"
            }
        }
        
        response = test_client.post("/mcp/tools/call", json=invalid_chart_request)
        assert response.status_code == 200
        
        result_data = response.json()
        assert result_data["result"]["isError"] is True
    
    def test_concurrent_requests(self, test_client: TestClient) -> None:
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request() -> int:
            response = test_client.post("/mcp/tools/list", json={})
            return response.status_code
        
        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    def _get_sample_prompt_arguments(self, prompt_name: str) -> Dict[str, Any]:
        """Get sample arguments for different prompt types."""
        sample_chart_data = {
            "chart_type": "natal",
            "date_time": "1990-05-15 14:30:00",
            "coordinates": {"latitude": "32n43", "longitude": "117w09"},
            "timezone": "UTC",
            "house_system": "placidus",
            "planets": [],
            "houses": [],
            "aspects": [],
            "metadata": {}
        }
        
        arguments_map = {
            "natal_chart_interpretation": {
                "chart_data": sample_chart_data,
                "focus_areas": ["personality"],
                "detail_level": "medium"
            },
            "transit_report": {
                "natal_chart": sample_chart_data,
                "transit_data": {"transits": []},
                "time_period": "current"
            },
            "compatibility_analysis": {
                "synastry_data": {
                    "person1_chart": sample_chart_data,
                    "person2_chart": sample_chart_data,
                    "interaspects": [],
                    "compatibility_score": 75.0
                },
                "relationship_type": "romantic"
            },
            "progression_forecast": {
                "progressed_chart": sample_chart_data,
                "natal_chart": sample_chart_data,
                "time_frame": "year ahead"
            }
        }
        
        return arguments_map.get(prompt_name, {})


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance aspects of the integration."""
    
    def test_response_time_benchmarks(self, test_client: TestClient) -> None:
        """Test response time benchmarks for key endpoints."""
        import time
        
        endpoints_to_test = [
            ("/mcp/tools/list", {}),
            ("/mcp/resources/list", {}),
            ("/mcp/prompts/list", {}),
        ]
        
        for endpoint, payload in endpoints_to_test:
            start_time = time.time()
            response = test_client.post(endpoint, json=payload)
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            
            # Response should be under 1 second for list operations
            assert response_time < 1.0, f"Endpoint {endpoint} took {response_time:.2f}s"
    
    def test_memory_usage_stability(self, test_client: TestClient) -> None:
        """Test that memory usage remains stable under load."""
        import gc
        import sys
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Make multiple requests
        for _ in range(50):
            response = test_client.post("/mcp/tools/list", json={})
            assert response.status_code == 200
        
        # Check memory usage after requests
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count shouldn't grow significantly
        growth_ratio = final_objects / initial_objects
        assert growth_ratio < 1.5, f"Memory usage grew by {growth_ratio:.2f}x"