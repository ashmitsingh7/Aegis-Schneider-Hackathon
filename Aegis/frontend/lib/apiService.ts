import type {
  HealthResponse,
  RULResponse,
  RiskResponse,
  DecisionResponse,
  SimulationResponse,
  SummaryResponse,
  TelemetryData,
  SimulationRequest
} from '@/types/api';

// Base URL for the API - in production this would come from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Service class for communicating with the Aegis backend API
 */
class ApiService {
  /**
   * Check if the backend API is healthy
   */
  async healthCheck(): Promise<{ status: string; timestamp: string; models_loaded: Record<string, boolean> }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get asset health assessment
   */
  async getAssetHealth(assetId: string, telemetry: TelemetryData): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}/health`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(telemetry),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get health data: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get asset Remaining Useful Life prediction
   */
  async getAssetRUL(assetId: string, telemetry: TelemetryData): Promise<RULResponse> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}/rul`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(telemetry),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get RUL data: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get comprehensive asset risk assessment
   */
  async getAssetRisk(assetId: string, telemetry: TelemetryData): Promise<RiskResponse> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}/risk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(telemetry),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get risk data: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get optimal intervention recommendation
   */
  async getAssetDecision(assetId: string, telemetry: TelemetryData): Promise<DecisionResponse> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}/decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(telemetry),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get decision data: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Run digital twin simulation for what-if analysis
   */
  async simulateAsset(assetId: string, simulationRequest: SimulationRequest): Promise<SimulationResponse> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(simulationRequest),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to run simulation: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get comprehensive asset summary
   */
  async getAssetSummary(assetId: string): Promise<SummaryResponse> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}/summary`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get asset summary: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get time-series telemetry data for asset
   */
  async getAssetTelemetry(assetId: string): Promise<{ asset_id: string; telemetry: Array<any>; count: number; time_range: { start: string; end: string } }> {
    const response = await fetch(`${API_BASE_URL}/assets/${assetId}/telemetry`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get telemetry data: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get information about loaded models
   */
  async getModelsInfo(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/models/info`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to get models info: ${response.status}`);
    }
    return response.json();
  }
}

// Export a singleton instance
export const apiService = new ApiService();

// Export types for convenience
export type {
  HealthResponse,
  RULResponse,
  RiskResponse,
  DecisionResponse,
  SimulationResponse,
  SummaryResponse,
  TelemetryData,
  SimulationRequest
};