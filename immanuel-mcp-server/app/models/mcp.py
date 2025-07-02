"""
MCP (Model Context Protocol) data models and schemas.

This module defines the Pydantic models for MCP protocol communication,
including requests, responses, and data structures as per MCP specification.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class MCPProtocolVersion(str, Enum):
    """Supported MCP protocol versions."""
    V1 = "2024-11-05"


class ToolParameterType(str, Enum):
    """Supported parameter types for MCP tools."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class MCPError(BaseModel):
    """MCP protocol error model."""
    model_config = ConfigDict(extra="forbid")
    
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class ServerCapabilities(BaseModel):
    """Server capabilities for MCP initialization."""
    model_config = ConfigDict(extra="forbid")
    
    experimental: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"listChanged": True})
    resources: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"subscribe": True})
    tools: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"listChanged": True})


class ClientCapabilities(BaseModel):
    """Client capabilities received during initialization."""
    model_config = ConfigDict(extra="forbid")
    
    experimental: Optional[Dict[str, Any]] = None
    roots: Optional[List[Dict[str, Any]]] = None
    sampling: Optional[Dict[str, Any]] = None


class InitializeRequest(BaseModel):
    """MCP initialize request."""
    model_config = ConfigDict(extra="forbid")
    
    protocolVersion: MCPProtocolVersion
    capabilities: ClientCapabilities
    clientInfo: Dict[str, str]


class InitializeResponse(BaseModel):
    """MCP initialize response."""
    model_config = ConfigDict(extra="forbid")
    
    protocolVersion: MCPProtocolVersion
    capabilities: ServerCapabilities
    serverInfo: Dict[str, str]
    instructions: Optional[str] = None


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    model_config = ConfigDict(extra="forbid")
    
    type: ToolParameterType
    description: str
    required: Optional[bool] = True
    enum: Optional[List[str]] = None
    properties: Optional[Dict[str, "ToolParameter"]] = None
    items: Optional["ToolParameter"] = None


class Tool(BaseModel):
    """MCP tool definition."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ToolsListRequest(BaseModel):
    """Request to list available tools."""
    model_config = ConfigDict(extra="forbid")
    
    cursor: Optional[str] = None


class ToolsListResponse(BaseModel):
    """Response containing list of available tools."""
    model_config = ConfigDict(extra="forbid")
    
    tools: List[Tool]
    nextCursor: Optional[str] = None


class ToolCallRequest(BaseModel):
    """Request to call a specific tool."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Result from tool execution."""
    model_config = ConfigDict(extra="forbid")
    
    content: List[Dict[str, Any]]
    isError: Optional[bool] = False


class ToolCallResponse(BaseModel):
    """Response from tool call."""
    model_config = ConfigDict(extra="forbid")
    
    result: ToolResult


class Resource(BaseModel):
    """MCP resource definition."""
    model_config = ConfigDict(extra="forbid")
    
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class ResourcesListRequest(BaseModel):
    """Request to list available resources."""
    model_config = ConfigDict(extra="forbid")
    
    cursor: Optional[str] = None


class ResourcesListResponse(BaseModel):
    """Response containing list of available resources."""
    model_config = ConfigDict(extra="forbid")
    
    resources: List[Resource]
    nextCursor: Optional[str] = None


class ResourceContent(BaseModel):
    """Content of a resource."""
    model_config = ConfigDict(extra="forbid")
    
    uri: str
    mimeType: str
    text: Optional[str] = None
    blob: Optional[str] = None


class ResourceReadRequest(BaseModel):
    """Request to read a specific resource."""
    model_config = ConfigDict(extra="forbid")
    
    uri: str


class ResourceReadResponse(BaseModel):
    """Response containing resource contents."""
    model_config = ConfigDict(extra="forbid")
    
    contents: List[ResourceContent]


class PromptArgument(BaseModel):
    """Prompt argument definition."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    description: str
    required: Optional[bool] = True


class Prompt(BaseModel):
    """MCP prompt definition."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    description: str
    arguments: Optional[List[PromptArgument]] = None


class PromptsListRequest(BaseModel):
    """Request to list available prompts."""
    model_config = ConfigDict(extra="forbid")
    
    cursor: Optional[str] = None


class PromptsListResponse(BaseModel):
    """Response containing list of available prompts."""
    model_config = ConfigDict(extra="forbid")
    
    prompts: List[Prompt]
    nextCursor: Optional[str] = None


class PromptMessage(BaseModel):
    """Message in prompt response."""
    model_config = ConfigDict(extra="forbid")
    
    role: str
    content: Dict[str, Any]


class PromptGetRequest(BaseModel):
    """Request to get a prompt with arguments."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    arguments: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PromptGetResponse(BaseModel):
    """Response containing formatted prompt."""
    model_config = ConfigDict(extra="forbid")
    
    description: Optional[str] = None
    messages: List[PromptMessage]


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request wrapper."""
    model_config = ConfigDict(extra="forbid")
    
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response wrapper."""
    model_config = ConfigDict(extra="forbid")
    
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[MCPError] = None


class LoggingLevel(str, Enum):
    """Logging levels."""
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"


class LogEntry(BaseModel):
    """Log entry for MCP logging."""
    model_config = ConfigDict(extra="forbid")
    
    level: LoggingLevel
    data: Any
    logger: Optional[str] = None