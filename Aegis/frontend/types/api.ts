/**
 * TypeScript interfaces for Aegis backend API responses
 * These mirror the Pydantic models in the backend/main.py file
 */

export interface HealthResponse {
  asset_id: string;
  health_score: float;
  failure_probability: float;
  estimated_rul_days: int;
  risk_level: string;
  degradation_type: string;
  is_anomaly: boolean;
  confidence: float;
}

export interface RULResponse {
  asset_id: string;
  rul_hours: float;
  rul_days: float;
  rul_years: float;
  confidence: float;
  basis: string;
  design_life_hours: int;
  percent_life_used: float;
}

export interface RiskResponse {
  asset_id: string;
  overall_risk_score: float;
  overall_risk_level: string;
  risk_level_numeric: int;
  risk_scores: Record<string, float>;
  risk_contributions_percent: Record<string, float>;
  primary_risk_drivers: Array<string>;
  risk_recommendations: Array<string>;
  confidence: float;
  assessment_timestamp: string;
  risk_trend: string;
  recommended_action_urgency: string;
}

export interface DecisionResponse {
  asset_id: string;
  recommended_intervention: string;
  recommended_intervention_key: string;
  intervention_scores: Record<string, any>;
  optimal_intervention_score: float;
  explanation: Array<string>;
  assessment_details: Record<string, any>;
}

export interface SimulationResponse {
  // Input parameters
  load_percent: float;
  ambient_temp_c: float;
  cooling_mode: string;
  harmonic_distortion_thd: float;
  simulation_hours: float;
  vibration_rms_mm_s: float;
  dielectric_stress_factor: float;
  symmetry_imbalance_percent: float;
  partial_discharge_detected: boolean;

  // Electrical parameters
  rated_current_a: float;
  actual_current_a: float;
  rated_voltage_kv: float;
  actual_voltage_kv: float;
  apparent_power_mva: float;
  real_power_mw: float;
  reactive_power_mvar: float;
  power_factor: float;
  resistance_ohm: float;
  reactance_ohm: float;
  impedance_ohm: float;
  impedance_percent: float;
  voltage_regulation_percent: float;

  // Losses breakdown
  no_load_losses_kw: float;
  load_losses_kw: float;
  total_losses_kw: float;
  losses_breakdown: Record<string, any>;
  harmonic_loss_factors: Record<string, float>;

  // Temperatures
  oil_temp_c: float;
  winding_temp_c: float;
  hotspot_temp_c: float;
  temperature_rise_oil_c: float;
  temperature_rise_winding_c: float;
  temperature_rise_hotspot_c: float;
  hotspot_gradient_c: float;
  oil_winding_gradient_c: float;

  // Thermal time constants
  thermal_time_constants_hours: Record<string, float>;

  // Efficiency and losses
  efficiency_percent: float;
  losses_percent: float;

  // Aging and health
  health_impact_per_hour: float;
  estimated_remaining_hours: float;
  aging_rate_per_hour: float;
  design_life_hours: int;
  combined_aging_factor: float;
  aging_breakdown: Record<string, float>;

  // Risk assessment
  risk_level: string;
  risk_level_numeric: int;
  risk_confidence: float;
  risk_scores: Record<string, float>;
  max_individual_risk: float;
  significant_risk_factors: Record<string, float>;

  // Dielectric and insulation
  bil_level_kv: float;
  dielectric_stress_actual: float;
  partial_discharge_risk: string;

  // System parameters
  frequency_hz: float;
  rated_mva: float;
  voltage_rating_kv: float;
  temp_rise_limit_c: float;
  impedance_percent: float;
  x_over_r_ratio: float;

  // Timestamp
  timestamp: string;
  simulation_id: string;
}

export interface SummaryResponse {
  asset_id: string;
  health: HealthResponse;
  rul: RULResponse;
  risk: RiskResponse;
  decision: DecisionResponse;
  simulation: SimulationResponse;
  timestamp: string;
}

export interface TelemetryData {
  asset_id: string;
  load_percent: float;
  voltage_kv?: float;
  current_a?: float;
  ambient_temp_c: float;
  oil_temp_c?: float;
  winding_temp_c?: float;
  vibration_mm_s: float;
  operating_hours?: float;
}

export interface SimulationRequest {
  load_percent: float;
  ambient_temp_c: float;
  cooling_mode: string;
  harmonic_distortion_thd: float;
  hours_at_conditions: float;
  vibration_rms_mm_s: float;
  dielectric_stress_factor: float;
  symmetry_imbalance_percent: float;
  partial_discharge_detected: boolean;
}