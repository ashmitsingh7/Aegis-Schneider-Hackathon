'use client';

import Link from 'next/link';
import { useState } from 'react';

const scenarios = [
  {
    id: 'overview',
    name: 'Aegis System Overview',
    duration: 15,
    assets: ['T-01'],
    description: 'Walk through the dashboard, asset health, simulation, decisions, and validation.',
    steps: [
      { title: 'Command Center', action: '/', detail: 'Review health score, risk state, and the active recommendation.' },
      { title: 'Asset Deep Dive', action: '/asset/T-01', detail: 'Inspect telemetry, degradation indicators, and model explanations.' },
      { title: 'Decision Center', action: '/decision', detail: 'Compare intervention options by risk, cost, downtime, and life impact.' },
      { title: 'Digital Twin', action: '/simulation', detail: 'Adjust operating assumptions and view predicted thermal impact.' },
      { title: 'Validation', action: '/validation', detail: 'Show test scenarios and validation metrics for the decision engine.' },
    ],
  },
  {
    id: 'thermal',
    name: 'Thermal Degradation Response',
    duration: 10,
    assets: ['T-01', 'T-02'],
    description: 'Demonstrate how Aegis responds to sustained overload and rising winding temperature.',
    steps: [
      { title: 'Degradation Sequence', action: '/degradation', detail: 'Play through the temperature and health decline timeline.' },
      { title: 'Decision Review', action: '/decision', detail: 'Select the recommended action and explain its tradeoffs.' },
      { title: 'Simulation Check', action: '/simulation', detail: 'Reduce load and compare the improved risk profile.' },
    ],
  },
];

export default function DemoPage() {
  const [scenarioId, setScenarioId] = useState(scenarios[0].id);
  const [stepIndex, setStepIndex] = useState(0);
  const scenario = scenarios.find(item => item.id === scenarioId) ?? scenarios[0];
  const step = scenario.steps[stepIndex];

  function selectScenario(nextScenarioId: string) {
    setScenarioId(nextScenarioId);
    setStepIndex(0);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Demonstration Mode</h1>
            <p className="text-sm text-gray-500">Guided tours of Aegis capabilities</p>
          </div>
          <Link className="text-sm font-medium text-blue-700" href="/">Back to Dashboard</Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-4">
            {scenarios.map(item => (
              <button
                key={item.id}
                onClick={() => selectScenario(item.id)}
                className={`w-full rounded-lg p-5 text-left shadow ${item.id === scenario.id ? 'bg-blue-600 text-white' : 'bg-white text-gray-900'}`}
              >
                <h2 className="font-semibold">{item.name}</h2>
                <p className={`mt-2 text-sm ${item.id === scenario.id ? 'text-blue-50' : 'text-gray-600'}`}>{item.description}</p>
                <p className={`mt-3 text-xs ${item.id === scenario.id ? 'text-blue-100' : 'text-gray-500'}`}>
                  {item.duration} minutes · {item.steps.length} steps · Assets: {item.assets.join(', ')}
                </p>
              </button>
            ))}
          </div>

          <article className="rounded-lg bg-white p-6 shadow lg:col-span-2">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{scenario.name}</h2>
                <p className="mt-2 text-gray-600">{scenario.description}</p>
              </div>
              <p className="text-sm text-gray-500">Step {stepIndex + 1} of {scenario.steps.length}</p>
            </div>

            <div className="mt-6 h-2 rounded-full bg-gray-200">
              <div className="h-2 rounded-full bg-blue-600" style={{ width: `${((stepIndex + 1) / scenario.steps.length) * 100}%` }} />
            </div>

            <div className="mt-8 rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900">{step.title}</h3>
              <p className="mt-2 text-gray-700">{step.detail}</p>
              <Link className="mt-5 inline-flex rounded-md bg-green-600 px-4 py-2 font-medium text-white hover:bg-green-700" href={step.action}>
                Open Step
              </Link>
            </div>

            <div className="mt-6 flex justify-between">
              <button
                onClick={() => setStepIndex(index => Math.max(0, index - 1))}
                disabled={stepIndex === 0}
                className="rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setStepIndex(index => Math.min(scenario.steps.length - 1, index + 1))}
                disabled={stepIndex === scenario.steps.length - 1}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}
