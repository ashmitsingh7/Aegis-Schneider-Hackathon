'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';

function buildSeries() {
  return Array.from({ length: 31 }, (_, day) => {
    const progress = day / 30;
    return {
      day,
      health: Math.round(85 - progress * 40),
      failure: Number((0.05 + progress * 0.58).toFixed(2)),
      windingTemp: Math.round(85 + progress * 25),
      rul: Math.round(310 - progress * 260),
      risk: progress > 0.8 ? 'CRITICAL' : progress > 0.45 ? 'HIGH' : progress > 0.2 ? 'MEDIUM' : 'LOW',
    };
  });
}

export default function DegradationScenarioPage() {
  const series = useMemo(buildSeries, []);
  const [day, setDay] = useState(15);
  const current = series[day];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Degradation Sequence Analysis</h1>
            <p className="text-sm text-gray-500">Progressive thermal degradation over 30 days</p>
          </div>
          <Link className="text-sm font-medium text-blue-700" href="/">Back to Dashboard</Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-6 rounded-lg bg-white p-6 shadow">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Scenario Controls</h2>
              <p className="mt-1 text-sm text-gray-600">Day {current.day} of 30</p>
            </div>
            <input
              aria-label="Scenario day"
              type="range"
              min="0"
              max="30"
              value={day}
              onChange={event => setDay(Number(event.target.value))}
              className="w-full sm:w-80"
            />
          </div>
        </section>

        <section className="mb-6 grid gap-4 sm:grid-cols-4">
          <Metric label="Health Score" value={`${current.health}/100`} />
          <Metric label="Failure Probability" value={`${Math.round(current.failure * 100)}%`} />
          <Metric label="Winding Temp" value={`${current.windingTemp} C`} />
          <Metric label="RUL" value={`${current.rul} days`} />
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <article className="rounded-lg bg-white p-6 shadow">
            <h2 className="text-lg font-semibold text-gray-900">Risk Timeline</h2>
            <div className="mt-5 flex h-16 items-end gap-1">
              {series.map(point => (
                <button
                  key={point.day}
                  onClick={() => setDay(point.day)}
                  className={`flex-1 rounded-t ${point.day === day ? 'bg-blue-600' : point.risk === 'CRITICAL' ? 'bg-red-500' : point.risk === 'HIGH' ? 'bg-orange-400' : point.risk === 'MEDIUM' ? 'bg-yellow-400' : 'bg-green-400'}`}
                  style={{ height: `${20 + (100 - point.health)}%` }}
                  aria-label={`Select day ${point.day}`}
                />
              ))}
            </div>
          </article>

          <article className="rounded-lg bg-white p-6 shadow">
            <h2 className="text-lg font-semibold text-gray-900">Condition Comparison</h2>
            <dl className="mt-5 space-y-3 text-sm">
              <Pair label="Initial health" value="85/100" />
              <Pair label="Current health" value={`${current.health}/100`} />
              <Pair label="Projected final health" value="45/100" />
              <Pair label="Current risk" value={current.risk} />
            </dl>
          </article>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white p-5 shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function Pair({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900">{value}</dd>
    </div>
  );
}
