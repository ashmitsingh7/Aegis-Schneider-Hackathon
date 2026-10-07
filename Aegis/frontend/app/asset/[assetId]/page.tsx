import Link from 'next/link';

const asset = {
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

export default function AssetPage({ params }: { params: { assetId: string } }) {
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

      <main className="mx-auto grid max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-3 lg:px-8">
        <article className="rounded-lg bg-white p-6 shadow lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900">Health Assessment</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <Metric label="Health Score" value={`${asset.healthScore}/100`} />
            <Metric label="Failure Probability" value={`${asset.failureProbability}%`} />
            <Metric label="Remaining Useful Life" value={`${asset.rulDays} days`} />
          </div>
        </article>

        <article className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-lg font-semibold text-gray-900">Risk</h2>
          <p className="mt-4 inline-flex rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800">{asset.riskLevel}</p>
          <p className="mt-4 text-sm text-gray-600">Thermal degradation is active and should be addressed before load increases.</p>
        </article>

        <article className="rounded-lg bg-white p-6 shadow lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900">Live Telemetry</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-4">
            <Metric label="Load" value={`${asset.load}%`} />
            <Metric label="Oil Temp" value={`${asset.oilTemp} C`} />
            <Metric label="Winding Temp" value={`${asset.windingTemp} C`} />
            <Metric label="Vibration" value={`${asset.vibration} mm/s`} />
          </div>
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
