"""
Health Prediction Model for Aegis
Converts transformer telemetry into asset health scores, failure probability, and degradation detection
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformerHealthModel:
    """
    Health prediction model for power transformers
    Processes telemetry data to generate health scores, failure probabilities, and degradation alerts
    """

    def __init__(self, model_path: str = None):
        """
        Initialize the health prediction model

        Args:
            model_path: Path to pre-trained model (optional)
        """
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False

        # Health score thresholds
        self.health_thresholds = {
            'excellent': 85,
            'good': 70,
            'fair': 55,
            'poor': 40,
            'critical': 0
        }

        # Risk level thresholds
        self.risk_thresholds = {
            'LOW': 0.3,
            'MEDIUM': 0.6,
            'HIGH': 0.8,
            'CRITICAL': 0.95
        }

        # Feature names for telemetry data
        self.feature_names = [
            'load_percent', 'voltage_kv', 'current_a',
            'ambient_temp_c', 'oil_temp_c', 'winding_temp_c',
            'vibration_mm_s', 'operating_hours'
        ]

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            logger.info("Health model initialized - will train on first use")

    def engineer_features(self, telemetry_data: Dict[str, Any]) -> np.ndarray:
        """
        Engineer features from raw telemetry data for health prediction

        Args:
            telemetry_data: Raw telemetry readings from transformer sensors

        Returns:
            Engineered feature array for model input
        """
        # Extract basic telemetry features
        features = []
        for feature in self.feature_names:
            value = telemetry_data.get(feature, 0.0)
            features.append(float(value))

        # Additional engineered features
        load_percent = telemetry_data.get('load_percent', 0.0)
        winding_temp = telemetry_data.get('winding_temp_c', 0.0)
        oil_temp = telemetry_data.get('oil_temp_c', 0.0)
        ambient_temp = telemetry_data.get('ambient_temp_c', 0.0)

        # Temperature gradients (key indicators of health)
        winding_oil_gradient = winding_temp - oil_temp
        oil_ambient_gradient = oil_temp - ambient_temp

        # Load-normalized temperature
        if load_percent > 0:
            temp_per_load = winding_temp / load_percent
        else:
            temp_per_load = winding_temp

        # Thermal stress indicator
        thermal_stress = np.clip((winding_temp - 90) / 20, 0, 1) if winding_temp > 90 else 0

        # Voltage regulation indicator (simplified)
        voltage = telemetry_data.get('voltage_kv', 23.0)
        voltage_deviation = abs(voltage - 23.0) / 23.0 if voltage > 0 else 0

        # Current imbalance (would come from phase monitoring in real system)
        current = telemetry_data.get('current_a', 0.0)
        rated_current = (10.0 * 1000) / (np.sqrt(3) * 23.0)  # 10 MVA, 23kV base
        current_ratio = current / rated_current if rated_current > 0 else 0
        current_imbalance = abs(current_ratio - load_percent/100.0)  # Deviation from expected

        # Add engineered features
        engineered_features = [
            winding_oil_gradient,
            oil_ambient_gradient,
            temp_per_load,
            thermal_stress,
            voltage_deviation,
            current_imbalance
        ]

        features.extend(engineered_features)

        return np.array(features).reshape(1, -1)

    def predict_health(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict transformer health from telemetry data

        Args:
            telemetry_data: Dictionary containing telemetry readings

        Returns:
            Dictionary with health score, failure probability, RUL, and risk level
        """
        try:
            # Engineer features
            features = self.engineer_features(telemetry_data)

            # If not trained, train on this sample (in production, would use historical data)
            if not self.is_trained:
                self._train_on_sample(features)

            # Scale features
            features_scaled = self.scaler.transform(features)

            # Get anomaly score (-1 for anomalies, 1 for normal)
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1

            # Convert anomaly score to health score (0-100 scale)
            # Anomaly scores typically range from -0.5 to 0.5, where negative is anomalous
            health_score_raw = max(0, min(100, (anomaly_score + 0.5) * 100))

            # Apply some smoothing and domain knowledge
            health_score = self._apply_domain_knowledge(telemetry_data, health_score_raw)

            # Calculate failure probability (inverse of health, with smoothing)
            failure_probability = max(0.01, min(0.99, (100 - health_score) / 100))

            # Estimate Remaining Useful Life (RUL) in days
            # Simplified model: Better health = longer RUL
            # Based on typical 20-30 year lifespan for transformers
            base_rul_days = 365 * 25  # 25 years baseline
            health_factor = health_score / 100.0
            estimated_rul_days = int(base_rul_days * health_factor)

            # Cap at reasonable values
            estimated_rul_days = max(1, min(estimated_rul_days, 365 * 40))  # 1 day to 40 years

            # Determine risk level
            risk_level = self._calculate_risk_level(failure_probability, telemetry_data)

            # Detect degradation type
            degradation_type = self._detect_degradation_type(telemetry_data, health_score)

            result = {
                'asset_id': telemetry_data.get('asset_id', 'T-01'),
                'health_score': round(health_score, 1),
                'failure_probability': round(failure_probability, 3),
                'estimated_rul_days': estimated_rul_days,
                'risk_level': risk_level,
                'degradation_type': degradation_type,
                'is_anomaly': bool(is_anomaly),
                'confidence': round(min(0.95, 0.7 + health_score/200), 3)  # Higher confidence with better data
            }

            logger.info(f"Health prediction completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in health prediction: {e}")
            # Return safe default values
            return {
                'asset_id': telemetry_data.get('asset_id', 'T-01'),
                'health_score': 50.0,
                'failure_probability': 0.5,
                'estimated_rul_days': 365 * 10,  # 10 years
                'risk_level': 'UNKNOWN',
                'degradation_type': 'UNDETERMINED',
                'is_anomaly': False,
                'confidence': 0.1
            }

    def _train_on_sample(self, features: np.ndarray):
        """Train the model on initial sample data"""
        # In a real implementation, this would use historical training data
        # For demo purposes, we'll create some reasonable baseline patterns
        baseline_data = np.array([
            [75, 23.0, 188, 25, 45, 65, 1.5, 8760*2],   # Normal operation
            [85, 23.0, 213, 30, 55, 80, 2.0, 8760*2],   # Elevated load
            [65, 23.0, 163, 20, 40, 55, 1.0, 8760*2],   # Light load
            [95, 23.0, 238, 35, 65, 90, 2.5, 8760*2],   # High load/hot
            [50, 22.8, 129, 15, 35, 50, 0.8, 8760*2],   # Low voltage/load
        ])

        # Add some engineered features to baseline data
        enhanced_baseline = []
        for row in baseline_data:
            telemetry_sample = {
                'load_percent': row[0],
                'voltage_kv': row[1],
                'current_a': row[2],
                'ambient_temp_c': row[3],
                'oil_temp_c': row[4],
                'winding_temp_c': row[5],
                'vibration_mm_s': row[6],
                'operating_hours': row[7]
            }
            enhanced_features = self.engineer_features(telemetry_sample)
            enhanced_baseline.append(enhanced_features[0])

        enhanced_baseline = np.array(enhanced_baseline)

        # Fit scaler and anomaly detector
        self.scaler.fit(enhanced_baseline)
        self.anomaly_detector.fit(self.scaler.transform(enhanced_baseline))
        self.is_trained = True
        logger.info("Health model trained on baseline data")

    def _apply_domain_knowledge(self, telemetry_data: Dict[str, Any], raw_health_score: float) -> float:
        """Apply domain-specific rules to adjust health score"""
        health_score = raw_health_score

        # Temperature-based adjustments
        winding_temp = telemetry_data.get('winding_temp_c', 0)
        oil_temp = telemetry_data.get('oil_temp_c', 0)

        # Critical temperature thresholds
        if winding_temp >= 120:
            health_score = min(health_score, 30)  # Severe overheating
        elif winding_temp >= 110:
            health_score = min(health_score, 50)  # Overheating
        elif winding_temp >= 100:
            health_score = min(health_score, 70)  # Elevated temperature

        if oil_temp >= 100:
            health_score = min(health_score, 40)  # High oil temperature
        elif oil_temp >= 90:
            health_score = min(health_score, 60)  # Elevated oil temperature

        # Load-based adjustments
        load_percent = telemetry_data.get('load_percent', 0)
        if load_percent >= 120:
            health_score = min(health_score, 40)  # Significant overload
        elif load_percent >= 110:
            health_score = min(health_score, 60)  # Overload
        elif load_percent >= 100:
            health_score = min(health_score, 80)  # At rating

        # Voltage adjustments
        voltage = telemetry_data.get('voltage_kv', 23.0)
        if voltage >= 26.0 or voltage <= 20.0:  # +/- 15% deviation
            health_score = min(health_score, 50)
        elif voltage >= 25.0 or voltage <= 21.0:  # +/- 10% deviation
            health_score = min(health_score, 70)

        # Vibration adjustments
        vibration = telemetry_data.get('vibration_mm_s', 0)
        if vibration >= 10:
            health_score = min(health_score, 30)  # High vibration
        elif vibration >= 7:
            health_score = min(health_score, 50)  # Elevated vibration

        # Ensure health score stays in valid range
        return max(0, min(100, health_score))

    def _calculate_risk_level(self, failure_probability: float, telemetry_data: Dict[str, Any]) -> str:
        """Calculate risk level based on failure probability and telemetry"""
        # Base risk from failure probability
        if failure_probability >= self.risk_thresholds['CRITICAL']:
            base_risk = 'CRITICAL'
        elif failure_probability >= self.risk_thresholds['HIGH']:
            base_risk = 'HIGH'
        elif failure_probability >= self.risk_thresholds['MEDIUM']:
            base_risk = 'MEDIUM'
        else:
            base_risk = 'LOW'

        # Adjust based on critical telemetry values
        winding_temp = telemetry_data.get('winding_temp_c', 0)
        load_percent = telemetry_data.get('load_percent', 0)

        # Upgrade risk for critical conditions
        if winding_temp >= 115 or load_percent >= 125:
            if base_risk in ['LOW', 'MEDIUM']:
                base_risk = 'HIGH'
            elif base_risk == 'HIGH':
                base_risk = 'CRITICAL'

        return base_risk

    def _detect_degradation_type(self, telemetry_data: Dict[str, Any], health_score: float) -> str:
        """Detect the type of degradation based on telemetry patterns"""
        if health_score >= 70:
            return 'NONE'

        winding_temp = telemetry_data.get('winding_temp_c', 0)
        oil_temp = telemetry_data.get('oil_temp_c', 0)
        load_percent = telemetry_data.get('load_percent', 0)
        vibration = telemetry_data.get('vibration_mm_s', 0)

        # Thermal degradation indicators
        if winding_temp > 100 or (winding_temp - oil_temp) > 15:
            return 'THERMAL'

        # Overload degradation
        if load_percent > 110:
            return 'OVERLOAD'

        # Vibration/mechanical degradation
        if vibration > 5:
            return 'MECHANICAL'

        # Insulation degradation (indicated by high oil temp with normal winding temp)
        if oil_temp > 85 and winding_temp < 95:
            return 'INSULATION'

        # Default to general degradation
        return 'GENERAL_DEGRADATION'

    def save_model(self, filepath: str):
        """Save the trained model to disk"""
        model_data = {
            'scaler': self.scaler,
            'anomaly_detector': self.anomaly_detector,
            'is_trained': self.is_trained,
            'health_thresholds': self.health_thresholds,
            'risk_thresholds': self.risk_thresholds
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Health model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load a pre-trained model from disk"""
        try:
            model_data = joblib.load(filepath)
            self.scaler = model_data['scaler']
            self.anomaly_detector = model_data['anomaly_detector']
            self.is_trained = model_data['is_trained']
            self.health_thresholds = model_data['health_thresholds']
            self.risk_thresholds = model_data['risk_thresholds']
            logger.info(f"Health model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Initialize fresh model
            self.__init__()


# Factory function for easy instantiation
def create_health_model(model_path: str = None) -> TransformerHealthModel:
    """
    Create and return a transformer health model instance

    Args:
        model_path: Path to pre-trained model (optional)

    Returns:
        TransformerHealthModel instance
    """
    return TransformerHealthModel(model_path)


# Example usage and testing
if __name__ == "__main__":
    print("Transformer Health Model - Testing")
    print("=" * 50)

    # Create health model
    health_model = create_health_model()

    # Test cases representing different operating conditions
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
            'operating_hours': 8760 * 3  # 3 years
        },
        {
            'name': 'Elevated Load',
            'asset_id': 'T-01',
            'load_percent': 85,
            'voltage_kv': 23.0,
            'current_a': 213,
            'ambient_temp_c': 30,
            'oil_temp_c': 55,
            'winding_temp_c': 80,
            'vibration_mm_s': 1.8,
            'operating_hours': 8760 * 3
        },
        {
            'name': 'Thermal Stress',
            'asset_id': 'T-01',
            'load_percent': 75,
            'voltage_kv': 23.0,
            'current_a': 188,
            'ambient_temp_c': 35,
            'oil_temp_c': 65,
            'winding_temp_c': 95,
            'vibration_mm_s': 2.0,
            'operating_hours': 8760 * 3
        },
        {
            'name': 'Overload Condition',
            'asset_id': 'T-01',
            'load_percent': 115,
            'voltage_kv': 22.5,
            'current_a': 288,
            'ambient_temp_c': 32,
            'oil_temp_c': 70,
            'winding_temp_c': 105,
            'vibration_mm_s': 2.5,
            'operating_hours': 8760 * 3
        },
        {
            'name': 'Critical Condition',
            'asset_id': 'T-01',
            'load_percent': 95,
            'voltage_kv': 22.0,
            'current_a': 238,
            'ambient_temp_c': 40,
            'oil_temp_c': 85,
            'winding_temp_c': 118,
            'vibration_mm_s': 3.0,
            'operating_hours': 8760 * 8  # 8 years - aged transformer
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print("-" * 30)

        result = health_model.predict_health(scenario)

        print(f"📊 HEALTH ASSESSMENT:")
        print(f"   Asset ID: {result['asset_id']}")
        print(f"   Health Score: {result['health_score']}/100")
        print(f"   Failure Probability: {result['failure_probability']*100:.1f}%")
        print(f"   Estimated RUL: {result['estimated_rul_days']:,} days ({result['estimated_rul_days']/365:.1f} years)")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Degradation Type: {result['degradation_type']}")
        print(f"   Anomaly Detected: {result['is_anomaly']}")
        print(f"   Confidence: {result['confidence']*100:.0f}%")

        # Health status interpretation
        health_score = result['health_score']
        if health_score >= 85:
            status = "EXCELLENT"
        elif health_score >= 70:
            status = "GOOD"
        elif health_score >= 55:
            status = "FAIR"
        elif health_score >= 40:
            status = "POOR"
        else:
            status = "CRITICAL"
        print(f"   Status: {status}")