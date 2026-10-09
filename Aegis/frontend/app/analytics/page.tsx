'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiService } from '@/lib/apiService';
import { advancedAnalyticsService } from '@/lib/analytics/advancedAnalyticsService';
import type { HealthResponse, TelemetryData } from '@/types/api';
import RootCauseAnalysisPanel from '@/components/analytics/RootCauseAnalysisPanel';
import WhatIfScenarioPlanner from '@/components/analytics/WhatIfScenarioPlanner';
import OptimizationRecommendations from '@/components/analytics/OptimizationRecommendations';

export default function AnalyticsPage() {
  const [assetData, setAssetData] = useState<any>(null);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get asset summary and telemetry
        const [summaryResult, telemetryResult] = await Promise.all([
          apiService.getAssetSummary('T-01'),
          apiService.getAssetTelemetry('T-01')
        ]);

        // Extract latest telemetry reading
        const latestTelemetry = telemetryResult.telemetry.length > 0
          ? telemetryResult.telemetry[telemetryResult.telemetry.length - 1]
          : {
              asset_id: 'T-01',
              load_percent: 75.0,
              voltage_kv: 23.0,
              current_a: 188.0,
              ambient_temp_c: 30.0,
              oil_temp_c: 50.0,
              winding_temp_c: 70.0,
              vibration_mm_s: 1.5,
              operating_hours: 8760 * 5
            };

        // Format telemetry for our services
        const formattedTelemetry: TelemetryData = {
          asset_id: latestTelemetry.asset_id,
          load_percent: latestTelemetry.load_percent,
          voltage_kv: latestTelemetry.voltage_kv,
          current_a: latestTelemetry.current_a,
          ambient_temp_c: latestTelemetry.ambient_temp_c,
          oil_temp_c: latestTelemetry.oil_temp_c,
          winding_temp_c: latestTelemetry.winding_temp_c,
          vibration_mm_s: latestTelemetry.vibration_mm_s,
          operating_hours: latestTelemetry.operating_hours
        };

        setAssetData(summaryResult);
        setTelemetry(formattedTelemetry);
      } catch (err) {
        console.error('Failed to load analytics data:', err);
        setError('Unable to load analytics data');

        // Fallback data
        setAssetData({
          asset_id: 'T-01',
          health: {
            asset_id: 'T-01',
            health_score: 67,
            failure_probability: 0.31,
            estimated_rul_days: 41,
            risk_level: 'HIGH',
            degradation_type: 'thermal_stress',
            is_anomaly: false,
            confidence: 0.85
          }
        } as any);

        setTelemetry({
          asset_id: 'T-01',
          load_percent: 75.0,
          voltage_kv: 23.0,
          current_a: 188.0,
          ambient_temp_c: 30.0,
          oil_temp_c: 50.0,
          winding_temp_c: 70.0,
          vibration_mm_s: 1.5,
          operating_hours: 8760 * 5
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading && !assetData && !telemetry) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="h-6 w-6 border-2 border-primary border-t-transparent rounded-full animate-spin mb-3"></div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Loading Analytics Dashboard</h2>
          <p className="text-lg text-gray-500">Initializing advanced analytics engine...</p>
        </div>
      </div>
    );
  }

  // Handle case where data is still loading or there was an error
  const asset = assetData || {
    asset_id: 'T-01',
    health: {
      asset_id: 'T-01',
      health_score: 67,
      failure_probability: 0.31,
      estimated_rul_days: 41,
      risk_level: 'HIGH',
      degradation_type: 'thermal_stress',
      is_anomaly: false,
      confidence: 0.85
    }
  } as any;

  const tel = telemetry || {
    asset_id: 'T-01',
    load_percent: 75.0,
    voltage_kv: 23.0,
    current_a: 188.0,
    ambient_temp_c: 30.0,
    oil_temp_c: 50.0,
    winding_temp_c: 70.0,
    vibration_mm_s: 1.5,
    operating_hours: 8760 * 5
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Advanced Analytics Center</h1>
            <p className="text-sm text-gray-500">AI-powered diagnostic and optimization capabilities</p>
          </div>
          <Link className="text-sm font-medium text-blue-700" href="/">Back to Dashboard</Link>
        </div>
      </header>

      {error && (
        <div className="p-4 mb-4 bg-red-50 border-l-4 border-red-200">
          <h3 className="text-sm font-medium text-red-800">Data Loading Error</h3>
          <p className="mt-1 text-xs text-red-600">{error}</p>
        </div>
      )}

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-6 md:grid-cols-2">
          {/* Root Cause Analysis */}
          <article className="rounded-lg bg-white p-6 shadow">
            <RootCauseAnalysisPanel
              assetId={asset.asset_id}
              telemetry={tel}
            />
          </article>

          {/* What-If Scenario Planning */}
          <article className="rounded-lg bg-white p-6 shadow">
            <WhatIfScenarioPlanner
              assetId={asset.asset_id}
              baseTelemetry={tel}
            />
          </article>

          {/* Optimization Recommendations - Full width */}
          <article className="rounded-lg bg-white p-6 shadow col-span-2">
            <OptimizationRecommendations
              assetId={asset.asset_id}
              telemetry={tel}
              constraints={{
                budget: 50000, // $50k budget constraint
                maxDowntimeHours: 4, // Max 4 hours downtime
                riskThreshold: 'MEDIUM' // Don't exceed medium risk
              }}
            />
          </article>
        </div>
      </main>
    </div>
  );
}