import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiService } from '@/lib/apiService';
import type { HealthResponse, RiskResponse, TelemetryData } from '@/types/api';

export default function AssetPage({ params }: { params: { assetId: string } }) {
  const [assetData, setAssetData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [telemetry, setTelemetry] = useState<Array<any>>([]);

  useEffect(() => {
    const fetchAssetData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch health and risk data in parallel
        const [healthResult, riskResult, telemetryResult] = await Promise.all([
          apiService.getAssetHealth(params.assetId, {
            asset_id: params.assetId,
            load_percent: 75.0,
            ambient_temp_c: 30.0,
          }),
          apiService.getAssetRisk(params.assetId, {
            asset_id: params.assetId,
            load_percent: 75.0,
            ambient_temp_c: 30.0,
          }),
          apiService.getAssetTelemetry(params.assetId)
        ]);

        // Transform the data to match the existing UI structure
        const transformedData = {
          healthScore: Math.round(healthResult.health_score),
          failureProbability: Math.round(healthResult.failure_probability),
          rulDays: 0, // We'd need to fetch RUL separately if we wanted to show it here
          riskLevel: riskResult.overall_risk_level,
          load: Math.round(75.0), // From our sample telemetry
          oilTemp: Math.round(riskResult.assessment_details?.oil_temp_c || 75.5),
          windingTemp: Math.round(riskResult.assessment_details?.winding_temp_c || 84),
          vibration: parseFloat(riskResult.assessment_details?.vibration_mm_s || 4.1).toFixed(1),
          explanation: healthResult.degradation_type.replace('_', ' ') +
            ' detected. ' +
            (riskResult.primary_risk_drivers && riskResult.primary_risk_drivers.length > 0
              ? 'Primary risk drivers: ' + riskResult.primary_risk_drivers.join(', ')
              : 'Monitor conditions closely.')
        };

        setAssetData(transformedData);
        setTelemetry(telemetryResult.telemetry || []);
      } catch (err) {
        console.error('Failed to fetch asset data:', err);
        setError('Failed to load asset data. Using fallback data.');

        // Fallback to static data if API call fails
        setAssetData({
          healthScore: 67,
          failureProbability: 31,
          rulDays: 41,
          riskLevel: 'HIGH',
          load: 89,
          oilTemp: 75.5,
          windingTemp: 84,
          vibration: 4.1,
          explanation: 'Load percent and winding temperature are the dominant drivers for the current thermal risk.',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAssetData();
  }, [params.assetId]);

  // Handle case where data is still loading or there was an error
  const asset = assetData || {
    healthScore: 67,
    failureProbability: 31,
    rulDays: 41,
    riskLevel: 'HIGH',
    load: 89,
    oilTemp: 75.5,
    windingTemp: 84,
    vibration: 4.1,
    explanation: 'Load percent and winding temperature are the dominant drivers for the current thermal risk.',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Asset {params.assetId}</h1>
            <p className="text-sm text-gray-500">Transformer health, telemetry, and model explanation</p>
          </div>
          <Link className="text-sm font-medium text-blue-700" href="/">Back to Dashboard</Link>
        </div>
      </header>

      {loading && !assetData && (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Loading Asset Data...</h2>
            <p className="text-lg text-gray-500">Fetching real-time data from the Aegis backend</p>
          </div>
        </div>
      )}

      <main className="mx-auto grid max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-3 lg:px-8">
        <article className="rounded-lg bg-white p-6 shadow lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900">Health Assessment</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <Metric label="Health Score" value={`${asset.healthScore}/100`} />
            <Metric label="Failure Probability" value={`${asset.failureProbability}%`} />
            <Metric label="Remaining Useful Life" value="Fetching..." />
          </div>
        </article>

        <article className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-lg font-semibold text-gray-900">Risk</h2>
          <p className="mt-4 inline-flex rounded-full
            {asset.riskLevel === 'LOW' ? 'bg-green-100 text-green-800'
              : asset.riskLevel === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'}"
            className="px-3 py-1 text-xs font-semibold">
            {asset.riskLevel}
          </p>
          <p className="mt-4 text-sm text-gray-600">
            {asset.explanation}
          </p>
        </article>

        <article className="rounded-lg bg-white p-6 shadow lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900">Live Telemetry</h2>
          {telemetry.length > 0 ? (
            <div className="mt-6 space-y-3">
              <div className="flex flex-col">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">Latest Readings</span>
                  <span className="text-sm text-gray-500">Updated {new Date(telemetry[telemetry.length - 1]?.timestamp || Date.now()).toLocaleTimeString()}</span>
                </div>
                <div className="grid gap-4 sm:grid-cols-4">
                  <Metric label="Load" value={`${Math.round(telemetry[telemetry.length - 1]?.load_percent || 0)}%`} />
                  <Metric label="Oil Temp" value={`${Math.round(telemetry[telemetry.length - 1]?.oil_temp_c || 0)}°C`} />
                  <Metric label="Winding Temp" value={`${Math.round(telemetry[telemetry.length - 1]?.winding_temp_c || 0)}°C`} />
                  <Metric label="Vibration" value={`${parseFloat(telemetry[telemetry.length - 1]?.vibration_mm_s || 0).toFixed(1)} mm/s`} />
                </div>
              </div>
            </div>
          ) : (
            <div className="mt-6 grid gap-4 sm:grid-cols-4">
              <Metric label="Load" value={`${asset.load}%`} />
              <Metric label="Oil Temp" value={`${asset.oilTemp} C`} />
              <Metric label="Winding Temp" value={`${asset.windingTemp} C`} />
              <Metric label="Vibration" value={`${asset.vibration} mm/s`} />
            </div>
          )}
        </article>

        <article className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-lg font-semibold text-gray-900">AI Explanation</h2>
          <p className="mt-4 text-sm text-gray-700">{asset.explanation}</p>
        </article>
      </main>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-gray-50 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 text-xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}
