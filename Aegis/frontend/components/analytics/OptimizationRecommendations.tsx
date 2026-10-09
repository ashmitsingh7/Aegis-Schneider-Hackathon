import { useEffect, useState } from 'react';
import { advancedAnalyticsService } from '@/lib/analytics/advancedAnalyticsService';
import type { OptimizationResult, TelemetryData } from '@/lib/analytics/advancedAnalyticsService';

interface OptimizationRecommendationsProps {
  assetId: string;
  telemetry: TelemetryData;
  constraints?: {
    budget?: number;
    maxDowntimeHours?: number;
    riskThreshold?: string;
  };
}

const OptimizationRecommendations = ({
  assetId,
  telemetry,
  constraints
}: OptimizationRecommendationsProps) => {
  const [optimization, setOptimization] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadOptimization = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await advancedAnalyticsService.optimizeMaintenanceStrategy(
          assetId,
          telemetry,
          constraints
        );
        setOptimization(result);
      } catch (err) {
        console.error('Failed to load optimization recommendations:', err);
        setError('Unable to generate optimization recommendations');
      } finally {
        setLoading(false);
      }
    };

    loadOptimization();
  }, [assetId, telemetry, constraints]);

  if (loading && !optimization) {
    return (
      <div className="text-center py-4">
        <div className="flex items-center justify-center mb-2">
          <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
        <p className="text-sm text-gray-500">Generating optimization recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border-l-4 border-red-200">
        <h3 className="text-sm font-medium text-red-800">Recommendations Unavailable</h3>
        <p className="mt-1 text-xs text-red-600">{error}</p>
      </div>
    );
  }

  if (!optimization) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-500">No optimization data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        Maintenance Optimization
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">AI-Powered</span>
      </h3>

      {/* Recommended Action */}
      <div className="bg-blue-50 border-l-4 border-blue-200 p-3">
        <p className="text-sm font-medium text-blue-800 mb-1">Recommended Strategy:</p>
        <p className="text-lg font-bold text-blue-900 mb-1">
          {optimization.recommendedAction}
        </p>
        <p className="text-xs text-blue-600">
          Confidence: {Math.round(optimization.confidenceScore * 100)}%
        </p>
      </div>

      {/* Expected Benefits */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-900 mb-1">Expected Benefits:</p>
        <div className="space-y-1">
          {optimization.expectedBenefits.map((benefit, index) => (
            <div key={index} className="flex items-start gap-2">
              <div className="flex-shrink-0 mt-0.5 h-2 w-2 bg-green-200"></div>
              <div className="flex-1 space-y-0.5">
                <p className="text-xs font-medium text-gray-800">{benefit.benefit}</p>
                <p className="text-xs text-gray-500">{benefit.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Implementation Plan */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-900 mb-1">Implementation Plan:</p>
        <div className="space-y-1">
          <div className="flex items-start gap-2">
            <div className="flex-shrink-0 mt-0.5 h-2 w-2 bg-yellow-200"></div>
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-800">Timeline:</p>
              <p className="text-xs text-gray-500">{optimization.implementation.timeline}</p>
            </div>
          </div>
          <div className="mt-1">
            <div className="flex items-start gap-2">
              <div className="flex-shrink-0 mt-0.5 h-2 w-2 bg-yellow-200"></div>
              <div className="flex-1">
                <p className="text-xs font-medium text-gray-800">Resources Required:</p>
                <p className="text-xs text-gray-500">{optimization.implementation.resources.join(', ')}</p>
              </div>
            </div>
          </div>
          <div className="mt-1">
            <div className="flex items-start gap-2">
              <div className="flex-shrink-0 mt-0.5 h-2 w-2 bg-yellow-200"></div>
              <div className="flex-1">
                <p className="text-xs font-medium text-gray-800">Prerequisites:</p>
                <p className="text-xs text-gray-500">{optimization.implementation.prerequisites.join(', ')}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ROI Analysis */}
      <div className="border-t pt-3">
        <p className="text-sm font-medium text-gray-900 mb-2">Return on Investment:</p>
        <div className="grid gap-2 text-xs">
          <div>
            <p className="font-medium">Initial Cost:</p>
            <p className="text-gray-600 font-medium">${optimization.roiAnalysis.initialCost.toLocaleString()}</p>
          </div>
          <div>
            <p className="font-medium">Annual Savings:</p>
            <p className="text-gray-600 font-medium">${optimization.roiAnalysis.annualSavings.toLocaleString()}</p>
          </div>
          <div>
            <p className="font-medium">Payback Period:</p>
            <p className="text-gray-600 font-medium">
              {optimization.roiAnalysis.paybackPeriodMonths === 0 ? 'Immediate' :
                optimization.roiAnalysis.paybackPeriodMonths >= 999 ? 'Long-term' :
                `${optimization.roiAnalysis.paybackPeriodMonths.toFixed(1)} months`}
            </p>
          </div>
        </div>
        {optimization.roiAnalysis.annualSavings > 0 && (
          <div className="mt-2 p-2 bg-green-50 rounded">
            <p className="text-xs text-green-600 font-medium">
              {((optimization.roiAnalysis.annualSavings / optimization.roiAnalysis.initialCost) * 100).toFixed(0)}%
              Annual Return on Investment
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OptimizationRecommendations;