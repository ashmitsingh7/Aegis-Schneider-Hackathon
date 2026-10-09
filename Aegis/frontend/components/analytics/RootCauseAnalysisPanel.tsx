import { useEffect, useState } from 'react';
import { advancedAnalyticsService } from '@/lib/analytics/advancedAnalyticsService';
import type { RootCauseAnalysis, TelemetryData } from '@/lib/analytics/advancedAnalyticsService';

interface RootCauseAnalysisPanelProps {
  assetId: string;
  telemetry: TelemetryData;
}

const RootCauseAnalysisPanel = ({ assetId, telemetry }: RootCauseAnalysisPanelProps) => {
  const [analysis, setAnalysis] = useState<RootCauseAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await advancedAnalyticsService.performRootCauseAnalysis(assetId, telemetry);
        setAnalysis(result);
      } catch (err) {
        console.error('Failed to load root cause analysis:', err);
        setError('Unable to perform root cause analysis');
      } finally {
        setLoading(false);
      }
    };

    loadAnalysis();
  }, [assetId, telemetry]);

  if (loading && !analysis) {
    return (
      <div className="text-center py-4">
        <div className="flex items-center justify-center mb-2">
          <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
        <p className="text-sm text-gray-500">Performing root cause analysis...</p>
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

  if (!analysis) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-500">No analysis data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        Root Cause Analysis
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">AI-Powered</span>
      </h3>

      {/* Primary Cause */}
      <div className="bg-yellow-50 border-l-4 border-yellow-200 p-3">
        <p className="text-sm font-medium text-yellow-800 mb-1">Primary Cause:</p>
        <p className="text-xs text-yellow-700">{analysis.primaryCause}</p>
      </div>

      {/* Contributing Factors */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-900 mb-1">Contributing Factors:</p>
        <div className="space-y-1">
          {analysis.contributingFactors.map((factor, index) => (
            <div key={index} className="flex items-center gap-2 text-xs">
              <div className="h-2 w-2 bg-primary-600 rounded"></div>
              <span>{factor.factor}</span>
              <span className="ml-auto text-gray-500">
                {(factor.impact * 100).toFixed(0)}% impact
              </span>
              <span className="ml-2 text-xs text-gray-400">
                ({Math.round(factor.confidence * 100)}% confidence)
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-900 mb-1">Recommended Actions:</p>
        <div className="space-y-1">
          {analysis.recommendedActions.map((action, index) => (
            <div key={index} className="flex items-start gap-2">
              <div className="flex-shrink-0 mt-0.5 h-2 w-2
                {action.priority === 'high' ? 'bg-red-200'
                  : action.priority === 'medium' ? 'bg-yellow-200'
                    : 'bg-green-200'"
              ></div>
              <div className="flex-1 space-y-0.5">
                <p className="text-xs font-medium
                  {action.priority === 'high' ? 'text-red-800'
                    : action.priority === 'medium' ? 'text-yellow-800'
                      : 'text-green-800'"
                >{action.action}</p>
                <p className="text-xs text-gray-500">
                  Expected impact: +{action.expectedEffect}%{' '}
                  <span className="font-medium">
                    {action.priority === 'high' ? '(High)' :
                      action.priority === 'medium' ? '(Medium)' : '(Low)'}
                  </span>
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="border-t pt-3">
        <p className="text-sm font-medium text-gray-900 mb-2">Remediation Timeline:</p>
        <div className="grid gap-2 text-xs">
          <div>
            <p className="font-medium">Immediate:</p>
            <p className="text-gray-600">{analysis.timeline.immediate}</p>
          </div>
          <div>
            <p className="font-medium">Short-term:</p>
            <p className="text-gray-600">{analysis.timeline.shortTerm}</p>
          </div>
          <div>
            <p className="font-medium">Long-term:</p>
            <p className="text-gray-600">{analysis.timeline.longTerm}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RootCauseAnalysisPanel;