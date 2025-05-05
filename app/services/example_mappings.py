example_endpoint_mappings = {
    "resident information by name": {
        "endpoint": "/residents",
        "method": "GET",
        "parameters": ["name"]
    },
    "resident id by name": {
        "endpoint": "/residents",
        "method": "GET",
        "parameters": ["name"]
    },
    "resident information by id": {
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
    "validate visitor visit access to resident": {
        "endpoint": "/visitor-availability",
        "method": "GET",
        "parameters": ["name"]
    },
    "get resident visitation history": {
        "endpoint": "/visitations",
        "method": "GET",
        "parameters": ["residentId", "date"],
        "depends_on": "resident id by name"
    },
    "visitations count by date": {
        "endpoint": "/visitations-count",
        "method": "GET",
        "parameters": ["date"]
    },
    "checked-in visitations count by date": {
        "endpoint": "/visitations-count",
        "method": "GET",
        "parameters": ["date", "isCheckedIn"]
    },
    "total visitation count in date range": {
        "endpoint": "/visitations-count",
        "method": "GET",
        "parameters": ["startDate", "endDate"]
    },
    "checked-in visitation count in date range": {
        "endpoint": "/visitations-count",
        "method": "GET",
        "parameters": ["startDate", "endDate", "isCheckedIn"]
    },
    "average visitation count over range": {
        "endpoint": "/visitations-average-count",
        "method": "GET",
        "parameters": ["startDate", "endDate"]
    },
    "visitation distribution across time blocks": {
        "endpoint": "/visitations-time-distribution",
        "method": "GET",
        "parameters": ["startDate", "endDate"]
    }
}
