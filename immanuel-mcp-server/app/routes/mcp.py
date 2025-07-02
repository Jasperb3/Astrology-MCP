"""
MCP protocol routes for the Immanuel MCP Server.

This module implements all MCP endpoints including initialization,
tools, resources, and prompts.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.config import get_settings, Settings
from app.models.mcp import (
    InitializeRequest,
    InitializeResponse,
    ToolsListRequest,
    ToolsListResponse,
    ToolCallRequest,
    ToolCallResponse,
    ToolResult,
    ResourcesListRequest,
    ResourcesListResponse,
    ResourceReadRequest,
    ResourceReadResponse,
    ResourceContent,
    PromptsListRequest,
    PromptsListResponse,
    PromptGetRequest,
    PromptGetResponse,
    JSONRPCRequest,
    JSONRPCResponse,
    MCPError,
    MCPProtocolVersion
)
from app.models.astrology import (
    NatalChartRequest,
    ProgressedChartRequest,
    SolarReturnRequest,
    CompositeChartRequest,
    SynastryRequest,
    TransitsRequest
)
from app.services.mcp_service import MCPService
from app.services.chart_service import ChartService
from app.services.validation import ValidationService
from app.utils.logging import get_logger
from app.utils.exceptions import (
    ImmanuelMCPError,
    ToolNotFoundError,
    ResourceNotFoundError,
    PromptNotFoundError,
    MCPProtocolError,
    ValidationError
)

logger = get_logger(__name__)
router = APIRouter()

# Service instances
mcp_service = MCPService()
chart_service = ChartService()
validation_service = ValidationService()


@router.post("/initialize", response_model=InitializeResponse)
async def initialize_mcp(
    request: InitializeRequest,
    settings: Settings = Depends(get_settings)
) -> InitializeResponse:
    """Initialize MCP connection and return server capabilities."""
    logger.info("MCP initialization requested", client_info=request.clientInfo)
    
    try:
        # Validate protocol version
        if request.protocolVersion != MCPProtocolVersion.V1:
            raise MCPProtocolError(f"Unsupported protocol version: {request.protocolVersion}")
        
        # Get server capabilities
        capabilities = mcp_service.get_server_capabilities()
        
        # Build server info
        server_info = {
            "name": settings.mcp_server_name,
            "version": settings.mcp_server_version
        }
        
        response = InitializeResponse(
            protocolVersion=MCPProtocolVersion.V1,
            capabilities=capabilities,
            serverInfo=server_info,
            instructions="Welcome to the Immanuel MCP Server! Use the available tools to generate astrological charts and calculations."
        )
        
        logger.info("MCP initialization completed successfully")
        return response
        
    except Exception as e:
        logger.error("MCP initialization failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@router.post("/tools/list", response_model=ToolsListResponse)
async def list_tools(request: ToolsListRequest = ToolsListRequest()) -> ToolsListResponse:
    """List all available astrological tools."""
    logger.info("Tools list requested", cursor=request.cursor)
    
    try:
        tools = mcp_service.list_tools(request.cursor)
        
        response = ToolsListResponse(
            tools=tools,
            nextCursor=None  # No pagination for now
        )
        
        logger.info("Tools list provided", count=len(tools))
        return response
        
    except Exception as e:
        logger.error("Failed to list tools", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """Execute an astrological tool."""
    logger.info("Tool call requested", tool_name=request.name, arguments_keys=list(request.arguments.keys()))
    
    try:
        # Validate tool exists
        tool = mcp_service.get_tool(request.name)
        
        # Sanitize and validate arguments
        sanitized_args = validation_service.sanitize_input(request.arguments)
        validation_service.validate_mcp_tool_arguments(request.name, sanitized_args)
        
        # Execute tool
        result_data = await execute_tool(request.name, sanitized_args)
        
        # Create tool result
        tool_result = ToolResult(
            content=[{
                "type": "text",
                "text": f"Tool '{request.name}' executed successfully",
                "data": result_data
            }],
            isError=False
        )
        
        response = ToolCallResponse(result=tool_result)
        
        logger.info("Tool executed successfully", tool_name=request.name)
        return response
        
    except (ToolNotFoundError, ValidationError) as e:
        logger.warning("Tool call validation failed", tool_name=request.name, error=str(e))
        tool_result = ToolResult(
            content=[{
                "type": "text",
                "text": f"Tool execution failed: {str(e)}"
            }],
            isError=True
        )
        return ToolCallResponse(result=tool_result)
        
    except Exception as e:
        logger.error("Tool execution failed", tool_name=request.name, error=str(e), exc_info=True)
        tool_result = ToolResult(
            content=[{
                "type": "text",
                "text": f"Tool execution failed: {str(e)}"
            }],
            isError=True
        )
        return ToolCallResponse(result=tool_result)


@router.post("/resources/list", response_model=ResourcesListResponse)
async def list_resources(request: ResourcesListRequest = ResourcesListRequest()) -> ResourcesListResponse:
    """List all available astrological resources."""
    logger.info("Resources list requested", cursor=request.cursor)
    
    try:
        resources = mcp_service.list_resources(request.cursor)
        
        response = ResourcesListResponse(
            resources=resources,
            nextCursor=None  # No pagination for now
        )
        
        logger.info("Resources list provided", count=len(resources))
        return response
        
    except Exception as e:
        logger.error("Failed to list resources", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")


@router.post("/resources/read", response_model=ResourceReadResponse)
async def read_resource(request: ResourceReadRequest) -> ResourceReadResponse:
    """Read the contents of a specific resource."""
    logger.info("Resource read requested", uri=request.uri)
    
    try:
        # Get resource content
        content_data = mcp_service.get_resource_content(request.uri)
        
        # Create resource content
        resource_content = ResourceContent(
            uri=request.uri,
            mimeType="application/json",
            text=str(content_data)  # Convert to JSON string
        )
        
        response = ResourceReadResponse(
            contents=[resource_content]
        )
        
        logger.info("Resource content provided", uri=request.uri)
        return response
        
    except ResourceNotFoundError as e:
        logger.warning("Resource not found", uri=request.uri)
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error("Failed to read resource", uri=request.uri, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to read resource: {str(e)}")


@router.post("/prompts/list", response_model=PromptsListResponse)
async def list_prompts(request: PromptsListRequest = PromptsListRequest()) -> PromptsListResponse:
    """List all available astrological prompts."""
    logger.info("Prompts list requested", cursor=request.cursor)
    
    try:
        prompts = mcp_service.list_prompts(request.cursor)
        
        response = PromptsListResponse(
            prompts=prompts,
            nextCursor=None  # No pagination for now
        )
        
        logger.info("Prompts list provided", count=len(prompts))
        return response
        
    except Exception as e:
        logger.error("Failed to list prompts", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {str(e)}")


@router.post("/prompts/get", response_model=PromptGetResponse)
async def get_prompt(request: PromptGetRequest) -> PromptGetResponse:
    """Get a formatted prompt with arguments."""
    logger.info("Prompt requested", name=request.name, arguments_keys=list(request.arguments.keys()) if request.arguments else [])
    
    try:
        # Sanitize arguments
        sanitized_args = validation_service.sanitize_input(request.arguments or {})
        
        # Get prompt content
        messages = mcp_service.get_prompt_content(request.name, sanitized_args)
        
        response = PromptGetResponse(
            description=f"Formatted prompt for {request.name}",
            messages=messages
        )
        
        logger.info("Prompt content provided", name=request.name)
        return response
        
    except PromptNotFoundError as e:
        logger.warning("Prompt not found", name=request.name)
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error("Failed to get prompt", name=request.name, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {str(e)}")


# JSON-RPC endpoints (alternative transport)
@router.post("/jsonrpc", response_model=JSONRPCResponse)
async def jsonrpc_handler(request: JSONRPCRequest) -> JSONRPCResponse:
    """Handle JSON-RPC requests for MCP protocol."""
    logger.info("JSON-RPC request", method=request.method, id=request.id)
    
    try:
        # Route to appropriate handler based on method
        method_handlers = {
            "initialize": handle_jsonrpc_initialize,
            "tools/list": handle_jsonrpc_tools_list,
            "tools/call": handle_jsonrpc_tools_call,
            "resources/list": handle_jsonrpc_resources_list,
            "resources/read": handle_jsonrpc_resources_read,
            "prompts/list": handle_jsonrpc_prompts_list,
            "prompts/get": handle_jsonrpc_prompts_get
        }
        
        handler = method_handlers.get(request.method)
        if not handler:
            raise MCPProtocolError(f"Unknown method: {request.method}")
        
        result = await handler(request.params or {})
        
        return JSONRPCResponse(
            id=request.id,
            result=result
        )
        
    except Exception as e:
        logger.error("JSON-RPC request failed", method=request.method, error=str(e), exc_info=True)
        
        error = MCPError(
            code=-32603,  # Internal error
            message=str(e)
        )
        
        return JSONRPCResponse(
            id=request.id,
            error=error
        )


# Tool execution functions
async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a specific tool with given arguments."""
    tool_executors = {
        "generate_natal_chart": execute_generate_natal_chart,
        "generate_progressed_chart": execute_generate_progressed_chart,
        "generate_solar_return": execute_generate_solar_return,
        "generate_composite_chart": execute_generate_composite_chart,
        "calculate_synastry": execute_calculate_synastry,
        "get_transits": execute_get_transits,
        "interpret_aspects": execute_interpret_aspects,
        "calculate_dignities": execute_calculate_dignities
    }
    
    executor = tool_executors.get(tool_name)
    if not executor:
        raise ToolNotFoundError(tool_name)
    
    return await executor(arguments)


async def execute_generate_natal_chart(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute natal chart generation."""
    request = NatalChartRequest(**arguments)
    chart_data = await chart_service.generate_natal_chart(request)
    return chart_data.model_dump()


async def execute_generate_progressed_chart(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute progressed chart generation."""
    request = ProgressedChartRequest(**arguments)
    chart_data = await chart_service.generate_progressed_chart(request)
    return chart_data.model_dump()


async def execute_generate_solar_return(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute solar return chart generation."""
    request = SolarReturnRequest(**arguments)
    chart_data = await chart_service.generate_solar_return(request)
    return chart_data.model_dump()


async def execute_generate_composite_chart(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute composite chart generation."""
    request = CompositeChartRequest(**arguments)
    chart_data = await chart_service.generate_composite_chart(request)
    return chart_data.model_dump()


async def execute_calculate_synastry(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute synastry calculation."""
    request = SynastryRequest(**arguments)
    synastry_data = await chart_service.calculate_synastry(request)
    return synastry_data.model_dump()


async def execute_get_transits(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute transit calculation."""
    request = TransitsRequest(**arguments)
    transits = await chart_service.get_transits(request)
    return {"transits": [t.model_dump() for t in transits]}


async def execute_interpret_aspects(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute aspect interpretation."""
    from app.models.astrology import ChartData
    
    chart_data = ChartData(**arguments["chart_data"])
    detail_level = arguments.get("detail_level", "medium")
    
    interpretation = await chart_service.interpret_aspects(chart_data, detail_level)
    return interpretation.model_dump()


async def execute_calculate_dignities(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute dignity calculation."""
    from app.models.astrology import ChartData
    
    chart_data = ChartData(**arguments["chart_data"])
    dignities = await chart_service.calculate_dignities(chart_data)
    return {"dignities": [d.model_dump() for d in dignities]}


# JSON-RPC handlers
async def handle_jsonrpc_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC initialize request."""
    request = InitializeRequest(**params)
    response = await initialize_mcp(request)
    return response.model_dump()


async def handle_jsonrpc_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC tools list request."""
    request = ToolsListRequest(**params)
    response = await list_tools(request)
    return response.model_dump()


async def handle_jsonrpc_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC tools call request."""
    request = ToolCallRequest(**params)
    response = await call_tool(request)
    return response.model_dump()


async def handle_jsonrpc_resources_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC resources list request."""
    request = ResourcesListRequest(**params)
    response = await list_resources(request)
    return response.model_dump()


async def handle_jsonrpc_resources_read(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC resources read request."""
    request = ResourceReadRequest(**params)
    response = await read_resource(request)
    return response.model_dump()


async def handle_jsonrpc_prompts_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC prompts list request."""
    request = PromptsListRequest(**params)
    response = await list_prompts(request)
    return response.model_dump()


async def handle_jsonrpc_prompts_get(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC prompts get request."""
    request = PromptGetRequest(**params)
    response = await get_prompt(request)
    return response.model_dump()