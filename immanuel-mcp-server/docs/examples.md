# Usage Examples

Practical examples for using the Immanuel MCP Server.

## Getting Started

These examples assume the server is running on `http://localhost:8000`.

## Basic Chart Generation

### Generate a Natal Chart

```python
import requests

# Basic natal chart generation
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "generate_natal_chart",
    "arguments": {
        "date_time": "1990-05-15 14:30:00",
        "latitude": "32n43",
        "longitude": "117w09",
        "timezone": "America/Los_Angeles",
        "house_system": "placidus"
    }
})

chart_data = response.json()["result"]["content"][0]["data"]
print(f"Generated chart with {len(chart_data['planets'])} planets")
```

### Using Decimal Coordinates

```python
# Using decimal degree coordinates
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "generate_natal_chart",
    "arguments": {
        "date_time": "1985-12-25 18:45:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "house_system": "koch",
        "objects": ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
    }
})
```

## Advanced Chart Types

### Progressive Chart

```python
# First, get a natal chart
natal_response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "generate_natal_chart",
    "arguments": {
        "date_time": "1990-05-15 14:30:00",
        "latitude": "32n43",
        "longitude": "117w09"
    }
})

natal_chart = natal_response.json()["result"]["content"][0]["data"]

# Generate progressed chart
progressed_response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "generate_progressed_chart",
    "arguments": {
        "natal_chart": natal_chart,
        "progression_date": "2024-05-15 14:30:00",
        "house_system": "placidus"
    }
})
```

### Solar Return Chart

```python
# Solar return for 2024
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "generate_solar_return",
    "arguments": {
        "birth_data": {
            "date_time": "1990-05-15 14:30:00",
            "coordinates": {
                "latitude": "32n43",
                "longitude": "117w09"
            },
            "timezone": "America/Los_Angeles"
        },
        "return_year": 2024,
        "return_location": {
            "latitude": "40n45",
            "longitude": "73w59"
        }
    }
})
```

## Relationship Analysis

### Synastry Calculation

```python
# Synastry between two people
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "calculate_synastry",
    "arguments": {
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
        },
        "aspect_orbs": {
            "conjunction": 8.0,
            "opposition": 8.0,
            "trine": 6.0,
            "square": 6.0,
            "sextile": 4.0
        }
    }
})

synastry = response.json()["result"]["content"][0]["data"]
print(f"Compatibility score: {synastry['compatibility_score']}")
print(f"Number of aspects: {len(synastry['interaspects'])}")
```

### Composite Chart

```python
# Generate composite chart
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "generate_composite_chart",
    "arguments": {
        "person1": {
            "date_time": "1990-05-15 14:30:00",
            "coordinates": {
                "latitude": "32n43",
                "longitude": "117w09"
            }
        },
        "person2": {
            "date_time": "1992-08-22 10:15:00",
            "coordinates": {
                "latitude": "40n45",
                "longitude": "73w59"
            }
        },
        "house_system": "equal"
    }
})
```

## Transit Analysis

### Current Transits

```python
# Get current transits to natal chart
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "get_transits",
    "arguments": {
        "natal_chart": natal_chart,  # From previous example
        "transit_date": "2024-01-01 12:00:00",
        "objects": ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    }
})

transits = response.json()["result"]["content"][0]["data"]["transits"]
print(f"Found {len(transits)} active transits")
```

## Interpretations

### Aspect Interpretation

```python
# Interpret aspects in a chart
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "interpret_aspects",
    "arguments": {
        "chart_data": chart_data,  # From previous example
        "aspect_types": ["conjunction", "opposition", "trine", "square"],
        "detail_level": "detailed"
    }
})

interpretation = response.json()["result"]["content"][0]["data"]
print(f"Summary: {interpretation['summary']}")
for analysis in interpretation['detailed_analysis']:
    print(f"- {analysis}")
```

### Essential Dignities

```python
# Calculate planetary dignities
response = requests.post("http://localhost:8000/mcp/tools/call", json={
    "name": "calculate_dignities",
    "arguments": {
        "chart_data": chart_data
    }
})

dignities = response.json()["result"]["content"][0]["data"]["dignities"]
for dignity in dignities:
    print(f"{dignity['planet']} in {dignity['sign']}: {dignity['total_score']} points")
```

## Resource Access

### Get Astrological Objects

```python
# List available astrological objects
response = requests.post("http://localhost:8000/mcp/resources/read", json={
    "uri": "astrological_objects"
})

objects = response.json()["contents"][0]["text"]
print(f"Available objects: {objects}")
```

### House Systems Information

```python
# Get house systems information
response = requests.post("http://localhost:8000/mcp/resources/read", json={
    "uri": "house_systems"
})

systems = response.json()["contents"][0]["text"]
print(f"Available house systems: {systems}")
```

## Prompt Usage

### Natal Chart Interpretation Prompt

```python
# Generate interpretation prompt
response = requests.post("http://localhost:8000/mcp/prompts/get", json={
    "name": "natal_chart_interpretation",
    "arguments": {
        "chart_data": chart_data,
        "focus_areas": ["personality", "career", "relationships"],
        "detail_level": "detailed"
    }
})

prompt = response.json()["messages"][0]["content"]["text"]
print("Generated prompt for AI interpretation:")
print(prompt)
```

### Transit Report Prompt

```python
# Generate transit report prompt
response = requests.post("http://localhost:8000/mcp/prompts/get", json={
    "name": "transit_report",
    "arguments": {
        "natal_chart": natal_chart,
        "transit_data": {"transits": transits},
        "time_period": "next 3 months"
    }
})
```

## Error Handling

### Handling Validation Errors

```python
try:
    response = requests.post("http://localhost:8000/mcp/tools/call", json={
        "name": "generate_natal_chart",
        "arguments": {
            "date_time": "invalid-date",
            "latitude": "invalid",
            "longitude": "invalid"
        }
    })
    
    result = response.json()
    if result["result"]["isError"]:
        print(f"Tool error: {result['result']['content'][0]['text']}")
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### Custom Error Handling

```python
def safe_chart_generation(date_time, latitude, longitude, **kwargs):
    """Safely generate a chart with error handling."""
    try:
        response = requests.post("http://localhost:8000/mcp/tools/call", json={
            "name": "generate_natal_chart",
            "arguments": {
                "date_time": date_time,
                "latitude": latitude,
                "longitude": longitude,
                **kwargs
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if not result["result"]["isError"]:
                return result["result"]["content"][0]["data"]
            else:
                print(f"Chart generation failed: {result['result']['content'][0]['text']}")
                return None
        else:
            print(f"HTTP error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
chart = safe_chart_generation(
    "1990-05-15 14:30:00",
    "32n43",
    "117w09",
    timezone="America/Los_Angeles"
)
```

## Batch Processing

### Multiple Chart Generation

```python
birth_data = [
    {"date_time": "1990-05-15 14:30:00", "lat": "32n43", "lon": "117w09"},
    {"date_time": "1985-12-25 18:45:00", "lat": "40n45", "lon": "73w59"},
    {"date_time": "1995-03-10 09:20:00", "lat": "34n03", "lon": "118w15"}
]

charts = []
for data in birth_data:
    chart = safe_chart_generation(
        data["date_time"],
        data["lat"],
        data["lon"]
    )
    if chart:
        charts.append(chart)

print(f"Generated {len(charts)} charts successfully")
```

### Batch Synastry Analysis

```python
def analyze_group_compatibility(birth_data_list):
    """Analyze compatibility between all pairs in a group."""
    results = []
    
    for i in range(len(birth_data_list)):
        for j in range(i + 1, len(birth_data_list)):
            person1 = birth_data_list[i]
            person2 = birth_data_list[j]
            
            response = requests.post("http://localhost:8000/mcp/tools/call", json={
                "name": "calculate_synastry",
                "arguments": {
                    "person1": person1,
                    "person2": person2
                }
            })
            
            if response.status_code == 200:
                result = response.json()
                if not result["result"]["isError"]:
                    synastry = result["result"]["content"][0]["data"]
                    results.append({
                        "person1": i,
                        "person2": j,
                        "compatibility": synastry["compatibility_score"]
                    })
    
    return sorted(results, key=lambda x: x["compatibility"], reverse=True)

# Find most compatible pairs
compatibility_results = analyze_group_compatibility(birth_data)
```

## WebSocket Integration (Future)

```python
# Example of how WebSocket integration might work
import asyncio
import websockets
import json

async def mcp_websocket_client():
    uri = "ws://localhost:8000/mcp/ws"
    
    async with websockets.connect(uri) as websocket:
        # Initialize
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "python-client", "version": "1.0.0"}
            }
        }))
        
        response = await websocket.recv()
        print(f"Initialized: {response}")
        
        # Generate chart
        await websocket.send(json.dumps({
            "jsonrpc": "2.0", 
            "id": "2",
            "method": "tools/call",
            "params": {
                "name": "generate_natal_chart",
                "arguments": {
                    "date_time": "1990-05-15 14:30:00",
                    "latitude": "32n43",
                    "longitude": "117w09"
                }
            }
        }))
        
        chart_response = await websocket.recv()
        print(f"Chart: {chart_response}")

# asyncio.run(mcp_websocket_client())
```

## Performance Tips

### Efficient Chart Processing

```python
# Reuse coordinate objects
from typing import Dict, Any

def create_coordinates(lat: str, lon: str) -> Dict[str, Any]:
    """Create reusable coordinate object."""
    return {"latitude": lat, "longitude": lon}

# Cache frequently used locations
LOCATIONS = {
    "new_york": create_coordinates("40n45", "73w59"),
    "los_angeles": create_coordinates("34n03", "118w15"),
    "london": create_coordinates("51n30", "0w10")
}

# Use consistent house systems for batch processing
HOUSE_SYSTEM = "placidus"

def efficient_chart_generation(date_time: str, location_key: str):
    """Generate chart efficiently using cached data."""
    return safe_chart_generation(
        date_time,
        LOCATIONS[location_key]["latitude"],
        LOCATIONS[location_key]["longitude"],
        house_system=HOUSE_SYSTEM
    )
```

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create session with connection pooling
session = requests.Session()

# Configure retries
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Use session for all requests
def generate_chart_with_session(date_time, latitude, longitude):
    response = session.post("http://localhost:8000/mcp/tools/call", json={
        "name": "generate_natal_chart",
        "arguments": {
            "date_time": date_time,
            "latitude": latitude,
            "longitude": longitude
        }
    })
    return response.json()
```