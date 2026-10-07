#!/usr/bin/env python3
"""
Test script to verify the Aegis backend is working correctly
"""

import requests
import json
import time

def test_backend():
    """Test the Aegis backend endpoints"""
    base_url = "http://localhost:8000"

    print("🧪 Testing Aegis Backend")
    print("=" * 50)

    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test 2: Health assessment
    print("\n2. Testing health assessment...")
    try:
        telemetry_data = {
            "asset_id": "T-01",
            "load_percent": 75,
            "voltage_kv": 23.0,
            "current_a": 188,
            "ambient_temp_c": 30,
            "oil_temp_c": 50,
            "winding_temp_c": 70,
            "vibration_mm_s": 1.5,
            "operating_hours": 8760 * 5
        }
        response = requests.post(f"{base_url}/assets/T-01/health", json=telemetry_data)
        if response.status_code == 200:
            print("✅ Health assessment passed")
            data = response.json()
            print(f"   Health Score: {data['health_score']}/100")
            print(f"   Failure Probability: {data['failure_probability']*100:.1f}%")
            print(f"   Risk Level: {data['risk_level']}")
        else:
            print(f"❌ Health assessment failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health assessment error: {e}")
        return False

    # Test 3: RUL prediction
    print("\n3. Testing RUL prediction...")
    try:
        telemetry_data = {
            "asset_id": "T-01",
            "load_percent": 75,
            "voltage_kv": 23.0,
            "current_a": 188,
            "ambient_temp_c": 30,
            "oil_temp_c": 50,
            "winding_temp_c": 70,
            "vibration_mm_s": 1.5,
            "operating_hours": 8760 * 5
        }
        response = requests.post(f"{base_url}/assets/T-01/rul", json=telemetry_data)
        if response.status_code == 200:
            print("✅ RUL prediction passed")
            data = response.json()
            print(f"   RUL: {data['rul_years']:.1f} years")
            print(f"   Confidence: {data['confidence']*100:.0f}%")
        else:
            print(f"❌ RUL prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ RUL prediction error: {e}")
        return False

    # Test 4: Risk assessment
    print("\n4. Testing risk assessment...")
    try:
        telemetry_data = {
            "asset_id": "T-01",
            "load_percent": 75,
            "voltage_kv": 23.0,
            "current_a": 188,
            "ambient_temp_c": 30,
            "oil_temp_c": 50,
            "winding_temp_c": 70,
            "vibration_mm_s": 1.5,
            "operating_hours": 8760 * 5
        }
        response = requests.post(f"{base_url}/assets/T-01/risk", json=telemetry_data)
        if response.status_code == 200:
            print("✅ Risk assessment passed")
            data = response.json()
            print(f"   Overall Risk: {data['overall_risk_score']}/5.0 ({data['overall_risk_level']})")
            print(f"   Confidence: {data['confidence']*100:.0f}%")
        else:
            print(f"❌ Risk assessment failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Risk assessment error: {e}")
        return False

    # Test 5: Decision optimization
    print("\n5. Testing decision optimization...")
    try:
        telemetry_data = {
            "asset_id": "T-01",
            "load_percent": 75,
            "voltage_kv": 23.0,
            "current_a": 188,
            "ambient_temp_c": 30,
            "oil_temp_c": 50,
            "winding_temp_c": 70,
            "vibration_mm_s": 1.5,
            "operating_hours": 8760 * 5
        }
        response = requests.post(f"{base_url}/assets/T-01/decision", json=telemetry_data)
        if response.status_code == 200:
            print("✅ Decision optimization passed")
            data = response.json()
            print(f"   Recommendation: {data['recommended_intervention']}")
            print(f"   Score: {data['optimal_intervention_score']}/100")
        else:
            print(f"❌ Decision optimization failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Decision optimization error: {e}")
        return False

    # Test 6: Digital twin simulation
    print("\n6. Testing digital twin simulation...")
    try:
        simulation_data = {
            "load_percent": 75,
            "ambient_temp_c": 30,
            "cooling_mode": "normal",
            "harmonic_distortion_thd": 0.05,
            "hours_at_conditions": 1.0,
            "vibration_rms_mm_s": 1.5,
            "dielectric_stress_factor": 1.0,
            "symmetry_imbalance_percent": 0.0,
            "partial_discharge_detected": False
        }
        response = requests.post(f"{base_url}/assets/T-01/simulate", json=simulation_data)
        if response.status_code == 200:
            print("✅ Digital twin simulation passed")
            data = response.json()
            print(f"   Efficiency: {data['efficiency_percent']:.1f}%")
            print(f"   Winding Temp: {data['winding_temp_c']:.1f}°C")
            print(f"   Hot Spot Temp: {data['hotspot_temp_c']:.1f}°C")
        else:
            print(f"❌ Digital twin simulation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Digital twin simulation error: {e}")
        return False

    # Test 7: Summary endpoint
    print("\n7. Testing summary endpoint...")
    try:
        response = requests.get(f"{base_url}/assets/T-01/summary")
        if response.status_code == 200:
            print("✅ Summary endpoint passed")
            data = response.json()
            print(f"   Asset ID: {data['asset_id']}")
            print(f"   Health Score: {data['health']['health_score']}/100")
            print(f"   Recommendation: {data['decision']['recommended_intervention']}")
        else:
            print(f"❌ Summary endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Summary endpoint error: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 All backend tests passed!")
    print("The Aegis platform is working correctly.")
    return True

if __name__ == "__main__":
    # Wait a moment for the server to be ready if needed
    print("Waiting for backend to be ready...")
    time.sleep(2)

    success = test_backend()
    if not success:
        exit(1)