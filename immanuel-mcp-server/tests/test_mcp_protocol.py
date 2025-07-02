"""
Tests for MCP protocol compliance and functionality.

This module tests the MCP protocol implementation including
initialization, tools, resources, and prompts.
"""

import pytest
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from app.services.mcp_service import MCPService
from app.models.mcp import (
    InitializeRequest,
    ToolsListRequest,
    ToolCallRequest,
    ResourcesListRequest,
    ResourceReadRequest,
    PromptsListRequest,
    PromptGetRequest
)
from app.utils.exceptions import ToolNotFoundError, ResourceNotFoundError, PromptNotFoundError


@pytest.mark.unit
class TestMCPService:
    """Test MCP service functionality."""
    
    def test_mcp_service_initialization(self, mcp_service: MCPService) -> None:
        """Test MCP service initializes correctly."""
        assert mcp_service is not None
        assert len(mcp_service._tools) > 0
        assert len(mcp_service._resources) > 0
        assert len(mcp_service._prompts) > 0
    
    def test_get_server_capabilities(self, mcp_service: MCPService) -> None:
        """Test server capabilities response."""
        capabilities = mcp_service.get_server_capabilities()
        
        assert capabilities.tools is not None
        assert capabilities.resources is not None
        assert capabilities.prompts is not None
    
    def test_list_tools(self, mcp_service: MCPService) -> None:
        """Test listing available tools."""
        tools = mcp_service.list_tools()
        
        assert len(tools) > 0
        
        # Check for required tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "generate_natal_chart",
            "generate_progressed_chart",
            "generate_solar_return",
            "generate_composite_chart",
            "calculate_synastry",
            "get_transits",
            "interpret_aspects",
            "calculate_dignities"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_get_tool_success(self, mcp_service: MCPService) -> None:
        """Test getting a specific tool."""
        tool = mcp_service.get_tool("generate_natal_chart")
        
        assert tool.name == "generate_natal_chart"
        assert tool.description is not None
        assert tool.inputSchema is not None
    
    def test_get_tool_not_found(self, mcp_service: MCPService) -> None:
        """Test getting a non-existent tool."""
        with pytest.raises(ToolNotFoundError):
            mcp_service.get_tool("non_existent_tool")
    
    def test_list_resources(self, mcp_service: MCPService) -> None:
        """Test listing available resources."""
        resources = mcp_service.list_resources()
        
        assert len(resources) > 0
        
        # Check for required resources
        resource_uris = [resource.uri for resource in resources]
        expected_resources = [
            "astrological_objects",
            "house_systems",
            "aspect_patterns",
            "sign_meanings",
            "planet_meanings",
            "house_meanings"
        ]
        
        for expected_resource in expected_resources:
            assert expected_resource in resource_uris
    
    def test_get_resource_content_success(self, mcp_service: MCPService) -> None:
        """Test getting resource content."""
        content = mcp_service.get_resource_content("astrological_objects")
        
        assert isinstance(content, dict)
        assert "planets" in content
        assert "asteroids" in content
    
    def test_get_resource_content_not_found(self, mcp_service: MCPService) -> None:
        """Test getting non-existent resource content."""
        with pytest.raises(ResourceNotFoundError):
            mcp_service.get_resource_content("non_existent_resource")
    
    def test_list_prompts(self, mcp_service: MCPService) -> None:
        """Test listing available prompts."""
        prompts = mcp_service.list_prompts()
        
        assert len(prompts) > 0
        
        # Check for required prompts
        prompt_names = [prompt.name for prompt in prompts]
        expected_prompts = [
            "natal_chart_interpretation",
            "transit_report",
            "compatibility_analysis",
            "progression_forecast"
        ]
        
        for expected_prompt in expected_prompts:
            assert expected_prompt in prompt_names
    
    def test_get_prompt_content_success(self, mcp_service: MCPService) -> None:
        """Test getting prompt content."""
        arguments = {
            "chart_data": {"test": "data"},
            "focus_areas": ["personality"],
            "detail_level": "medium"
        }
        
        messages = mcp_service.get_prompt_content("natal_chart_interpretation", arguments)
        
        assert isinstance(messages, list)
        assert len(messages) > 0
        assert messages[0].role == "user"
    
    def test_get_prompt_content_not_found(self, mcp_service: MCPService) -> None:
        """Test getting non-existent prompt content."""
        with pytest.raises(PromptNotFoundError):
            mcp_service.get_prompt_content("non_existent_prompt", {})


@pytest.mark.integration
class TestMCPEndpoints:
    """Test MCP HTTP endpoints."""
    
    def test_mcp_initialize_success(
        self, 
        test_client: TestClient, 
        sample_mcp_initialize_request: Dict[str, Any]
    ) -> None:
        """Test MCP initialization endpoint."""
        response = test_client.post("/mcp/initialize", json=sample_mcp_initialize_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["protocolVersion"] == "2024-11-05"
        assert "capabilities" in data
        assert "serverInfo" in data
    
    def test_mcp_initialize_invalid_protocol(self, test_client: TestClient) -> None:
        """Test MCP initialization with invalid protocol version."""
        request = {
            "protocolVersion": "invalid-version",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
        
        response = test_client.post("/mcp/initialize", json=request)
        assert response.status_code in [400, 422]  # Validation error
    
    def test_tools_list_endpoint(self, test_client: TestClient) -> None:
        """Test tools list endpoint."""
        response = test_client.post("/mcp/tools/list", json={})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tools" in data
        assert len(data["tools"]) > 0
    
    def test_tools_call_endpoint_success(
        self, 
        test_client: TestClient, 
        sample_tool_call_request: Dict[str, Any]
    ) -> None:
        """Test successful tool call endpoint."""
        with patch('app.routes.mcp.chart_service') as mock_service:
            mock_service.generate_natal_chart.return_value = AsyncMock()
            mock_service.generate_natal_chart.return_value.model_dump.return_value = {"test": "result"}
            
            response = test_client.post("/mcp/tools/call", json=sample_tool_call_request)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "result" in data
            assert data["result"]["isError"] is False
    
    def test_tools_call_endpoint_invalid_tool(self, test_client: TestClient) -> None:
        """Test tool call with invalid tool name."""
        request = {
            "name": "invalid_tool",
            "arguments": {}
        }
        
        response = test_client.post("/mcp/tools/call", json=request)
        
        assert response.status_code == 200  # MCP returns success with error in result
        data = response.json()
        
        assert data["result"]["isError"] is True
    
    def test_resources_list_endpoint(self, test_client: TestClient) -> None:
        """Test resources list endpoint."""
        response = test_client.post("/mcp/resources/list", json={})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "resources" in data
        assert len(data["resources"]) > 0
    
    def test_resources_read_endpoint_success(self, test_client: TestClient) -> None:
        """Test successful resource read endpoint."""
        request = {"uri": "astrological_objects"}
        
        response = test_client.post("/mcp/resources/read", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "contents" in data
        assert len(data["contents"]) > 0
    
    def test_resources_read_endpoint_not_found(self, test_client: TestClient) -> None:
        """Test resource read with non-existent resource."""
        request = {"uri": "non_existent_resource"}
        
        response = test_client.post("/mcp/resources/read", json=request)
        assert response.status_code == 404
    
    def test_prompts_list_endpoint(self, test_client: TestClient) -> None:
        """Test prompts list endpoint."""
        response = test_client.post("/mcp/prompts/list", json={})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "prompts" in data
        assert len(data["prompts"]) > 0
    
    def test_prompts_get_endpoint_success(self, test_client: TestClient) -> None:
        """Test successful prompt get endpoint."""
        request = {
            "name": "natal_chart_interpretation",
            "arguments": {
                "chart_data": {"test": "data"},
                "detail_level": "medium"
            }
        }
        
        response = test_client.post("/mcp/prompts/get", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "messages" in data
        assert len(data["messages"]) > 0
    
    def test_prompts_get_endpoint_not_found(self, test_client: TestClient) -> None:
        """Test prompt get with non-existent prompt."""
        request = {
            "name": "non_existent_prompt",
            "arguments": {}
        }
        
        response = test_client.post("/mcp/prompts/get", json=request)
        assert response.status_code == 404
    
    def test_jsonrpc_endpoint_success(self, test_client: TestClient) -> None:
        """Test JSON-RPC endpoint with valid request."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "tools/list",
            "params": {}
        }
        
        response = test_client.post("/mcp/jsonrpc", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "test-1"
        assert "result" in data
    
    def test_jsonrpc_endpoint_invalid_method(self, test_client: TestClient) -> None:
        """Test JSON-RPC endpoint with invalid method."""
        request = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "invalid/method",
            "params": {}
        }
        
        response = test_client.post("/mcp/jsonrpc", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "test-2"
        assert "error" in data


@pytest.mark.unit
class TestMCPDataModels:
    """Test MCP data model validation."""
    
    def test_initialize_request_validation(self) -> None:
        """Test InitializeRequest validation."""
        valid_data = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"experimental": {}},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
        
        request = InitializeRequest(**valid_data)
        assert request.protocolVersion == "2024-11-05"
    
    def test_tool_call_request_validation(self) -> None:
        """Test ToolCallRequest validation."""
        valid_data = {
            "name": "generate_natal_chart",
            "arguments": {
                "date_time": "1990-05-15 14:30:00",
                "latitude": "32n43",
                "longitude": "117w09"
            }
        }
        
        request = ToolCallRequest(**valid_data)
        assert request.name == "generate_natal_chart"
        assert "date_time" in request.arguments
    
    def test_resource_read_request_validation(self) -> None:
        """Test ResourceReadRequest validation."""
        valid_data = {"uri": "astrological_objects"}
        
        request = ResourceReadRequest(**valid_data)
        assert request.uri == "astrological_objects"
    
    def test_prompt_get_request_validation(self) -> None:
        """Test PromptGetRequest validation."""
        valid_data = {
            "name": "natal_chart_interpretation",
            "arguments": {"chart_data": {}, "detail_level": "medium"}
        }
        
        request = PromptGetRequest(**valid_data)
        assert request.name == "natal_chart_interpretation"
        assert "chart_data" in request.arguments