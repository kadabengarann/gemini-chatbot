example_endpoint_mappings = {
    "resident details by name": {
        "endpoint": "/residents",
        "method": "GET",
        "parameters": ["name"]
    },
    "resident details by id": {
        "endpoint": "/residents",
        "method": "GET",
        "parameters": ["id"]
    },
    "resident location": {
        "endpoint": "/residents",
        "method": "GET",
        "parameters": ["name"]
    },
    "visitor list for resident": {
        "endpoint": "/residents",
        "method": "GET",
        "parameters": ["name"]
    },
    "visitor appointments": {
        "endpoint": "/visitations",
        "method": "GET",
        "parameters": ["visitorId"]
    },
    "validate visitor access to resident": {
        "endpoint": "/visitor-availability",
        "method": "GET",
        "parameters": ["name"]
    },
    "get resident visitation history": {
        "endpoint": "/visitations",
        "method": "GET",
        "parameters": ["residentId", "date"]
    }
}
