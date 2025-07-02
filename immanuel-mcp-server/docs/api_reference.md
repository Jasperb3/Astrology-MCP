# API Reference

Complete API documentation for the Immanuel MCP Server.

## Overview

The Immanuel MCP Server implements the Model Context Protocol (MCP) v2024-11-05 specification, providing astrological calculation capabilities through standardized JSON-RPC and HTTP endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. In production, consider implementing appropriate authentication and authorization mechanisms.

## MCP Protocol Endpoints

### Initialize Connection

Initialize the MCP connection and exchange capabilities.

**POST** `/mcp/initialize`

#### Request Body

```json
{
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "experimental": {},
    "roots": [],
    "sampling": {}
  },
  "clientInfo": {
    "name": "claude-desktop",
    "version": "1.0.0"
  }
}
```

#### Response

```json
{
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "tools": {"listChanged": true},
    "resources": {"subscribe": true},
    "prompts": {"listChanged": true}
  },
  "serverInfo": {
    "name": "immanuel-astrology",
    "version": "1.0.0"
  },
  "instructions": "Welcome to the Immanuel MCP Server!"
}
```

### List Tools

Get all available astrological tools.

**POST** `/mcp/tools/list`

#### Request Body

```json
{
  "cursor": null
}
```

#### Response

```json
{
  "tools": [
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
            "description": "Latitude in decimal degrees or DMS format"
          },
          "longitude": {
            "type": ["string", "number"],
            "description": "Longitude in decimal degrees or DMS format"
          }
        },
        "required": ["date_time", "latitude", "longitude"]
      }
    }
  ],
  "nextCursor": null
}
```

### Call Tool

Execute a specific astrological tool.

**POST** `/mcp/tools/call`

#### Request Body

```json
{
  "name": "generate_natal_chart",
  "arguments": {
    "date_time": "1990-05-15 14:30:00",
    "latitude": "32n43",
    "longitude": "117w09",
    "timezone": "America/Los_Angeles",
    "house_system": "placidus"
  }
}
```

#### Response

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool 'generate_natal_chart' executed successfully",
        "data": {
          "chart_type": "natal",
          "date_time": "1990-05-15 14:30:00",
          "coordinates": {
            "latitude": "32n43",
            "longitude": "117w09"
          },
          "planets": [...],
          "houses": [...],
          "aspects": [...]
        }
      }
    ],
    "isError": false
  }
}
```

### List Resources

Get all available astrological reference resources.

**POST** `/mcp/resources/list`

#### Response

```json
{
  "resources": [
    {
      "uri": "astrological_objects",
      "name": "Astrological Objects",
      "description": "List of planets, asteroids, and points",
      "mimeType": "application/json"
    }
  ],
  "nextCursor": null
}
```

### Read Resource

Get the content of a specific resource.

**POST** `/mcp/resources/read`

#### Request Body

```json
{
  "uri": "astrological_objects"
}
```

#### Response

```json
{
  "contents": [
    {
      "uri": "astrological_objects",
      "mimeType": "application/json",
      "text": "{\"planets\": [\"sun\", \"moon\", \"mercury\", ...]}"
    }
  ]
}
```

### List Prompts

Get all available prompt templates.

**POST** `/mcp/prompts/list`

#### Response

```json
{
  "prompts": [
    {
      "name": "natal_chart_interpretation",
      "description": "Generate a comprehensive natal chart interpretation",
      "arguments": [
        {
          "name": "chart_data",
          "description": "Complete natal chart data",
          "required": true
        }
      ]
    }
  ],
  "nextCursor": null
}
```

### Get Prompt

Get a formatted prompt with arguments.

**POST** `/mcp/prompts/get`

#### Request Body

```json
{
  "name": "natal_chart_interpretation",
  "arguments": {
    "chart_data": {...},
    "detail_level": "medium"
  }
}
```

#### Response

```json
{
  "description": "Formatted prompt for natal_chart_interpretation",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "Generate a comprehensive natal chart interpretation..."
      }
    }
  ]
}
```

## Tools Reference

### generate_natal_chart

Generate a complete natal chart.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_time` | string | Yes | ISO format datetime |
| `latitude` | string/number | Yes | Latitude in degrees or DMS |
| `longitude` | string/number | Yes | Longitude in degrees or DMS |
| `timezone` | string | No | Timezone identifier |
| `house_system` | string | No | House system (default: placidus) |
| `objects` | array | No | Objects to include |

#### Example

```json
{
  "name": "generate_natal_chart",
  "arguments": {
    "date_time": "1990-05-15 14:30:00",
    "latitude": "32n43",
    "longitude": "117w09",
    "timezone": "America/Los_Angeles",
    "house_system": "placidus",
    "objects": ["sun", "moon", "mercury", "venus", "mars"]
  }
}
```

### generate_progressed_chart

Generate a progressed chart for personal evolution analysis.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `natal_chart` | object | Yes | Reference natal chart data |
| `progression_date` | string | Yes | Date for progression |
| `house_system` | string | No | House system |

### generate_solar_return

Generate a solar return chart for yearly forecasts.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `birth_data` | object | Yes | Original birth data |
| `return_year` | integer | Yes | Year for solar return |
| `return_location` | object | No | Location for return |

### generate_composite_chart

Create a relationship composite chart.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `person1` | object | Yes | First person's birth data |
| `person2` | object | Yes | Second person's birth data |
| `house_system` | string | No | House system |

### calculate_synastry

Perform compatibility analysis between two charts.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `person1` | object | Yes | First person's birth data |
| `person2` | object | Yes | Second person's birth data |
| `aspect_orbs` | object | No | Custom aspect orbs |

### get_transits

Calculate current planetary transits.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `natal_chart` | object | Yes | Reference natal chart |
| `transit_date` | string | Yes | Date for transits |
| `objects` | array | No | Transiting objects |

### interpret_aspects

Get detailed aspect interpretations.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chart_data` | object | Yes | Chart data with aspects |
| `aspect_types` | array | No | Specific aspects to interpret |
| `detail_level` | string | No | Level of detail |

### calculate_dignities

Calculate essential dignities for planets.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chart_data` | object | Yes | Chart data with planets |

## Resources Reference

### astrological_objects

List of available astrological objects.

```json
{
  "planets": ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"],
  "asteroids": ["chiron", "ceres", "pallas", "juno", "vesta"],
  "points": ["north_node", "south_node", "lilith", "part_of_fortune", "vertex"]
}
```

### house_systems

Available house calculation systems.

```json
{
  "systems": ["placidus", "koch", "equal", "whole_sign", "porphyrius", "regiomontanus"],
  "descriptions": {
    "placidus": "Most popular system, uses time-based division",
    "koch": "Birthplace system, focuses on birthplace coordinates"
  }
}
```

### aspect_patterns

Supported aspect types and orbs.

```json
{
  "major_aspects": {
    "conjunction": {"degrees": 0, "orb": 8.0, "nature": "neutral"},
    "opposition": {"degrees": 180, "orb": 8.0, "nature": "challenging"},
    "trine": {"degrees": 120, "orb": 8.0, "nature": "harmonious"}
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": "ValidationError",
  "message": "Invalid datetime format",
  "details": {
    "field": "date_time",
    "value": "invalid-date"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Tool/resource/prompt not found |
| 422 | Unprocessable Entity - Chart generation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limiting

Default rate limits:
- 100 requests per minute per IP
- Configurable via environment variables

## JSON-RPC Support

All MCP endpoints are also available via JSON-RPC 2.0:

**POST** `/mcp/jsonrpc`

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/list",
  "params": {}
}
```

## Health Endpoints

### Health Check

**GET** `/health/`

### Readiness Check

**GET** `/health/ready`

### Liveness Check

**GET** `/health/liveness`

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`