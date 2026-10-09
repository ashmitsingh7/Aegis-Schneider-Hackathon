'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiService } from '@/lib/apiService';
import type { HealthResponse, DecisionResponse, RULResponse, RiskResponse, SimulationResponse } from '@/types/api';
import HealthGauge from '@/components/visualizations/HealthGauge';
import TelemetryTrendsChart from '@/components/visualizations/TelemetryTrendsChart';
import RadialProgressBar from '@/components/visualizations/RadialProgressBar';
import RiskFactorsChart from '@/components/visualizations/RiskFactorsChart';

export default function Home() {
  const [assetData, setAssetData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssetData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch comprehensive asset summary
        const summary = await apiService.getAssetSummary('T-01');

        // Transform the data to match the existing UI structure
        const transformedData = {
          assetId: summary.asset_id,
          name: 'Power Transformer',
          site: 'Main Substation Transformer',
          healthScore: Math.round(summary.health.health_score),
          failureProbability: Math.round(summary.health.failure_probability),
          rulDays: Math.round(summary.rul.rul_days),
          riskLevel: summary.risk.overall_risk_level,
          degradation: summary.health.degradation_type.replace('_', ' '),
          load: Math.round(summary.simulation.load_percent),
          windingTemp: Math.round(summary.simulation.winding_temp_c),
          voltage: Math.round(summary.simulation.actual_voltage_kv * 10), // Convert to volts for display
          current: Math.round(summary.simulation.actual_current_a),
          efficiency: Math.round(summary.simulation.efficiency_percent),
          losses: parseFloat(summary.simulation.total_losses_kw.toFixed(2)),
          recommendation: summary.decision.recommended_intervention.replace('_', ' ').toLowerCase(),
          recommendedScore: Math.round(summary.decision.optimal_intervention_score),
          cost: Math.round(summary.decision.assessment_details?.cost || 7500),
          lifeImpact: Math.round(summary.decision.assessment_details?.lifeImpact || 8),
          reasoning: summary.decision.explanation || [
            'High transformer loading',
            'Elevated winding temperature',
            'Load reduction significantly lowers thermal risk',
          ],
        };

        setAssetData(transformedData);
      } catch (err) {
        console.error('Failed to fetch asset data:', err);
        setError('Failed to load asset data. Using fallback data.');

        // Fallback to static data if API call fails
        setAssetData({
          assetId: 'T-01',
          name: 'Power Transformer',
          site: 'Main Substation Transformer',
          healthScore: 67,
          failureProbability: 31,
          rulDays: 41,
          riskLevel: 'HIGH',
          degradation: 'Thermal stress',
          load: 89,
          windingTemp: 84,
          voltage: 228.5,
          current: 156.8,
          efficiency: 99.9,
          losses: 0.22,
          recommendation: 'Reduce load',
          recommendedScore: 31,
          cost: 7500,
          lifeImpact: 8,
          reasoning: [
            'High transformer loading',
            'Elevated winding temperature',
            'Load reduction significantly lowers thermal risk',
          ],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAssetData();
  }, []);

  // Handle case where data is still loading or there was an error
  const asset = assetData || {
    assetId: 'T-01',
    name: 'Power Transformer',
    site: 'Main Substation Transformer',
    healthScore: 67,
    failureProbability: 31,
    rulDays: 41,
    riskLevel: 'HIGH',
    degradation: 'Thermal stress',
    load: 89,
    windingTemp: 84,
    voltage: 228.5,
    current: 156.8,
    efficiency: 99.9,
    losses: 0.22,
    recommendation: 'Reduce load',
    recommendedScore: 31,
    cost: 7500,
    lifeImpact: 8,
    reasoning: [
      'High transformer loading',
      'Elevated winding temperature',
      'Load reduction significantly lowers thermal risk',
    ],
  };

function RiskBadge({ value }: { value: string }) {
  const classes =
    value === 'LOW'
      ? 'bg-green-100 text-green-800'
      : value === 'MEDIUM'
        ? 'bg-yellow-100 text-yellow-800'
        : 'bg-red-100 text-red-800';

  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${classes}`}>{value}</span>;
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white p-5 shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Aegis Command Center</h1>
            <p className="text-sm text-gray-500">Asset intelligence for critical electrical infrastructure</p>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link className="font-medium text-blue-700" href="/">Dashboard</Link>
            <Link className="text-gray-600 hover:text-gray-900" href="/demo">Demo</Link>
            <Link className="text-gray-600 hover:text-gray-900" href="/decision">Decision</Link>
            <Link className="text-gray-600 hover:text-gray-900" href="/simulation">Simulation</Link>
            <Link className="text-gray-600 hover:text-gray-900" href="/analytics">Analytics</Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-6 rounded-lg border-l-4 border-red-500 bg-red-50 p-4">
          <h2 className="text-sm font-semibold text-red-800">HIGH PRIORITY ALERT</h2>
          <p className="mt-1 text-sm text-red-700">Thermal stress detected. Reduce load and monitor winding temperature.</p>
        </section>

        <section className="grid gap-6">
          {/* Left Column: Health Indicators */}
          <article className="rounded-lg bg-white p-6 shadow w-full md:w-1/2 lg:w-1/3">
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold text-gray-900">
                  Asset {asset.assetId}: {asset.name}
                </h2>
                <div className="flex items-center gap-2">
                  <RiskBadge value={asset.riskLevel} />
                </div>
              </div>

              {/* Health Gauge */}
              <div className="space-y-2">
                <HealthGauge healthScore={asset.healthScore} size={140} />
              </div>

              {/* Key Metrics */}
              <div className="grid gap-3 md:grid-cols-2">
                <MetricCard label="Failure Probability" value={`${asset.failureProbability}%`} />
                <MetricCard label="Degradation" value={asset.degradation} />
                <MetricCard label="Remaining Useful Life" value={`${asset.rulDays} days`} />
                <MetricCard label="Load" value={`${asset.load}%`} />
              </div>
            </div>
          </article>

          {/* Middle Column: Operational Trends & Simulation */}
          <article className="rounded-lg bg-white p-6 shadow w-full md:w-1/2 lg:w-1/3">
            <div className="space-y-4">
              {/* Operating Conditions */}
              <div className="space-y-2">
                <h2 className="text-lg font-semibold text-gray-900">Current Operating Conditions</h2>
                <div className="grid gap-4 md:grid-cols-2">
                  <MetricCard label="Winding Temp" value={`${asset.windingTemp} C`} />
                  <MetricCard label="Oil Temp" value="{(asset.windingTemp - 10)} C" />
                  <MetricCard label="Voltage" value={`${asset.voltage} V`} />
                  <MetricCard label="Current" value={`${asset.current} A`} />
                </div>
              </div>

              {/* Telemetry Trends */}
              <TelemetryTrendsChart
                data={[
                  { timestamp: '00:00', load: 65, oilTemp: 45, windingTemp: 60, vibration: 1.2 },
                  { timestamp: '03:00', load: 58, oilTemp: 42, windingTemp: 55, vibration: 1.0 },
                  { timestamp: '06:00', load: 70, oilTemp: 48, windingTemp: 65, vibration: 1.3 },
                  { timestamp: '09:00', load: 82, oilTemp: 52, windingTemp: 72, vibration: 1.8 },
                  { timestamp: '12:00', load: 89, oilTemp: 58, windingTemp: 78, vibration: 2.1 },
                  { timestamp: '15:00', load: 76, oilTemp: 50, windingTemp: 68, vibration: 1.5 },
                  { timestamp: '18:00', load: 68, oilTemp: 46, windingTemp: 62, vibration: 1.1 },
                  { timestamp: '21:00', load: 60, oilTemp: 44, windingTemp: 58, vibration: 0.9 }
                ]}
              />
            </div>
          </article>

          {/* Right Column: Analytics & Recommendations */}
          <article className="rounded-lg bg-white p-6 shadow w-full md:w-1/2 lg:w-1/3">
            <div className="space-y-4">
              {/* Baseline Simulation */}
              <div className="space-y-2">
                <h2 className="text-lg font-semibold text-gray-900">Baseline Simulation</h2>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Efficiency</span>
                    <span>{asset.efficiency}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Total losses</span>
                    <span>{asset.losses} kW</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Risk level</span>
                    <RiskBadge value={asset.riskLevel} />
                  </div>
                </div>
              </div>

              {/* Risk Factors Breakdown */}
              <div className="space-y-2">
                <RiskFactorsChart
                  riskFactors={[
                    { name: 'Thermal', value: 35 },
                    { name: 'Electrical', value: 25 },
                    { name: 'Insulation', value: 20 },
                    { name: 'Mechanical', value: 10 },
                    { name: 'Aging', value: 10 }
                  ]}
                />
              </div>

              {/* RUL Indicator */}
              <div className="space-y-2">
                <RadialProgressBar
                  progress={Math.min(100, Math.max(0, (asset.rulDays / 365) * 100))}
                  label="Life Remaining"
                  size={100}
                />
              </div>

              {/* AI Recommendation */}
              <div className="space-y-2">
                <h2 className="text-lg font-semibold text-gray-900">AI Recommendation</h2>
                <div className="mt-4 rounded-lg bg-blue-50 p-4">
                  <p className="font-semibold text-blue-900">{asset.recommendation}</p>
                  <p className="text-sm text-blue-800">Decision score: {asset.recommendedScore}</p>
                </div>
                <div className="mt-3 space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Cost</span>
                    <span className="font-medium">${asset.cost.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Life impact</span>
                    <span className="font-medium">+{asset.lifeImpact} days</span>
                  </div>
                </div>
                <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-gray-700">
                  {asset.reasoning.map(reason => <li key={reason}>{reason}</li>)}
                </ul>
              </div>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}
