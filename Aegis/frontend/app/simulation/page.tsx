'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';

export default function SimulationPage() {
  const [load, setLoad] = useState(89);
  const [ambient, setAmbient] = useState(28);
  const [cooling, setCooling] = useState('normal');

  const result = useMemo(() => {
    const coolingFactor = cooling === 'forced' ? 0.7 : cooling === 'directed' ? 0.8 : 1;
    const rise = (50 * Math.pow(load / 100, 1.6) + ambient - 25) * coolingFactor;
    const winding = ambient + rise;
    const losses = 0.1 + 0.05 * Math.pow(load / 100, 2);
    const efficiency = (load * 0.1 / (load * 0.1 + losses)) * 100;
    const risk = winding > 110 ? 'CRITICAL' : winding > 100 ? 'HIGH' : winding > 90 ? 'MEDIUM' : 'LOW';
    return { rise, winding, oil: ambient + rise * 0.8, losses, efficiency, risk };
  }, [ambient, cooling, load]);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Digital Twin Simulation</h1>
            <p className="text-sm text-gray-500">What-if analysis for transformer asset T-01</p>
          </div>
          <Link className="text-sm font-medium text-blue-700" href="/">Back to Dashboard</Link>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-3 lg:px-8">
        <section className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-lg font-semibold text-gray-900">Simulation Inputs</h2>
          <div className="mt-6 space-y-5">
            <Slider label="Load" value={load} suffix="%" min={50} max={120} onChange={setLoad} />
            <Slider label="Ambient Temp" value={ambient} suffix=" C" min={10} max={45} onChange={setAmbient} />
            <label className="block text-sm font-medium text-gray-700">
              Cooling Mode
              <select
                value={cooling}
                onChange={event => setCooling(event.target.value)}
                className="mt-2 w-full rounded-md border border-gray-300 bg-white px-3 py-2"
              >
                <option value="normal">Normal</option>
                <option value="directed">Directed</option>
                <option value="forced">Forced</option>
              </select>
            </label>
          </div>
        </section>

        <section className="rounded-lg bg-white p-6 shadow lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900">Predicted Results</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <Metric label="Winding Temp" value={`${result.winding.toFixed(1)} C`} />
            <Metric label="Oil Temp" value={`${result.oil.toFixed(1)} C`} />
            <Metric label="Temp Rise" value={`${result.rise.toFixed(1)} C`} />
            <Metric label="Losses" value={`${result.losses.toFixed(3)} kW`} />
            <Metric label="Efficiency" value={`${result.efficiency.toFixed(1)}%`} />
            <Metric label="Risk" value={result.risk} />
          </div>
        </section>
      </main>
    </div>
  );
}

function Slider({
  label,
  value,
  suffix,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  suffix: string;
  min: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="block text-sm font-medium text-gray-700">
      <span className="flex justify-between">
        <span>{label}</span>
        <span>{value}{suffix}</span>
      </span>
      <input className="mt-2 w-full" type="range" min={min} max={max} value={value} onChange={event => onChange(Number(event.target.value))} />
    </label>
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
