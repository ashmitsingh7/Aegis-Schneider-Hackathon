'use client';

import Link from 'next/link';
import { useState } from 'react';

const interventions = [
  {
    key: 'CONTINUE_OPERATION',
    label: 'Continue Operation',
    decisionScore: 42,
    riskScore: 65,
    cost: 0,
    downtime: 0,
    lifeImpact: 0,
    reasoning: 'Maintains service but leaves thermal risk elevated.',
  },
  {
    key: 'REDUCE_LOAD',
    label: 'Reduce Load',
    decisionScore: 31,
    riskScore: 38,
    cost: 7500,
    downtime: 0,
    lifeImpact: 8,
    reasoning: 'Cuts thermal stress quickly with minimal operating disruption.',
  },
  {
    key: 'SCHEDULE_MAINTENANCE',
    label: 'Schedule Maintenance',
    decisionScore: 45,
    riskScore: 55,
    cost: 15000,
    downtime: 4,
    lifeImpact: 25,
    reasoning: 'Addresses degradation causes but requires a planned outage.',
  },
  {
    key: 'REPLACE_ASSET',
    label: 'Replace Asset',
    decisionScore: 58,
    riskScore: 70,
    cost: 200000,
    downtime: 8,
    lifeImpact: 365,
    reasoning: 'Resets asset health but carries high cost and downtime.',
  },
];

export default function DecisionCenterPage() {
  const [selectedAsset, setSelectedAsset] = useState('T-01');
  const recommended = 'REDUCE_LOAD';

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Decision Center</h1>
            <p className="text-sm text-gray-500">Multi-criteria intervention analysis</p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={selectedAsset}
              onChange={event => setSelectedAsset(event.target.value)}
              className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm"
            >
              <option value="T-01">Asset T-01</option>
              <option value="T-02">Asset T-02</option>
            </select>
            <Link className="text-sm font-medium text-blue-700" href="/">Back to Dashboard</Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-6 grid gap-4 sm:grid-cols-4">
          <Metric label="Health Score" value="67/100" />
          <Metric label="Risk Level" value="HIGH" tone="red" />
          <Metric label="RUL" value="41 days" />
          <Metric label="Selected Asset" value={selectedAsset} />
        </section>

        <section className="rounded-lg bg-white p-6 shadow">
          <h2 className="text-lg font-semibold text-gray-900">Intervention Options</h2>
          <div className="mt-5 space-y-4">
            {interventions.map(item => {
              const isRecommended = item.key === recommended;
              return (
                <article
                  key={item.key}
                  className={`rounded-lg border-l-4 p-5 ${isRecommended ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-gray-50'}`}
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {item.label}
                        {isRecommended && <span className="ml-2 rounded bg-blue-100 px-2 py-1 text-xs text-blue-800">RECOMMENDED</span>}
                      </h3>
                      <p className="mt-1 text-sm text-gray-600">{item.reasoning}</p>
                    </div>
                    <p className="text-sm font-medium text-gray-700">Score {item.decisionScore}</p>
                  </div>
                  <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
                    <Pair label="Risk" value={item.riskScore.toFixed(1)} />
                    <Pair label="Cost" value={`$${item.cost.toLocaleString()}`} />
                    <Pair label="Downtime" value={`${item.downtime} hours`} />
                    <Pair label="Life Impact" value={`+${item.lifeImpact} days`} />
                  </dl>
                </article>
              );
            })}
          </div>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, tone = 'default' }: { label: string; value: string; tone?: 'default' | 'red' }) {
  return (
    <div className="rounded-lg bg-white p-5 shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`mt-2 text-2xl font-bold ${tone === 'red' ? 'text-red-700' : 'text-gray-900'}`}>{value}</p>
    </div>
  );
}

function Pair({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900">{value}</dd>
    </div>
  );
}
