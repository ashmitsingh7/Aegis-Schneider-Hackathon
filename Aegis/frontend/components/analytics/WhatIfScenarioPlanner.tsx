import { useEffect, useState } from 'react';
import { advancedAnalyticsService } from '@/lib/analytics/advancedAnalyticsService';
import type { WhatIfScenario, TelemetryData } from '@/lib/analytics/advancedAnalyticsService';

interface WhatIfScenarioPlannerProps {
  assetId: string;
  baseTelemetry: TelemetryData;
}

const WhatIfScenarioPlanner = ({ assetId, baseTelemetry }: WhatIfScenarioPlannerProps) => {
  const [scenarios, setScenarios] = useState<WhatIfScenario[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Predefined scenario templates
  const scenarioTemplates = [
    {
      name: 'Continue Operation',
      description: 'Maintain current operating parameters',
      modifications: {} as Partial<TelemetryData>
    },
    {
      name: 'Reduce Load by 10%',
      description: 'Decrease electrical loading to reduce thermal stress',
      modifications: { load_percent: (telemetry: TelemetryData) => Math.max(20, telemetry.load_percent * 0.9) }
    },
    {
      name: 'Reduce Load by 25%',
      description: 'Significantly decrease loading for thermal relief',
      modifications: { load_percent: (telemetry: TelemetryData) => Math.max(20, telemetry.load_percent * 0.75) }
    },
    {
      name: 'Improve Cooling',
      description: 'Enhance cooling system effectiveness',
      modifications: { ambient_temp_c: (telemetry: TelemetryData) => Math.max(10, telemetry.ambient_temp_c - 5) }
    },
    {
      name: 'Reduce Vibration',
      description: 'Improve mechanical stability and alignment',
      modifications: { vibration_mm_s: (telemetry: TelemetryData) => Math.max(0.1, telemetry.vibration_mm_s * 0.7) }
    }
  ];

  useEffect(() => {
    const loadScenarios = async () => {
      try {
        setLoading(true);
        setError(null);

        // Resolve scenario modifications
        const resolvedScenarios = scenarioTemplates.map(template => ({
          ...template,
          modifications: typeof template.modifications === 'function'
            ? template.modifications(baseTelemetry)
            : template.modifications
        }));

        const results = await advancedAnalyticsService.runWhatIfScenarios(assetId, baseTelemetry, resolvedScenarios);
        setScenarios(results);
      } catch (err) {
        console.error('Failed to load what-if scenarios:', err);
        setError('Unable to run what-if scenario analysis');
      } finally {
        setLoading(false);
      }
    };

    loadScenarios();
  }, [assetId, baseTelemetry]);

  if (loading && scenarios.length === 0) {
    return (
      <div className="text-center py-4">
        <div className="flex items-center justify-center mb-2">
          <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
        <p className="text-sm text-gray-500">Running what-if scenario analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border-l-4 border-red-200">
        <h3 className="text-sm font-medium text-red-800">Analysis Unavailable</h3>
        <p className="mt-1 text-xs text-red-600">{error}</p>
      </div>
    );
  }

  if (scenarios.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-500">No scenario data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        What-If Scenario Planning
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">AI-Powered</span>
      </h3>

      <div className="space-y-3">
        {scenarios.map((scenario, index) => {
          const isBest = index === 0; // First scenario is best after sorting
          return (
            <div key={index} className={`border-l-4
              ${isBest ? 'border-blue-500 bg-blue-50' :
                'border-gray-200 bg-gray-50'}

              p-4
            `}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium
                  {isBest ? 'text-blue-800' : 'text-gray-900'"
                >
                  {scenario.scenarioName}
                  {isBest && <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded">RECOMMENDED</span>}
                </h3>
                <p className="text-xs text-gray-500">
                  Confidence: {Math.round(scenario.confidence * 100)}%
                </p>
              </div>
              <p className="text-xs text-gray-600 mb-1">{scenario.description}</p>

              <div className="grid gap-2 text-xs">
                <div className="flex items-center gap-1">
                  <div className="h-2 w-2
                    {scenario.predictedOutcome.healthScoreChange > 0 ? 'bg-green-200' :
                      scenario.predictedOutcome.healthScoreChange < 0 ? 'bg-red-200' :
                        'bg-gray-200'"
                  ></div>
                  <span className="text-xs">Health Score:</span>
                  <span className="font-medium ml-1
                    {scenario.predictedOutcome.healthScoreChange > 0 ? 'text-green-800' :
                      scenario.predictedOutcome.healthScoreChange < 0 ? 'text-red-800' :
                        'text-gray-600'"
                  >
                    {scenario.predictedOutcome.healthScoreChange > 0 ? '+' : ''}
                    {scenario.predictedOutcome.healthScoreChange}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-2 w-2
                    {scenario.predictedOutcome.rulChangeDays > 0 ? 'bg-green-200' :
                      scenario.predictedOutcome.rulChangeDays < 0 ? 'bg-red-200' :
                        'bg-gray-200'"
                  ></div>
                  <span className="text-xs">RUL Change:</span>
                  <span className="font-medium ml-1
                    {scenario.predictedOutcome.rulChangeDays > 0 ? 'text-green-800' :
                      scenario.predictedOutcome.rulChangeDays < 0 ? 'text-red-800' :
                        'text-gray-600'"
                  >
                    {scenario.predictedOutcome.rulChangeDays > 0 ? '+' : ''}
                    {scenario.predictedOutcome.rulChangeDays} days
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-2 w-2
                    {scenario.predictedOutcome.costImpact < 0 ? 'bg-green-200' :
                      scenario.predictedOutcome.costImpact > 0 ? 'bg-red-200' :
                        'bg-gray-200'"
                  ></div>
                  <span className="text-xs">Cost Impact:</span>
                  <span className="font-medium ml-1
                    {scenario.predictedOutcome.costImpact < 0 ? 'text-green-800' :
                      scenario.predictedOutcome.costImpact > 0 ? 'text-red-800' :
                        'text-gray-600'"
                  >
                    {scenario.predictedOutcome.costImpact < 0 ? '-' : '$'}
                    {Math.abs(scenario.predictedOutcome.costImpact).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="mt-2 p-2 bg-gray-50 rounded">
                <p className="text-xs text-gray-600 font-medium">Parameters:</p>
                <div className="flex flex-wrap gap-1 text-xs">
                  {Object.entries(scenario.parameters).map(([param, value]) => (
                    <span key={param} className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">
                      {param}: {value}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WhatIfScenarioPlanner;