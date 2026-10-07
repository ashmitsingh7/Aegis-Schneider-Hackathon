"""
Main API for Aegis - AI-Powered Decision Intelligence Platform
Integrates health prediction, RUL estimation, risk assessment, decision optimization, and digital twin simulation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import logging
import pandas as pd
from datetime import datetime

# Import our models
from models.health_model import create_health_model
from models.rul_model import create_rul_model
from models.risk_model import create_risk_model
from decision_engine.optimizer import create_decision_optimizer
from digital_twin.enhanced_transformer import create_enhanced_transformer_simulator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Aegis API",
    description="AI-Powered Decision Intelligence Platform for Critical Electrical Infrastructure",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (singleton pattern)
health_model = create_health_model()
rul_model = create_rul_model()
risk_model = create_risk_model()
decision_optimizer = create_decision_optimizer()
transformer_simulator = create_enhanced_transformer_simulator(
    rating_mva=10.0,
    voltage_rating_kv=23.0,
    temp_rise_limit_c=65.0,
    frequency_hz=60.0,
    impedance_percent=8.0,
    x_over_r_ratio=20.0
)

# Pydantic models for request/response validation
class TelemetryData(BaseModel):
    asset_id: str = "T-01"
    load_percent: float
    voltage_kv: Optional[float] = 23.0
    current_a: Optional[float] = None
    ambient_temp_c: float
    oil_temp_c: Optional[float] = None
    winding_temp_c: Optional[float] = None
    vibration_mm_s: float = 1.0
    operating_hours: Optional[float] = 0.0

class SimulationRequest(BaseModel):
    load_percent: float
    ambient_temp_c: float
    cooling_mode: str = "normal"
    harmonic_distortion_thd: float = 0.05
    hours_at_conditions: float = 1.0
    vibration_rms_mm_s: float = 2.0
    dielectric_stress_factor: float = 1.0
    symmetry_imbalance_percent: float = 0.0
    partial_discharge_detected: bool = False

class HealthResponse(BaseModel):
    asset_id: str
    health_score: float
    failure_probability: float
    estimated_rul_days: int
    risk_level: str
    degradation_type: str
    is_anomaly: bool
    confidence: float

class RULResponse(BaseModel):
    asset_id: str
    rul_hours: float
    rul_days: float
    rul_years: float
    confidence: float
    basis: str
    design_life_hours: int
    percent_life_used: float

class RiskResponse(BaseModel):
    asset_id: str
    overall_risk_score: float
    overall_risk_level: str
    risk_level_numeric: int
    risk_scores: Dict[str, float]
    risk_contributions_percent: Dict[str, float]
    primary_risk_drivers: List[str]
    risk_recommendations: List[str]
    confidence: float
    assessment_timestamp: str
    risk_trend: str
    recommended_action_urgency: str

class DecisionResponse(BaseModel):
    asset_id: str
    recommended_intervention: str
    recommended_intervention_key: str
    intervention_scores: Dict[str, Any]
    optimal_intervention_score: float
    explanation: List[str]
    assessment_details: Dict[str, Any]

class SimulationResponse(BaseModel):
    # Digital twin simulation results
    load_percent: float
    ambient_temp_c: float
    cooling_mode: str
    harmonic_distortion_thd: float
    simulation_hours: float
    vibration_rms_mm_s: float
    dielectric_stress_factor: float
    symmetry_imbalance_percent: float
    partial_discharge_detected: bool

    # Electrical parameters
    rated_current_a: float
    actual_current_a: float
    rated_voltage_kv: float
    actual_voltage_kv: float
    apparent_power_mva: float
    real_power_mw: float
    reactive_power_mvar: float
    power_factor: float
    resistance_ohm: float
    reactance_ohm: float
    impedance_ohm: float
    impedance_percent: float
    voltage_regulation_percent: float

    # Losses breakdown
    no_load_losses_kw: float
    load_losses_kw: float
    total_losses_kw: float
    losses_breakdown: Dict[str, Any]
    harmonic_loss_factors: Dict[str, float]

    # Temperatures
    oil_temp_c: float
    winding_temp_c: float
    hotspot_temp_c: float
    temperature_rise_oil_c: float
    temperature_rise_winding_c: float
    temperature_rise_hotspot_c: float
    hotspot_gradient_c: float
    oil_winding_gradient_c: float

    # Thermal time constants
    thermal_time_constants_hours: Dict[str, float]

    # Efficiency and losses
    efficiency_percent: float
    losses_percent: float

    # Aging and health
    health_impact_per_hour: float
    estimated_remaining_hours: float
    aging_rate_per_hour: float
    design_life_hours: int
    combined_aging_factor: float
    aging_breakdown: Dict[str, float]

    # Risk assessment
    risk_level: str
    risk_level_numeric: int
    risk_confidence: float
    risk_scores: Dict[str, float]
    max_individual_risk: float
    significant_risk_factors: Dict[str, float]

    # Dielectric and insulation
    bil_level_kv: float
    dielectric_stress_actual: float
    partial_discharge_risk: str

    # System parameters
    frequency_hz: float
    rated_mva: float
    voltage_rating_kv: float
    temp_rise_limit_c: float
    impedance_percent: float
    x_over_r_ratio: float

    # Timestamp
    timestamp: str
    simulation_id: str

class SummaryResponse(BaseModel):
    asset_id: str
    health: HealthResponse
    rul: RULResponse
    risk: RiskResponse
    decision: DecisionResponse
    simulation: SimulationResponse
    timestamp: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Aegis AI-Powered Decision Intelligence Platform",
        "version": "1.0.0",
        "description": "Platform for critical electrical infrastructure monitoring and decision support",
        "docs": "/docs",
        "health_check": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "health_model": health_model is not None,
            "rul_model": rul_model is not None,
            "risk_model": risk_model is not None,
            "decision_optimizer": decision_optimizer is not None,
            "transformer_simulator": transformer_simulator is not None
        }
    }


@app.post("/assets/{asset_id}/health", response_model=HealthResponse)
async def get_asset_health(asset_id: str, telemetry: TelemetryData):
    """
    Get asset health assessment
    Returns health score, failure probability, and degradation detection
    """
    try:
        # Override asset_id from path if provided
        telemetry.asset_id = asset_id

        # Get health assessment
        health_result = health_model.predict_health(telemetry.dict())

        return HealthResponse(**health_result)

    except Exception as e:
        logger.error(f"Error in health assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assets/{asset_id}/rul", response_model=RULResponse)
async def get_asset_rul(asset_id: str, telemetry: TelemetryData):
    """
    Get asset Remaining Useful Life prediction
    Returns RUL in hours, days, and years
    """
    try:
        # Override asset_id from path if provided
        telemetry.asset_id = asset_id

        # Get health assessment first (needed for RUL prediction)
        health_result = health_model.predict_health(telemetry.dict())

        # Get RUL prediction
        rul_result = rul_model.predict_rul(telemetry.dict(), health_result)

        return RULResponse(**rul_result)

    except Exception as e:
        logger.error(f"Error in RUL prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assets/{asset_id}/risk", response_model=RiskResponse)
async def get_asset_risk(asset_id: str, telemetry: TelemetryData):
    """
    Get comprehensive asset risk assessment
    Returns detailed risk scores and recommendations
    """
    try:
        # Override asset_id from path if provided
        telemetry.asset_id = asset_id

        # Get supporting assessments
        health_result = health_model.predict_health(telemetry.dict())
        rul_result = rul_model.predict_rul(telemetry.dict(), health_result)

        # Get risk assessment
        risk_result = risk_model.assess_comprehensive_risk(
            telemetry.dict(), health_result, rul_result
        )

        return RiskResponse(**risk_result)

    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assets/{asset_id}/decision", response_model=DecisionResponse)
async def get_asset_decision(asset_id: str, telemetry: TelemetryData):
    """
    Get optimal intervention recommendation
    Returns decision analysis and recommended action
    """
    try:
        # Override asset_id from path if provided
        telemetry.asset_id = asset_id

        # Get supporting assessments
        health_result = health_model.predict_health(telemetry.dict())
        rul_result = rul_model.predict_rul(telemetry.dict(), health_result)
        risk_result = risk_model.assess_comprehensive_risk(
            telemetry.dict(), health_result, rul_result
        )

        # Get digital twin simulation for what-if analysis
        # Use current telemetry as baseline for simulation
        sim_request = SimulationRequest(
            load_percent=telemetry.load_percent,
            ambient_temp_c=telemetry.ambient_temp_c,
            cooling_mode="normal",  # Default
            harmonic_distortion_thd=0.05,
            hours_at_conditions=1.0,
            vibration_rms_mm_s=telemetry.vibration_mm_s,
            dielectric_stress_factor=1.0,
            symmetry_imbalance_percent=0.0,
            partial_discharge_detected=False
        )

        # Run baseline simulation
        simulation_result = transformer_simulator.simulate_enhanced(**sim_request.dict())

        # Get decision recommendation
        decision_result = decision_optimizer.evaluate_interventions(
            telemetry.dict(), health_result, rul_result, risk_result, simulation_result
        )

        return DecisionResponse(**decision_result)

    except Exception as e:
        logger.error(f"Error in decision optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assets/{asset_id}/simulate", response_model=SimulationResponse)
async def simulate_asset(asset_id: str, simulation_request: SimulationRequest):
    """
    Run digital twin simulation for what-if analysis
    Returns comprehensive simulation results
    """
    try:
        # Run the enhanced transformer simulation
        simulation_result = transformer_simulator.simulate_enhanced(
            asset_id=asset_id,
            **simulation_request.dict()
        )

        return SimulationResponse(**simulation_result)

    except Exception as e:
        logger.error(f"Error in simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/assets/{asset_id}/summary", response_model=SummaryResponse)
async def get_asset_summary(asset_id: str):
    """
    Get comprehensive asset summary
    Combines health, RUL, risk, decision, and simulation data
    """
    try:
        # Create default telemetry for summary (in real system, this would come from live data)
        default_telemetry = TelemetryData(
            asset_id=asset_id,
            load_percent=75.0,
            voltage_kv=23.0,
            current_a=188.0,
            ambient_temp_c=30.0,
            oil_temp_c=50.0,
            winding_temp_c=70.0,
            vibration_mm_s=1.5,
            operating_hours=8760 * 5  # 5 years
        )

        # Get all assessments
        health_result = health_model.predict_health(default_telemetry.dict())
        rul_result = rul_model.predict_rul(default_telemetry.dict(), health_result)
        risk_result = risk_model.assess_comprehensive_risk(
            default_telemetry.dict(), health_result, rul_result
        )

        # Run simulation for summary
        sim_request = SimulationRequest(
            load_percent=default_telemetry.load_percent,
            ambient_temp_c=default_telemetry.ambient_temp_c,
            cooling_mode="normal",
            harmonic_distortion_thd=0.05,
            hours_at_conditions=1.0,
            vibration_rms_mm_s=default_telemetry.vibration_mm_s,
            dielectric_stress_factor=1.0,
            symmetry_imbalance_percent=0.0,
            partial_discharge_detected=False
        )
        simulation_result = transformer_simulator.simulate_enhanced(**sim_request.dict())

        # Get decision recommendation
        decision_result = decision_optimizer.evaluate_interventions(
            default_telemetry.dict(), health_result, rul_result, risk_result, simulation_result
        )

        # Combine all results
        summary_result = {
            "asset_id": asset_id,
            "health": health_result,
            "rul": rul_result,
            "risk": risk_result,
            "decision": decision_result,
            "simulation": simulation_result,
            "timestamp": datetime.now().isoformat()
        }

        return SummaryResponse(**summary_result)

    except Exception as e:
        logger.error(f"Error in asset summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/assets/{asset_id}/telemetry")
async def get_asset_telemetry(asset_id: str):
    """
    Get time-series telemetry data for asset
    Returns historical telemetry for trending and analysis
    """
    try:
        # In a real implementation, this would query a time-series database
        # For demo, return mock recent telemetry data

        # Generate some realistic telemetry history
        import random
        from datetime import datetime, timedelta

        base_time = datetime.now() - timedelta(hours=24)
        telemetry_data = []

        for i in range(24):  # Last 24 hours
            timestamp = base_time + timedelta(hours=i)

            # Simulate daily load pattern
            hour_of_day = timestamp.hour
            load_factor = 0.7 + 0.3 * math.sin((hour_of_day - 6) * math.pi / 12)  # Peak at 2PM
            load_factor = max(0.3, min(1.2, load_factor))  # Clamp to reasonable range

            base_load = 70.0
            load_percent = base_load * load_factor

            # Temperature correlates with load
            base_temp = 25.0
            temp_rise = (load_percent - 50) * 0.3  # Rough approximation
            ambient_temp = base_temp + temp_rise * 0.6
            oil_temp = ambient_temp + 20 + (load_percent - 50) * 0.2
            winding_temp = oil_temp + 15 + (load_percent - 50) * 0.15

            telemetry_data.append({
                "timestamp": timestamp.isoformat(),
                "asset_id": asset_id,
                "load_percent": round(load_percent, 1),
                "voltage_kv": round(23.0 + random.uniform(-0.5, 0.5), 1),
                "current_a": round((load_percent / 100.0) * 188, 1),
                "ambient_temp_c": round(ambient_temp, 1),
                "oil_temp_c": round(oil_temp, 1),
                "winding_temp_c": round(winding_temp, 1),
                "vibration_mm_s": round(1.0 + random.uniform(-0.2, 0.5), 1),
                "operating_hours": 8760 * 5 + i  # Incrementally increasing
            })

        return {
            "asset_id": asset_id,
            "telemetry": telemetry_data,
            "count": len(telemetry_data),
            "time_range": {
                "start": telemetry_data[0]["timestamp"],
                "end": telemetry_data[-1]["timestamp"]
            }
        }

    except Exception as e:
        logger.error(f"Error retrieving telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional utility endpoints
@app.get("/models/info")
async def get_models_info():
    """Get information about loaded models"""
    return {
        "health_model": {
            "type": "TransformerHealthModel",
            "trained": health_model.is_trained if hasattr(health_model, 'is_trained') else True,
            "features": len(health_model.feature_names) if hasattr(health_model, 'feature_names') else 8
        },
        "rul_model": {
            "type": "TransformerRULModel",
            "trained": rul_model.is_trained if hasattr(rul_model, 'is_trained') else True,
            "design_life_hours": rul_model.design_life_hours if hasattr(rul_model, 'design_life_hours') else 180000
        },
        "risk_model": {
            "type": "TransformerRiskModel",
            "criteria": list(risk_model.risk_weights.keys()) if hasattr(risk_model, 'risk_weights') else []
        },
        "decision_optimizer": {
            "type": "TransformerDecisionOptimizer",
            "strategies": list(decision_optimizer.intervention_strategies.keys()) if hasattr(decision_optimizer, 'intervention_strategies') else []
        },
        "transformer_simulator": {
            "type": "EnhancedTransformerSimulator",
            "rating_mva": transformer_simulator.rating_mva,
            "voltage_rating_kv": transformer_simulator.voltage_rating_kv
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)