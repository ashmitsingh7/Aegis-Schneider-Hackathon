"""
Risk Assessment Model for Aegis
Evaluates multiple risk factors including thermal, electrical, mechanical, and dielectric stresses
to provide comprehensive risk assessment for power transformers
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
import logging
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformerRiskModel:
    """
    Comprehensive risk assessment model for power transformers
    Evaluates multiple risk factors and provides actionable risk levels
    """

    def __init__(self):
        """Initialize the risk assessment model"""
        # Risk factor weights (must sum to 1.0)
        self.risk_weights = {
            'thermal': 0.30,      # Temperature-related risks
            'electrical': 0.25,   # Voltage, current, loading stresses
            'insulation': 0.20,   # Dielectric and insulation integrity
            'mechanical': 0.15,   # Vibration, mechanical stresses
            'aging': 0.10         # Cumulative aging effects
        }

        # Risk level thresholds (0-5 scale)
        self.risk_levels = {
            'MINIMAL': (0.0, 1.0),
            'LOW': (1.0, 2.0),
            'MEDIUM': (2.0, 3.0),
            'HIGH': (3.0, 4.0),
            'CRITICAL': (4.0, 5.0)
        }

        # Thermal risk parameters
        self.thermal_thresholds = {
            'winding_warning': 90,    # °C
            'winding_alarm': 105,     # °C
            'winding_trip': 115,      # °C
            'hotspot_warning': 110,   # °C
            'hotspot_alarm': 125,     # °C
            'hotspot_trip': 135,      # °C
            'oil_warning': 85,        # °C
            'oil_alarm': 95,          # °C
            'oil_trip': 105           # °C
        }

        # Electrical risk parameters
        self.electrical_thresholds = {
            'overload_warning': 100,   # % of rating
            'overload_alarm': 110,     # % of rating
            'overload_trip': 125,      # % of rating
            'overvoltage_warning': 105, # % of rated voltage
            'overvoltage_alarm': 110,   # % of rated voltage
            'overvoltage_trip': 120,    # % of rated voltage
            'undervoltage_warning': 95,  # % of rated voltage
            'undervoltage_alarm': 90,   # % of rated voltage
            'undervoltage_trip': 80,    # % of rated voltage
            'voltage_imbalance_warning': 5,   # % imbalance
            'voltage_imbalance_alarm': 10,    # % imbalance
            'voltage_imbalance_trip': 15      # % imbalance
        }

        # Mechanical risk parameters
        self.mechanical_thresholds = {
            'vibration_warning': 3.0,   # mm/s RMS
            'vibration_alarm': 5.0,     # mm/s RMS
            'vibration_trip': 7.0,      # mm/s RMS
            'shock_warning': 50,        # g peak
            'shock_alarm': 100,         # g peak
            'shock_trip': 150           # g peak
        }

        # Insulation/dielectric risk parameters
        self.insulation_thresholds = {
            'partial_discharge_concern': 50,   # mV (indicative level)
            'partial_discharge_warning': 100,  # mV
            'partial_discharge_alarm': 200,    # mV
            'moisture_warning': 30,            # ppm water in oil
            'moisture_alarm': 50,              # ppm water in oil
            'oil_acidity_warning': 0.1,        # mg KOH/g
            'oil_acidity_alarm': 0.2           # mg KOH/g
        }

        # Aging risk parameters
        self.aging_thresholds = {
            'aging_factor_warning': 1.5,   # x design aging rate
            'aging_factor_alarm': 2.0,     # x design aging rate
            'aging_factor_trip': 3.0,      # x design aging rate
            'furan_warning': 0.5,          # mg/kg (degree of polymerization)
            'furan_alarm': 1.0,            # mg/kg
            'furan_trip': 2.0              # mg/kg
        }

        logger.info("Transformer Risk Model initialized")

    def assess_comprehensive_risk(self, telemetry_data: Dict[str, Any],
                                health_metrics: Dict[str, Any] = None,
                                rul_metrics: Dict[str, Any] = None,
                                electrical_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment

        Args:
            telemetry_data: Current telemetry readings
            health_metrics: Health assessment from health model (optional)
            rul_metrics: RUL assessment from RUL model (optional)
            electrical_params: Electrical parameters from digital twin (optional)

        Returns:
            Dictionary with detailed risk scores, levels, and recommendations
        """
        try:
            # Calculate individual risk factor scores (0-5 scale)
            thermal_risk = self._assess_thermal_risk(telemetry_data)
            electrical_risk = self._assess_electrical_risk(telemetry_data, electrical_params)
            insulation_risk = self._assess_insulation_risk(telemetry_data, health_metrics)
            mechanical_risk = self._assess_mechanical_risk(telemetry_data)
            aging_risk = self._assess_aging_risk(telemetry_data, health_metrics, rul_metrics)

            # Calculate weighted composite risk score
            composite_risk_score = (
                self.risk_weights['thermal'] * thermal_risk +
                self.risk_weights['electrical'] * electrical_risk +
                self.risk_weights['insulation'] * insulation_risk +
                self.risk_weights['mechanical'] * mechanical_risk +
                self.risk_weights['aging'] * aging_risk
            )

            # Determine overall risk level
            overall_risk_level = self._get_risk_level(composite_risk_score)

            # Calculate risk contributions (percentage of total risk)
            total_weighted_risk = (
                self.risk_weights['thermal'] * thermal_risk +
                self.risk_weights['electrical'] * electrical_risk +
                self.risk_weights['insulation'] * insulation_risk +
                self.risk_weights['mechanical'] * mechanical_risk +
                self.risk_weights['aging'] * aging_risk
            )

            if total_weighted_risk > 0:
                risk_contributions = {
                    'thermal': (self.risk_weights['thermal'] * thermal_risk / total_weighted_risk) * 100,
                    'electrical': (self.risk_weights['electrical'] * electrical_risk / total_weighted_risk) * 100,
                    'insulation': (self.risk_weights['insulation'] * insulation_risk / total_weighted_risk) * 100,
                    'mechanical': (self.risk_weights['mechanical'] * mechanical_risk / total_weighted_risk) * 100,
                    'aging': (self.risk_weights['aging'] * aging_risk / total_weighted_risk) * 100
                }
            else:
                risk_contributions = {
                    'thermal': 0.0,
                    'electrical': 0.0,
                    'insulation': 0.0,
                    'mechanical': 0.0,
                    'aging': 0.0
                }

            # Identify primary risk drivers (factors contributing >20% to total risk)
            primary_drivers = [factor for factor, contribution in risk_contributions.items()
                             if contribution > 20.0]

            # Generate risk-based recommendations
            recommendations = self._generate_risk_recommendations(
                thermal_risk, electrical_risk, insulation_risk,
                mechanical_risk, aging_risk, overall_risk_level, telemetry_data
            )

            # Calculate confidence in assessment
            confidence = self._assess_confidence(telemetry_data, health_metrics, rul_metrics, electrical_params)

            result = {
                'asset_id': telemetry_data.get('asset_id', 'T-01'),
                'overall_risk_score': round(composite_risk_score, 2),
                'overall_risk_level': overall_risk_level,
                'risk_level_numeric': self._risk_level_to_numeric(overall_risk_level),
                'risk_scores': {
                    'thermal': round(thermal_risk, 2),
                    'electrical': round(electrical_risk, 2),
                    'insulation': round(insulation_risk, 2),
                    'mechanical': round(mechanical_risk, 2),
                    'aging': round(aging_risk, 2)
                },
                'risk_contributions_percent': {
                    k: round(v, 1) for k, v in risk_contributions.items()
                },
                'primary_risk_drivers': primary_drivers,
                'risk_recommendations': recommendations,
                'confidence': round(confidence, 3),
                'assessment_timestamp': pd.Timestamp.now().isoformat(),
                'risk_trend': 'STABLE',  # Would be calculated from historical data
                'recommended_action_urgency': self._get_action_urgency(overall_risk_level)
            }

            logger.info(f"Comprehensive risk assessment completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            # Return safe default assessment
            return {
                'asset_id': telemetry_data.get('asset_id', 'T-01'),
                'overall_risk_score': 2.5,
                'overall_risk_level': 'MEDIUM',
                'risk_level_numeric': 3,
                'risk_scores': {
                    'thermal': 2.5,
                    'electrical': 2.5,
                    'insulation': 2.5,
                    'mechanical': 2.5,
                    'aging': 2.5
                },
                'risk_contributions_percent': {
                    'thermal': 20.0,
                    'electrical': 20.0,
                    'insulation': 20.0,
                    'mechanical': 20.0,
                    'aging': 20.0
                },
                'primary_risk_drivers': ['unknown'],
                'risk_recommendations': ['Perform detailed inspection and monitoring'],
                'confidence': 0.3,
                'assessment_timestamp': pd.Timestamp.now().isoformat(),
                'risk_trend': 'UNKNOWN',
                'recommended_action_urgency': 'MEDIUM'
            }

    def _assess_thermal_risk(self, telemetry_data: Dict[str, Any]) -> float:
        """Assess thermal-related risks (0-5 scale)"""
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)
        oil_temp = telemetry_data.get('oil_temp_c', 0.0)
        ambient_temp = telemetry_data.get('ambient_temp_c', 0.0)

        # Winding temperature risk
        if winding_temp >= self.thermal_thresholds['winding_trip']:
            winding_risk = 5.0
        elif winding_temp >= self.thermal_thresholds['winding_alarm']:
            winding_risk = 4.0
        elif winding_temp >= self.thermal_thresholds['winding_warning']:
            winding_risk = 3.0
        elif winding_temp >= 80:  # Warning threshold
            winding_risk = 2.0
        else:
            winding_risk = max(0.0, (winding_temp - 25) / 55 * 1.0)  # Linear from 25°C to 80°C

        # Oil temperature risk
        if oil_temp >= self.thermal_thresholds['oil_trip']:
            oil_risk = 5.0
        elif oil_temp >= self.thermal_thresholds['oil_alarm']:
            oil_risk = 4.0
        elif oil_temp >= self.thermal_thresholds['oil_warning']:
            oil_risk = 3.0
        else:
            oil_risk = max(0.0, (oil_temp - 25) / 60 * 2.0)  # Linear from 25°C to 85°C

        # Temperature gradient risk (winding-oil indicates loading)
        gradient = winding_temp - oil_temp
        if gradient >= 25:
            gradient_risk = 4.0
        elif gradient >= 20:
            gradient_risk = 3.0
        elif gradient >= 15:
            gradient_risk = 2.0
        else:
            gradient_risk = max(0.0, gradient / 15 * 1.0)

        # Hot spot risk (estimated)
        hotspot_est = winding_temp + 15  # Approximate hot spot
        if hotspot_est >= self.thermal_thresholds['hotspot_trip']:
            hotspot_risk = 5.0
        elif hotspot_est >= self.thermal_thresholds['hotspot_alarm']:
            hotspot_risk = 4.0
        elif hotspot_est >= self.thermal_thresholds['hotspot_warning']:
            hotspot_risk = 3.0
        else:
            hotspot_risk = max(0.0, (hotspot_est - 90) / 25 * 2.0) if hotspot_est > 90 else 0.0

        # Return maximum of all thermal risks
        return max(winding_risk, oil_risk, gradient_risk, hotspot_risk)

    def _assess_electrical_risk(self, telemetry_data: Dict[str, Any],
                              electrical_params: Dict[str, Any] = None) -> float:
        """Assess electrical-related risks (0-5 scale)"""
        load_percent = telemetry_data.get('load_percent', 0.0)
        voltage_kv = telemetry_data.get('voltage_kv', 0.0)
        current_a = telemetry_data.get('current_a', 0.0)

        # Use electrical params if available (more accurate)
        if electrical_params:
            # These would come from the digital twin model
            impedance_percent = electrical_params.get('impedance_percent', 8.0)
            voltage_regulation = electrical_params.get('voltage_regulation_percent', 5.0)
            efficiency = electrical_params.get('efficiency_percent', 98.0)
        else:
            # Fallback to telemetry-based estimates
            impedance_percent = 8.0  # Default
            voltage_regulation = 5.0  # Default
            efficiency = 98.0  # Default

        # Overload risk
        if load_percent >= self.electrical_thresholds['overload_trip']:
            overload_risk = 5.0
        elif load_percent >= self.electrical_thresholds['overload_alarm']:
            overload_risk = 4.0
        elif load_percent >= self.electrical_thresholds['overload_warning']:
            overload_risk = 3.0
        else:
            overload_risk = max(0.0, (load_percent - 80) / 20 * 2.0) if load_percent > 80 else 0.0

        # Overvoltage risk
        if voltage_kv > 0:
            voltage_percent = (voltage_kv / 23.0) * 100  # Assuming 23kV rated
            if voltage_percent >= self.electrical_thresholds['overvoltage_trip']:
                overvoltage_risk = 5.0
            elif voltage_percent >= self.electrical_thresholds['overvoltage_alarm']:
                overvoltage_risk = 4.0
            elif voltage_percent >= self.electrical_thresholds['overvoltage_warning']:
                overvoltage_risk = 3.0
            else:
                overvoltage_risk = max(0.0, (voltage_percent - 100) / 10 * 1.5) if voltage_percent > 100 else 0.0

            # Undervoltage risk
            if voltage_percent <= self.electrical_thresholds['undervoltage_trip']:
                undervoltage_risk = 5.0
            elif voltage_percent <= self.electrical_thresholds['undervoltage_alarm']:
                undervoltage_risk = 4.0
            elif voltage_percent <= self.electrical_thresholds['undervoltage_warning']:
                undervoltage_risk = 3.0
            else:
                undervoltage_risk = max(0.0, (95 - voltage_percent) / 5 * 2.0) if voltage_percent < 95 else 0.0
            voltage_risk = max(overvoltage_risk, undervoltage_risk)
        else:
            voltage_risk = 0.0
            overload_risk = 0.0

        # Efficiency loss risk (indicates internal problems)
        if efficiency < 95:
            efficiency_risk = 4.0
        elif efficiency < 96:
            efficiency_risk = 3.0
        elif efficiency < 97:
            efficiency_risk = 2.0
        else:
            efficiency_risk = 0.0

        # Voltage regulation risk
        if voltage_regulation >= 10:
            regulation_risk = 4.0
        elif voltage_regulation >= 7:
            regulation_risk = 3.0
        elif voltage_regulation >= 5:
            regulation_risk = 2.0
        else:
            regulation_risk = 0.0

        # Impedance deviation risk (would indicate winding problems)
        impedance_deviation = abs(impedance_percent - 8.0)  # Assuming 8% nominal
        if impedance_deviation >= 3:
            impedance_risk = 4.0
        elif impedance_deviation >= 2:
            impedance_risk = 3.0
        elif impedance_deviation >= 1:
            impedance_risk = 2.0
        else:
            impedance_risk = impedance_deviation * 0.5

        # Current imbalance would come from phased CTs in real system
        # For now, simulate based on load deviation from expected
        expected_current = (load_percent / 100.0) * (10.0 * 1000) / (np.sqrt(3) * 23.0)  # Expected for load
        if expected_current > 0:
            current_imbalance = abs(current_a - expected_current) / expected_current * 100
        else:
            current_imbalance = 0

        if current_imbalance >= self.electrical_thresholds['voltage_imbalance_trip']:
            imbalance_risk = 5.0
        elif current_imbalance >= self.electrical_thresholds['voltage_imbalance_alarm']:
            imbalance_risk = 4.0
        elif current_imbalance >= self.electrical_thresholds['voltage_imbalance_warning']:
            imbalance_risk = 3.0
        else:
            imbalance_risk = max(0.0, (current_imbalance - 2) / 3 * 2.0) if current_imbalance > 2 else 0.0

        # Return maximum of all electrical risks
        return max(overload_risk, voltage_risk, efficiency_risk, regulation_risk, impedance_risk, imbalance_risk)

    def _assess_insulation_risk(self, telemetry_data: Dict[str, Any],
                              health_metrics: Dict[str, Any] = None) -> float:
        """Assess insulation and dielectric-related risks (0-5 scale)"""
        oil_temp = telemetry_data.get('oil_temp_c', 0.0)
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)
        load_percent = telemetry_data.get('load_percent', 0.0)

        # Thermal aging of insulation (main insulation stressor)
        thermal_aging = 1.0
        if winding_temp > 80:
            # Approximate doubling of aging rate every 6-8°C over 80°C
            excess_temp = winding_temp - 80
            thermal_aging = 1.0 + (excess_temp / 7.0)  # Rough approximation

        # Moisture risk (would come from oil testing in real system)
        # Simulate based on temperature and age
        moisture_risk = min(3.0, (oil_temp - 25) / 20 * 1.5) if oil_temp > 25 else 0.0

        # Partial discharge risk (increases with voltage stress and aging)
        voltage_stress = load_percent / 100.0  # Simplified
        pd_risk = min(4.0, voltage_stress * 2.0 + (thermal_aging - 1.0) * 1.5)

        # Oil deterioration risk
        oil_deterioration = min(3.0, (oil_temp - 40) / 25 * 2.0) if oil_temp > 40 else 0.0

        # Combine insulation risks
        insulation_risk = max(thermal_aging - 1.0, moisture_risk, pd_risk, oil_deterioration)
        insulation_risk = min(insulation_risk, 5.0)  # Cap at maximum

        return insulation_risk

    def _assess_mechanical_risk(self, telemetry_data: Dict[str, Any]) -> float:
        """Assess mechanical-related risks (0-5 scale)"""
        vibration = telemetry_data.get('vibration_mm_s', 0.0)
        # In a real system, we would also have:
        # - Shock sensors (for transport/fault detection)
        # - Pressure relief valve monitoring
        # - bushing movement sensors

        # Vibration risk
        if vibration >= self.mechanical_thresholds['vibration_trip']:
            vibration_risk = 5.0
        elif vibration >= self.mechanical_thresholds['vibration_alarm']:
            vibration_risk = 4.0
        elif vibration >= self.mechanical_thresholds['vibration_warning']:
            vibration_risk = 3.0
        else:
            vibration_risk = max(0.0, (vibration - 1.0) / 2.0 * 1.0) if vibration > 1.0 else 0.0

        # For now, vibration is the primary mechanical risk we can measure
        # Other mechanical risks would require additional sensors
        return vibration_risk

    def _assess_aging_risk(self, telemetry_data: Dict[str, Any],
                         health_metrics: Dict[str, Any] = None,
                         rul_metrics: Dict[str, Any] = None) -> float:
        """Assess aging-related risks (0-5 scale)"""
        # Use RUL metrics if available (most direct measure of aging)
        if rul_metrics:
            percent_life_used = rul_metrics.get('percent_life_used', 0.0)
            # Convert percentage life used to risk score
            if percent_life_used >= 90:
                aging_risk = 5.0
            elif percent_life_used >= 80:
                aging_risk = 4.0
            elif percent_life_used >= 70:
                aging_risk = 3.0
            elif percent_life_used >= 60:
                aging_risk = 2.0
            elif percent_life_used >= 40:
                aging_risk = 1.0
            else:
                aging_risk = 0.0
            return min(aging_risk, 5.0)

        # Use health metrics as fallback
        if health_metrics:
            health_score = health_metrics.get('health_score', 100.0)
            failure_prob = health_metrics.get('failure_probability', 0.0)
            # Invert health score and combine with failure probability
            health_risk = (100 - health_score) / 20.0  # 0-5 scale
            failure_risk = failure_prob * 5.0  # 0-5 scale
            aging_risk = max(health_risk, failure_risk)
            return min(aging_risk, 5.0)

        # Estimate from telemetry-based aging factors
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)
        load_percent = telemetry_data.get('load_percent', 0.0)
        voltage_kv = telemetry_data.get('voltage_kv', 23.0)
        operating_hours = telemetry_data.get('operating_hours', 0.0)

        # Thermal aging estimate
        thermal_aging = 1.0
        if winding_temp > 80:
            thermal_aging = np.exp((winding_temp - 80) / 10.0)  # Simplified
            thermal_aging = min(thermal_aging, 10.0)

        # Load aging estimate
        load_factor = load_percent / 100.0
        load_aging = 1.0 + abs(load_factor - 0.6)  # Deviation from 60% average load

        # Voltage aging estimate
        voltage_deviation = abs(voltage_kv - 23.0) / 23.0
        voltage_aging = 1.0 + voltage_deviation

        # Service aging
        service_years = operating_hours / 8760.0 if operating_hours > 0 else 0
        service_aging = 1.0 + service_years / 25.0  # Normalize to 25-year design life

        # Combined aging factor
        combined_aging = thermal_aging * load_aging * voltage_aging * service_aging
        aging_risk = min((combined_aging - 1.0) / 2.0 * 4.0, 4.0)  # Scale to 0-4 range

        return max(aging_risk, 0.0)

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert numeric risk score to risk level"""
        for level, (min_val, max_val) in self.risk_levels.items():
            if min_val <= risk_score < max_val:
                return level
        # Handle edge case of exactly 5.0
        if risk_score >= 5.0:
            return 'CRITICAL'
        return 'MINIMAL'  # Default fallback

    def _risk_level_to_numeric(self, risk_level: str) -> int:
        """Convert risk level to numeric value for easier comparison"""
        level_map = {
            'MINIMAL': 1,
            'LOW': 2,
            'MEDIUM': 3,
            'HIGH': 4,
            'CRITICAL': 5
        }
        return level_map.get(risk_level, 3)  # Default to MEDIUM

    def _generate_risk_recommendations(self, thermal_risk: float, electrical_risk: float,
                                     insulation_risk: float, mechanical_risk: float,
                                     aging_risk: float, overall_risk_level: str,
                                     telemetry_data: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on risk factors"""
        recommendations = []

        # Thermal risk recommendations
        if thermal_risk >= 4.0:
            recommendations.append("Immediate load reduction recommended to prevent thermal damage")
            recommendations.append("Check cooling system effectiveness and oil circulation")
        elif thermal_risk >= 3.0:
            recommendations.append("Monitor temperature closely and consider load management")
            recommendations.append("Verify cooling system operation")

        # Electrical risk recommendations
        if electrical_risk >= 4.0:
            recommendations.append("Investigate possible overload or voltage regulation issues")
            recommendations.append("Check tap changer operation and voltage regulators")
        elif electrical_risk >= 3.0:
            recommendations.append("Monitor electrical parameters for abnormalities")
            recommendations.append("Verify load balance and voltage levels")

        # Insulation risk recommendations
        if insulation_risk >= 4.0:
            recommendations.append("Schedule dissolved gas analysis and oil testing")
            recommendations.append("Consider reducing operating voltage to decrease stress")
        elif insulation_risk >= 3.0:
            recommendations.append("Plan insulation testing during next maintenance window")
            recommendations.append("Monitor for signs of insulation deterioration")

        # Mechanical risk recommendations
        if mechanical_risk >= 4.0:
            recommendations.append("Investigate excessive vibration - check mechanical mounting and bushings")
            recommendations.append("Consider transient monitoring for mechanical shock detection")
        elif mechanical_risk >= 3.0:
            recommendations.append("Monitor vibration trends and check mechanical integrity")

        # Aging risk recommendations
        if aging_risk >= 4.0:
            recommendations.append("Advanced aging detected - evaluate replacement timing")
            recommendations.append("Consider accelerated testing to determine remaining life")
        elif aging_risk >= 3.0:
            recommendations.append("Review maintenance history and consider condition-based monitoring")
            recommendations.append("Plan for potential life extension activities")

        # Overall risk level recommendations
        if overall_risk_level == 'CRITICAL':
            recommendations.insert(0, "CRITICAL: Immediate action required - consider load reduction or outage")
            recommendations.insert(1, "Notify operations and maintenance teams immediately")
        elif overall_risk_level == 'HIGH':
            recommendations.insert(0, "HIGH: Schedule maintenance intervention within 7 days")
            recommendations.insert(1, "Increase monitoring frequency to daily checks")
        elif overall_risk_level == 'MEDIUM':
            recommendations.insert(0, "MEDIUM: Include in routine maintenance planning")
            recommendations.insert(1, "Continue normal monitoring with increased awareness")

        # Default recommendation if none generated
        if not recommendations:
            recommendations.append("Continue normal operation and monitoring")
            recommendations.append("No immediate action required based on current risk assessment")

        return recommendations

    def _assess_confidence(self, telemetry_data: Dict[str, Any],
                         health_metrics: Dict[str, Any] = None,
                         rul_metrics: Dict[str, Any] = None,
                         electrical_params: Dict[str, Any] = None) -> float:
        """Assess confidence in the risk assessment"""
        base_confidence = 0.6

        # Data completeness bonus
        expected_telemetry = ['load_percent', 'voltage_kv', 'current_a',
                            'ambient_temp_c', 'oil_temp_c', 'winding_temp_c',
                            'vibration_mm_s', 'operating_hours']
        telemetry_complete = sum(1 for field in expected_telemetry
                               if field in telemetry_data and telemetry_data[field] is not None)
        completeness_bonus = (telemetry_complete / len(expected_telemetry)) * 0.2

        # Health metrics bonus
        health_bonus = 0.1 if health_metrics else 0.0

        # RUL metrics bonus
        rul_bonus = 0.1 if rul_metrics else 0.0

        # Electrical params bonus (most sophisticated data)
        electrical_bonus = 0.1 if electrical_params else 0.0

        # Penalty for missing critical data
        critical_missing = 0
        critical_fields = ['winding_temp_c', 'load_percent', 'oil_temp_c']
        for field in critical_fields:
            if field not in telemetry_data or telemetry_data[field] is None:
                critical_missing += 1
        critical_penalty = (critical_missing / len(critical_fields)) * 0.3

        confidence = base_confidence + completeness_bonus + health_bonus + rul_bonus + electrical_bonus - critical_penalty

        return max(0.2, min(0.95, confidence))

    def _get_action_urgency(self, risk_level: str) -> str:
        """Get recommended action urgency based on risk level"""
        urgency_map = {
            'MINIMAL': 'LOW',
            'LOW': 'LOW',
            'MEDIUM': 'MEDIUM',
            'HIGH': 'HIGH',
            'CRITICAL': 'CRITICAL'
        }
        return urgency_map.get(risk_level, 'MEDIUM')


# Factory function for easy instantiation
def create_risk_model() -> TransformerRiskModel:
    """
    Create and return a transformer risk model instance

    Returns:
        TransformerRiskModel instance
    """
    return TransformerRiskModel()


# Example usage and testing
if __name__ == "__main__":
    print("Transformer Risk Model - Testing")
    print("=" * 40)

    # Create risk model
    risk_model = create_risk_model()

    # Test cases representing different risk scenarios
    test_scenarios = [
        {
            'name': 'Normal Operation',
            'asset_id': 'T-01',
            'load_percent': 65,
            'voltage_kv': 23.0,
            'current_a': 163,
            'ambient_temp_c': 25,
            'oil_temp_c': 45,
            'winding_temp_c': 55,
            'vibration_mm_s': 1.2,
            'operating_hours': 8760 * 2  # 2 years
        },
        {
            'name': 'Elevated Temperature',
            'asset_id': 'T-01',
            'load_percent': 70,
            'voltage_kv': 23.0,
            'current_a': 175,
            'ambient_temp_c': 30,
            'oil_temp_c': 55,
            'winding_temp_c': 85,
            'vibration_mm_s': 1.5,
            'operating_hours': 8760 * 2
        },
        {
            'name': 'Overload Condition',
            'asset_id': 'T-01',
            'load_percent': 115,
            'voltage_kv': 22.5,
            'current_a': 288,
            'ambient_temp_c': 32,
            'oil_temp_c': 60,
            'winding_temp_c': 95,
            'vibration_mm_s': 2.0,
            'operating_hours': 8760 * 2
        },
        {
            'name': 'High Voltage Stress',
            'asset_id': 'T-01',
            'load_percent': 80,
            'voltage_kv': 25.0,  # Overvoltage
            'current_a': 200,
            'ambient_temp_c': 28,
            'oil_temp_c': 50,
            'winding_temp_c': 70,
            'vibration_mm_s': 1.0,
            'operating_hours': 8760 * 2
        },
        {
            'name': 'Multiple Stress Factors',
            'asset_id': 'T-01',
            'load_percent': 95,
            'voltage_kv': 22.0,
            'current_a': 237,
            'ambient_temp_c': 35,
            'oil_temp_c': 75,
            'winding_temp_c': 105,
            'vibration_mm_s': 2.5,
            'operating_hours': 8760 * 8  # Aged unit
        }
    ]

    # Create health and RUL models for enhanced assessment
    from .health_model import create_health_model
    from .rul_model import create_rul_model
    health_model = create_health_model()
    rul_model = create_rul_model()

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print("-" * 35)

        # Get health and RUL metrics for comprehensive assessment
        health_metrics = health_model.predict_health(scenario)
        rul_metrics = rul_model.predict_rul(scenario, health_metrics)

        # Simulate electrical params (would come from digital twin)
        electrical_params = {
            'impedance_percent': 8.2,
            'voltage_regulation_percent': 6.5,
            'efficiency_percent': 96.8
        }

        # Perform comprehensive risk assessment
        result = risk_model.assess_comprehensive_risk(
            scenario, health_metrics, rul_metrics, electrical_params
        )

        print(f"⚠️  RISK ASSESSMENT:")
        print(f"   Overall Risk Score: {result['overall_risk_score']}/5.0")
        print(f"   Overall Risk Level: {result['overall_risk_level']}")
        print(f"   Confidence: {result['confidence']*100:.0f}%")
        print(f"   Action Urgency: {result['recommended_action_urgency']}")

        print(f"\n📊 RISK BREAKDOWN:")
        for risk_type, score in result['risk_scores'].items():
            contribution = result['risk_contributions_percent'][risk_type]
            print(f"   {risk_type.capitalize()}: {score}/5.0 ({contribution}%)")

        if result['primary_risk_drivers'] and result['primary_risk_drivers'][0] != 'unknown':
            print(f"   Primary Drivers: {', '.join(result['primary_risk_drivers'])}")

        print(f"\n💡 RECOMMENDATIONS:")
        for j, rec in enumerate(result['risk_recommendations'][:3], 1):  # Show top 3
            print(f"   {j}. {rec}")