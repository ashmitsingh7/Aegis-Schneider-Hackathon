'use client';

import Link from 'next/link';

const asset = {
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
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-6 rounded-lg border-l-4 border-red-500 bg-red-50 p-4">
          <h2 className="text-sm font-semibold text-red-800">HIGH PRIORITY ALERT</h2>
          <p className="mt-1 text-sm text-red-700">Thermal stress detected. Reduce load and monitor winding temperature.</p>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <article className="rounded-lg bg-white p-6 shadow lg:col-span-2">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Asset {asset.assetId}: {asset.name}
                </h2>
                <p className="mt-1 text-sm text-gray-500">{asset.site}</p>
              </div>
              <RiskBadge value={asset.riskLevel} />
            </div>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <MetricCard label="Health Score" value={`${asset.healthScore}/100`} />
              <MetricCard label="Failure Probability" value={`${asset.failureProbability}%`} />
              <MetricCard label="Remaining Useful Life" value={`${asset.rulDays} days`} />
              <MetricCard label="Degradation" value={asset.degradation} />
            </div>
          </article>

          <article className="rounded-lg bg-white p-6 shadow">
            <h2 className="text-lg font-semibold text-gray-900">Current Operating Conditions</h2>
            <div className="mt-5 grid grid-cols-2 gap-4 text-center">
              <MetricCard label="Load" value={`${asset.load}%`} />
              <MetricCard label="Winding Temp" value={`${asset.windingTemp} C`} />
              <MetricCard label="Voltage" value={`${asset.voltage} V`} />
              <MetricCard label="Current" value={`${asset.current} A`} />
            </div>
          </article>

          <article className="rounded-lg bg-white p-6 shadow">
            <h2 className="text-lg font-semibold text-gray-900">Baseline Simulation</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between"><dt className="text-gray-500">Efficiency</dt><dd>{asset.efficiency}%</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Total losses</dt><dd>{asset.losses} kW</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Risk level</dt><dd><RiskBadge value={asset.riskLevel} /></dd></div>
            </dl>
          </article>

          <article className="rounded-lg bg-white p-6 shadow lg:col-span-2">
            <h2 className="text-lg font-semibold text-gray-900">AI Recommendation</h2>
            <div className="mt-4 rounded-lg bg-blue-50 p-4">
              <p className="font-semibold text-blue-900">{asset.recommendation}</p>
              <p className="text-sm text-blue-800">Decision score: {asset.recommendedScore}</p>
            </div>
            <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
              <div><dt className="text-gray-500">Cost</dt><dd className="font-medium">${asset.cost.toLocaleString()}</dd></div>
              <div><dt className="text-gray-500">Life impact</dt><dd className="font-medium">+{asset.lifeImpact} days</dd></div>
            </dl>
            <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-gray-700">
              {asset.reasoning.map(reason => <li key={reason}>{reason}</li>)}
            </ul>
          </article>
        </section>
      </main>
    </div>
  );
}
