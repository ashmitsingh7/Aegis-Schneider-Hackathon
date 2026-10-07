"""
Remaining Useful Life (RUL) Prediction Model for Aegis
Estimates transformer remaining useful life based on health metrics, aging models, and operational stresses
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
import logging
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformerRULModel:
    """
    Remaining Useful Life prediction model for power transformers
    Estimates RUL based on comprehensive aging models and operational condition history
    """

    def __init__(self, model_path: str = None):
        """
        Initialize the RUL prediction model

        Args:
            model_path: Path to pre-trained model (optional)
        """
        self.scaler = StandardScaler()
        self.rul_predictor = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.is_trained = False

        # Transformer design specifications (baseline for a 10 MVA, 23 kV unit)
        self.design_life_hours = 180000  # ~20 years at 40°C ambient, average loading
        self.base_temperature_c = 40.0   # Reference ambient temperature
        self.base_load_percent = 60.0    # Reference average load

        # Aging model parameters (Arrhenius-based)
        self.aging_acceleration_ea = 15000  # Activation energy (J/mol) for cellulose insulation
        self.aging_acceleration_r = 8.314   # Gas constant (J/mol·K)

        # Temperature thresholds for aging acceleration
        self.temp_aging_thresholds = [
            (80, 6.0),   # 80-90°C: 6x aging rate
            (90, 8.0),   # 90-95°C: 8x aging rate
            (95, 10.0),  # 95-100°C: 10x aging rate
            (100, 12.0), # 100-110°C: 12x aging rate
            (110, 15.0), # 110-120°C: 15x aging rate
            (120, 18.0)  # >120°C: 18x aging rate
        ]

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            logger.info("RUL model initialized - will train on first use")

    def engineer_features(self, telemetry_data: Dict[str, Any],
                         health_metrics: Dict[str, Any] = None) -> np.ndarray:
        """
        Engineer features for RUL prediction from telemetry and health data

        Args:
            telemetry_data: Current telemetry readings
            health_metrics: Health assessment from health model (optional)

        Returns:
            Engineered feature array for RUL prediction
        """
        # Extract core telemetry features
        load_percent = telemetry_data.get('load_percent', 0.0)
        ambient_temp = telemetry_data.get('ambient_temp_c', 0.0)
        oil_temp = telemetry_data.get('oil_temp_c', 0.0)
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)
        voltage_kv = telemetry_data.get('voltage_kv', 23.0)
        current_a = telemetry_data.get('current_a', 0.0)
        vibration = telemetry_data.get('vibration_mm_s', 0.0)
        operating_hours = telemetry_data.get('operating_hours', 0.0)

        # Calculate derived thermal metrics
        winding_oil_gradient = winding_temp - oil_temp
        oil_ambient_gradient = oil_temp - ambient_temp
        hotspot_gradient = winding_temp * 1.2 - winding_temp  # Approximate hotspot gradient

        # Electrical stress factors
        rated_current = (10.0 * 1000) / (np.sqrt(3) * 23.0)  # 10 MVA, 23kV base
        load_factor = load_percent / 100.0
        current_ratio = current_a / rated_current if rated_current > 0 else 0
        current_imbalance = abs(current_ratio - load_factor) if rated_current > 0 else 0

        voltage_deviation = abs(voltage_kv - 23.0) / 23.0 if voltage_kv > 0 else 0
        overvoltage_factor = max(0, (voltage_kv - 23.0) / 23.0)
        undervoltage_factor = max(0, (23.0 - voltage_kv) / 23.0)

        # Thermal aging calculation
        thermal_aging_factor = self._calculate_thermal_aging_factor(winding_temp)

        # Load aging factor (simplified - quadratic dependence on load)
        load_aging_factor = 1.0 + (load_factor - 0.6) ** 2 * 0.5  # Baseline at 60% load

        # Voltage aging factor
        voltage_aging_factor = 1.0 + overvoltage_factor * 0.3 + undervoltage_factor * 0.1

        # Vibration aging factor
        vibration_aging_factor = 1.0 + (vibration / 10.0) ** 2 * 0.2

        # Combined aging rate
        combined_aging_rate = thermal_aging_factor * load_aging_factor * voltage_aging_factor * vibration_aging_factor

        # Operational stress indicators
        thermal_stress_ratio = max(0, (winding_temp - 90) / 30)  # Stress above 90°C
        overload_stress = max(0, (load_percent - 100) / 50)     # Stress above rating
        voltage_stress = max(0, (abs(voltage_kv - 23.0) - 2) / 10)  # Stress beyond +/-2%

        # Service age factor
        service_age_factor = operating_hours / self.design_life_hours if self.design_life_hours > 0 else 0

        # Health-based features (if available)
        health_score = 50.0  # Default middle value
        failure_probability = 0.5  # Default middle value
        if health_metrics:
            health_score = health_metrics.get('health_score', 50.0)
            failure_probability = health_metrics.get('failure_probability', 0.5)

        # Construct feature vector
        features = [
            # Core operational parameters
            load_percent,
            ambient_temp,
            oil_temp,
            winding_temp,
            voltage_kv,
            current_a,
            vibration,
            operating_hours,

            # Derived thermal metrics
            winding_oil_gradient,
            oil_ambient_gradient,
            hotspot_gradient,

            # Electrical stress factors
            load_factor,
            current_imbalance,
            voltage_deviation,
            overvoltage_factor,
            undervoltage_factor,

            # Aging factors
            thermal_aging_factor,
            load_aging_factor,
            voltage_aging_factor,
            vibration_aging_factor,
            combined_aging_rate,

            # Stress indicators
            thermal_stress_ratio,
            overload_stress,
            voltage_stress,

            # Service and health factors
            service_age_factor,
            health_score,
            failure_probability,

            # Interaction terms (capture combined effects)
            load_percent * winding_temp / 10000,  # Load-temperature interaction
            vibration * operating_hours / 1e8,    # Vibration-service interaction
            voltage_deviation * load_factor,      # Voltage-load interaction
        ]

        return np.array(features).reshape(1, -1)

    def predict_rul(self, telemetry_data: Dict[str, Any],
                   health_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Predict Remaining Useful Life from telemetry and health data

        Args:
            telemetry_data: Dictionary containing telemetry readings
            health_metrics: Health assessment from health model (optional)

        Returns:
            Dictionary with RUL prediction in hours, days, and years, plus confidence
        """
        try:
            # Engineer features
            features = self.engineer_features(telemetry_data, health_metrics)

            # If not trained, train on baseline data
            if not self.is_trained:
                self._train_on_baseline()

            # Scale features
            features_scaled = self.scaler.transform(features)

            # Predict RUL in hours
            predicted_rul_hours = max(1.0, self.rul_predictor.predict(features_scaled)[0])

            # Apply physics-based constraints and aging model adjustment
            physics_based_rul = self._calculate_physics_based_rul(telemetry_data, health_metrics)

            # Combine ML prediction with physics-based estimate (weighted average)
            # Trust physics more at extremes, ML in normal operating range
            weight_physics = 0.7 if (health_metrics and health_metrics.get('health_score', 50) < 60) else 0.3
            final_rul_hours = (weight_physics * physics_based_rul +
                              (1 - weight_physics) * predicted_rul_hours)

            # Apply reasonable bounds
            final_rul_hours = max(24, min(final_rul_hours, self.design_life_hours * 2))  # 1 day to 2x design life

            # Convert to days and years
            rul_days = final_rul_hours / 24.0
            rul_years = rul_days / 365.0

            # Calculate confidence based on data quality and model certainty
            confidence = self._calculate_prediction_confidence(telemetry_data, health_metrics, features_scaled)

            result = {
                'asset_id': telemetry_data.get('asset_id', 'T-01'),
                'rul_hours': round(final_rul_hours, 1),
                'rul_days': round(rul_days, 1),
                'rul_years': round(rul_years, 2),
                'confidence': round(confidence, 3),
                'basis': 'physics_ml_hybrid',
                'design_life_hours': self.design_life_hours,
                'percent_life_used': round((1 - (final_rul_hours / self.design_life_hours)) * 100, 1) if final_rul_hours > 0 else 100
            }

            logger.info(f"RUL prediction completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in RUL prediction: {e}")
            # Return physics-based estimate as fallback
            fallback_rul = self._calculate_physics_based_rul(telemetry_data, health_metrics)
            fallback_rul = max(24, min(fallback_rul, self.design_life_hours * 2))

            return {
                'asset_id': telemetry_data.get('asset_id', 'T-01'),
                'rul_hours': round(fallback_rul, 1),
                'rul_days': round(fallback_rul / 24.0, 1),
                'rul_years': round((fallback_rul / 24.0) / 365.0, 2),
                'confidence': 0.3,  # Low confidence for fallback
                'basis': 'physics_only_fallback',
                'design_life_hours': self.design_life_hours,
                'percent_life_used': round((1 - (fallback_rul / self.design_life_hours)) * 100, 1) if fallback_rul > 0 else 100
            }

    def _train_on_baseline(self):
        """Train the RUL model on baseline operating data"""
        # Generate synthetic training data representing various operating conditions
        np.random.seed(42)  # For reproducible results
        n_samples = 500

        # Generate realistic operating scenarios
        baseline_data = []
        baseline_rul = []

        for _ in range(n_samples):
            # Random operating conditions within realistic bounds
            load_percent = np.random.uniform(20, 110)      # 20% to 110% load
            ambient_temp = np.random.uniform(-10, 45)      # -10°C to 45°C ambient
            oil_temp = np.random.uniform(25, 85)           # 25°C to 85°C oil
            winding_temp = np.random.uniform(30, 105)      # 30°C to 105°C winding
            voltage_kv = np.random.uniform(20, 26)         # 20kV to 26V voltage
            current_a = load_percent * 188 / 75             # Approximate current for load
            vibration = np.random.uniform(0.5, 5.0)        # 0.5 to 5.0 mm/s vibration
            operating_hours = np.random.uniform(0, 8760 * 15)  # 0 to 15 years service

            telemetry_data = {
                'asset_id': 'T-01',
                'load_percent': load_percent,
                'voltage_kv': voltage_kv,
                'current_a': current_a,
                'ambient_temp_c': ambient_temp,
                'oil_temp_c': oil_temp,
                'winding_temp_c': winding_temp,
                'vibration_mm_s': vibration,
                'operating_hours': operating_hours
            }

            # Calculate physics-based RUL for training target
            physics_rul = self._calculate_physics_based_rul(telemetry_data, None)

            # Add some noise to make it more realistic
            noise_factor = np.random.uniform(0.8, 1.2)
            training_rul = physics_rul * noise_factor
            training_rul = max(24, min(training_rul, self.design_life_hours * 2))

            # Engineer features
            features = self.engineer_features(telemetry_data, None)
            baseline_data.append(features[0])
            baseline_rul.append(training_rul)

        # Convert to arrays and train
        X_train = np.array(baseline_data)
        y_train = np.array(baseline_rul)

        # Fit scaler and predictor
        self.scaler.fit(X_train)
        self.rul_predictor.fit(self.scaler.transform(X_train), y_train)
        self.is_trained = True
        logger.info(f"RUL model trained on {n_samples} baseline samples")

    def _calculate_thermal_aging_factor(self, winding_temp_c: float) -> float:
        """Calculate thermal aging factor using Arrhenius-based model"""
        if winding_temp_c < 0:
            return 1.0

        # Convert to Kelvin
        temp_k = winding_temp_c + 273.15
        reference_temp_k = self.base_temperature_c + 273.15

        # Arrhenius equation: k = A * exp(-Ea/(R*T))
        # Aging acceleration factor = exp[(Ea/R) * (1/T_ref - 1/T_actual)]
        try:
            aging_factor = np.exp(
                (self.aging_acceleration_ea / self.aging_acceleration_r) *
                (1/reference_temp_k - 1/temp_k)
            )
            # Cap extreme values for numerical stability
            return max(0.1, min(aging_factor, 50.0))
        except:
            # Fallback to piecewise linear if calculation fails
            return self._piecewise_thermal_aging(winding_temp_c)

    def _piecewise_thermal_aging(self, winding_temp_c: float) -> float:
        """Piecewise linear thermal aging model as fallback"""
        if winding_temp_c <= self.base_temperature_c:
            return 1.0

        for temp_threshold, aging_multiplier in self.temp_aging_thresholds:
            if winding_temp_c <= temp_threshold:
                # Linear interpolation between thresholds
                if temp_threshold == self.temp_aging_thresholds[0][0]:  # First threshold
                    return 1.0 + (aging_multiplier - 1.0) * (
                        (winding_temp_c - self.base_temperature_c) /
                        (temp_threshold - self.base_temperature_c)
                    )
                else:
                    # Find previous threshold
                    prev_threshold = [t for t, m in self.temp_aging_thresholds if t < temp_threshold][-1]
                    prev_multiplier = [m for t, m in self.temp_aging_thresholds if t == prev_threshold][0]
                    return prev_multiplier + (aging_multiplier - prev_multiplier) * (
                        (winding_temp_c - prev_threshold) / (temp_threshold - prev_threshold)
                    )

        # Above highest threshold
        return self.temp_aging_thresholds[-1][1]

    def _calculate_physics_based_rul(self, telemetry_data: Dict[str, Any],
                                   health_metrics: Dict[str, Any] = None) -> float:
        """
        Calculate RUL based on physics-informed aging models
        """
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)
        load_percent = telemetry_data.get('load_percent', 0.0)
        voltage_kv = telemetry_data.get('voltage_kv', 23.0)
        vibration = telemetry_data.get('vibration_mm_s', 0.0)
        operating_hours = telemetry_data.get('operating_hours', 0.0)

        # Calculate aging rates
        thermal_aging = self._calculate_thermal_aging_factor(winding_temp)
        load_factor = load_percent / 100.0
        load_aging = 1.0 + (load_factor - 0.6) ** 2 * 0.3  # Quadratic aging with load deviation

        # Voltage aging
        overvoltage = max(0, (voltage_kv - 23.0) / 23.0)
        undervoltage = max(0, (23.0 - voltage_kv) / 23.0)
        voltage_aging = 1.0 + overvoltage * 0.4 + undervoltage * 0.1

        # Vibration aging
        vibration_aging = 1.0 + (vibration / 10.0) ** 2 * 0.25

        # Combined aging rate (hours of aging per actual hour)
        combined_aging_rate = thermal_aging * load_aging * voltage_aging * vibration_aging

        # Ensure minimum aging rate
        combined_aging_rate = max(combined_aging_rate, 0.5)

        # Calculate effective aging hours
        effective_aging_hours = operating_hours * combined_aging_rate

        # Estimate remaining life
        if effective_aging_hours >= self.design_life_hours:
            # Already exceeded design life - estimate based on excess aging
            excess_aging = effective_aging_hours - self.design_life_hours
            remaining_hours = max(24, self.design_life_hours / (1 + excess_aging / self.design_life_hours))
        else:
            # Normal case: remaining life = design life - effective aging
            remaining_hours = self.design_life_hours - effective_aging_hours
            remaining_hours = max(24, remaining_hours)  # At least 1 day

        return remaining_hours

    def _calculate_prediction_confidence(self, telemetry_data: Dict[str, Any],
                                       health_metrics: Dict[str, Any] = None,
                                       features_scaled: np.ndarray = None) -> float:
        """Calculate confidence in the RUL prediction"""
        base_confidence = 0.6

        # Increase confidence with more complete data
        data_completeness = 0
        expected_fields = ['load_percent', 'voltage_kv', 'current_a',
                         'ambient_temp_c', 'oil_temp_c', 'winding_temp_c',
                         'vibration_mm_s', 'operating_hours']

        for field in expected_fields:
            if field in telemetry_data and telemetry_data[field] is not None:
                data_completeness += 1

        completeness_bonus = (data_completeness / len(expected_fields)) * 0.25

        # Increase confidence if health metrics are available
        health_bonus = 0.1 if health_metrics else 0.0

        # Decrease confidence for extreme values (extrapolation risk)
        extreme_penalty = 0.0
        winding_temp = telemetry_data.get('winding_temp_c', 0)
        load_percent = telemetry_data.get('load_percent', 0)
        voltage_kv = telemetry_data.get('voltage_kv', 23)

        if winding_temp < 0 or winding_temp > 130:
            extreme_penalty += 0.1
        if load_percent < 0 or load_percent > 150:
            extreme_penalty += 0.1
        if voltage_kv < 18 or voltage_kv > 28:
            extreme_penalty += 0.1

        # Model-based confidence (if we have feature distances to training data)
        model_confidence = 0.05  # Small baseline

        confidence = base_confidence + completeness_bonus + health_bonus + model_confidence - extreme_penalty

        return max(0.1, min(0.95, confidence))

    def save_model(self, filepath: str):
        """Save the trained model to disk"""
        model_data = {
            'scaler': self.scaler,
            'rul_predictor': self.rul_predictor,
            'is_trained': self.is_trained,
            'design_life_hours': self.design_life_hours,
            'base_temperature_c': self.base_temperature_c,
            'base_load_percent': self.base_load_percent,
            'aging_acceleration_ea': self.aging_acceleration_ea,
            'aging_acceleration_r': self.aging_acceleration_r,
            'temp_aging_thresholds': self.temp_aging_thresholds
        }
        joblib.dump(model_data, filepath)
        logger.info(f"RUL model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load a pre-trained model from disk"""
        try:
            model_data = joblib.load(filepath)
            self.scaler = model_data['scaler']
            self.rul_predictor = model_data['rul_predictor']
            self.is_trained = model_data['is_trained']
            self.design_life_hours = model_data['design_life_hours']
            self.base_temperature_c = model_data['base_temperature_c']
            self.base_load_percent = model_data['base_load_percent']
            self.aging_acceleration_ea = model_data['aging_acceleration_ea']
            self.aging_acceleration_r = model_data['aging_acceleration_r']
            self.temp_aging_thresholds = model_data['temp_aging_thresholds']
            logger.info(f"RUL model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading RUL model: {e}")
            # Initialize fresh model
            self.__init__()


# Factory function for easy instantiation
def create_rul_model(model_path: str = None) -> TransformerRULModel:
    """
    Create and return a transformer RUL model instance

    Args:
        model_path: Path to pre-trained model (optional)

    Returns:
        TransformerRULModel instance
    """
    return TransformerRULModel(model_path)


# Example usage and testing
if __name__ == "__main__":
    print("Transformer RUL Model - Testing")
    print("=" * 40)

    # Create RUL model
    rul_model = create_rul_model()

    # Test cases representing different operating conditions
    test_scenarios = [
        {
            'name': 'New Transformer - Normal Operation',
            'asset_id': 'T-01',
            'load_percent': 60,
            'voltage_kv': 23.0,
            'current_a': 150,
            'ambient_temp_c': 25,
            'oil_temp_c': 40,
            'winding_temp_c': 55,
            'vibration_mm_s': 1.0,
            'operating_hours': 8760 * 0.5  # 0.5 years
        },
        {
            'name': 'Mid-Life Transformer - Elevated Load',
            'asset_id': 'T-01',
            'load_percent': 85,
            'voltage_kv': 22.8,
            'current_a': 212,
            'ambient_temp_c': 30,
            'oil_temp_c': 55,
            'winding_temp_c': 78,
            'vibration_mm_s': 1.5,
            'operating_hours': 8760 * 7  # 7 years
        },
        {
            'name': 'Aged Transformer - Thermal Stress',
            'asset_id': 'T-01',
            'load_percent': 75,
            'voltage_kv': 22.5,
            'current_a': 187,
            'ambient_temp_c': 35,
            'oil_temp_c': 65,
            'winding_temp_c': 92,
            'vibration_mm_s': 2.0,
            'operating_hours': 8760 * 12  # 12 years
        },
        {
            'name': 'Old Transformer - Overload Condition',
            'asset_id': 'T-01',
            'load_percent': 110,
            'voltage_kv': 22.0,
            'current_a': 275,
            'ambient_temp_c': 32,
            'oil_temp_c': 70,
            'winding_temp_c': 100,
            'vibration_mm_s': 2.5,
            'operating_hours': 8760 * 18  # 18 years
        },
        {
            'name': 'Critical Condition - High Temp & Load',
            'asset_id': 'T-01',
            'load_percent': 95,
            'voltage_kv': 22.0,
            'current_a': 237,
            'ambient_temp_c': 40,
            'oil_temp_c': 80,
            'winding_temp_c': 110,
            'vibration_mm_s': 3.0,
            'operating_hours': 8760 * 15  # 15 years
        }
    ]

    # Create a health model to provide health metrics
    from .health_model import create_health_model
    health_model = create_health_model()

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print("-" * 35)

        # Get health metrics first
        health_metrics = health_model.predict_health(scenario)

        # Predict RUL
        result = rul_model.predict_rul(scenario, health_metrics)

        print(f"📊 RUL PREDICTION:")
        print(f"   Asset ID: {result['asset_id']}")
        print(f"   RUL: {result['rul_hours']:,.0f} hours")
        print(f"   RUL: {result['rul_days']:,.0f} days")
        print(f"   RUL: {result['rul_years']:.1f} years")
        print(f"   Design Life Used: {result['percent_life_used']:.1f}%")
        print(f"   Confidence: {result['confidence']*100:.0f}%")
        print(f"   Basis: {result['basis']}")

        # Show health context
        print(f"📋 HEALTH CONTEXT:")
        print(f"   Health Score: {health_metrics['health_score']}/100")
        print(f"   Failure Probability: {health_metrics['failure_probability']*100:.1f}%")
        print(f"   Risk Level: {health_metrics['risk_level']}")