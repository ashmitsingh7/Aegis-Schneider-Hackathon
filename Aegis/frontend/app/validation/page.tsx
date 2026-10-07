'use client';

import Link from 'next/link';
import { useState } from 'react';

const initialScenarios = [
  { id: 'baseline', name: 'Healthy Transformer Baseline', status: 'passed', accuracy: 0.94, expected: 'Normal operation' },
  { id: 'early', name: 'Early Stage Degradation', status: 'passed', accuracy: 0.89, expected: 'Preventive maintenance' },
  { id: 'thermal', name: 'Thermal Overload', status: 'pending', accuracy: 0.91, expected: 'Reduce load' },
  { id: 'critical', name: 'Critical Failure Risk', status: 'pending', accuracy: 0.87, expected: 'Emergency intervention' },
] as const;

type Scenario = {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  accuracy: number;
  expected: string;
};

export default function ValidationPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>(initialScenarios.map(item => ({ ...item })));
  const completed = scenarios.filter(item => item.status === 'passed' || item.status === 'failed').length;
  const progress = Math.round((completed / scenarios.length) * 100);

  function runTest(id: string) {
    setScenarios(items => items.map(item => item.id === id ? { ...item, status: 'running' } : item));
    window.setTimeout(() => {
      setScenarios(items => items.map(item => item.id === id ? { ...item, status: 'passed' } : item));
    }, 500);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Validation Testing Suite</h1>
            <p className="text-sm text-gray-500">System validation scenarios for decision intelligence</p>
          </div>
          <Link className="text-sm font-medium text-blue-700" href="/">Back to Dashboard</Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-6 rounded-lg bg-white p-6 shadow">
          <div className="flex justify-between text-sm">
            <h2 className="font-semibold text-gray-900">Validation Progress</h2>
            <span className="text-gray-500">{progress}% complete</span>
          </div>
          <div className="mt-4 h-3 rounded-full bg-gray-200">
            <div className="h-3 rounded-full bg-blue-600" style={{ width: `${progress}%` }} />
          </div>
        </section>

        <section className="space-y-4">
          {scenarios.map(item => (
            <article key={item.id} className="rounded-lg bg-white p-6 shadow">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{item.name}</h3>
                  <p className="mt-1 text-sm text-gray-600">Expected outcome: {item.expected}</p>
                  <p className="mt-2 text-sm text-gray-500">Accuracy: {(item.accuracy * 100).toFixed(0)}%</p>
                </div>
                <div className="flex items-center gap-3">
                  <Status value={item.status} />
                  <button
                    onClick={() => runTest(item.id)}
                    disabled={item.status === 'running'}
                    className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
                  >
                    {item.status === 'running' ? 'Running' : 'Run Test'}
                  </button>
                </div>
              </div>
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}

function Status({ value }: { value: Scenario['status'] }) {
  const classes =
    value === 'passed'
      ? 'bg-green-100 text-green-800'
      : value === 'failed'
        ? 'bg-red-100 text-red-800'
        : value === 'running'
          ? 'bg-yellow-100 text-yellow-800'
          : 'bg-gray-100 text-gray-800';

  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${classes}`}>{value.toUpperCase()}</span>;
}
