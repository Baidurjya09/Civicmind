"""
CivicMind — Mock API Server (Theme 3.1: Professional Tasks)
FastAPI server with 8 tool endpoints for agents to call.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import random

app = FastAPI(title="CivicMind City API", version="1.0.0")

# Mock state (in production, would connect to real database)
city_state = {
    "budget": 1_000_000,
    "hospital_beds": 500,
    "crime_incidents": 150,
    "power_grid_status": "operational",
    "trust_score": 0.75,
}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CivicMind API"}


@app.get("/city/status")
def get_city_status():
    """Get overall city status"""
    return {
        "population": 10_000,
        "trust_score": city_state["trust_score"],
        "budget": city_state["budget"],
        "status": "operational",
    }


@app.get("/budget/status")
def get_budget_status():
    """Finance tool: Get budget status"""
    return {
        "total_budget": city_state["budget"],
        "allocated": city_state["budget"] * 0.6,
        "remaining": city_state["budget"] * 0.4,
        "debt": 200_000,
    }


@app.get("/hospital/status")
def get_hospital_status():
    """Health tool: Get hospital capacity"""
    return {
        "total_beds": city_state["hospital_beds"],
        "occupied_beds": int(city_state["hospital_beds"] * 0.7),
        "available_beds": int(city_state["hospital_beds"] * 0.3),
        "capacity_utilization": 0.7,
    }


@app.get("/crime/stats")
def get_crime_stats():
    """Police tool: Get crime statistics"""
    return {
        "total_incidents": city_state["crime_incidents"],
        "violent_crimes": int(city_state["crime_incidents"] * 0.2),
        "property_crimes": int(city_state["crime_incidents"] * 0.5),
        "other": int(city_state["crime_incidents"] * 0.3),
        "crime_rate": city_state["crime_incidents"] / 10_000,
    }


@app.get("/infrastructure/grid")
def get_power_grid_status():
    """Infrastructure tool: Power grid status"""
    return {
        "status": city_state["power_grid_status"],
        "capacity": 1000,  # MW
        "current_load": 750,  # MW
        "health_score": 0.85,
        "maintenance_required": False,
    }


@app.get("/media/sentiment")
def get_public_sentiment():
    """Media tool: Public sentiment analysis"""
    return {
        "trust_score": city_state["trust_score"],
        "satisfaction": 0.70,
        "misinformation_level": 0.15,
        "trending_topics": ["healthcare", "economy", "safety"],
    }


@app.get("/citizens/petitions")
def get_citizen_petitions():
    """Media tool: Recent citizen petitions"""
    return {
        "total_petitions": 45,
        "urgent": 8,
        "recent": [
            {"id": 1, "type": "healthcare_access", "urgency": "high"},
            {"id": 2, "type": "crime_safety", "urgency": "medium"},
            {"id": 3, "type": "infrastructure_failure", "urgency": "high"},
        ],
    }


@app.get("/oversight/report")
def get_oversight_report():
    """Oversight tool: Agent behavior report"""
    return {
        "flagged_actions": 2,
        "alignment_score": 0.82,
        "recommendations": [
            "Review recent tax policy decisions",
            "Monitor police deployment strategies",
        ],
    }


@app.post("/action/execute")
def execute_action(action: Dict[str, Any]):
    """Execute a policy action"""
    action_type = action.get("type")
    
    if action_type == "increase_tax":
        city_state["budget"] += 50_000
        city_state["trust_score"] -= 0.03
        return {"success": True, "effect": "Budget +50k, Trust -3%"}
    
    elif action_type == "emergency_budget":
        city_state["budget"] -= 150_000
        city_state["trust_score"] += 0.06
        return {"success": True, "effect": "Budget -150k, Trust +6%"}
    
    else:
        return {"success": False, "error": "Unknown action type"}


def main():
    """Run API server"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
