'use client';

import { useState, useEffect } from 'react';

export default function Home() {
  const [apiData, setApiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch summary data from backend API
        const response = await fetch('http://localhost:8000/assets/T-01/summary');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setApiData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
        console.error('Fetch error:', err);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
        <p className="mt-4 text-lg text-gray-600">Loading Aegis Platform...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading Platform</h1>
        <p className="text-gray-600 mb-6">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!apiData) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
        <h1 className="text-2xl font-bold text-gray-600 mb-4">No Data Available</h1>
        <p className="text-gray-600">Waiting for backend data...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-800">
            Aegis - AI-Powered Decision Intelligence Platform
          </h1>
          <p className="mt-2 text-gray-600">
            Monitoring Transformer T-01 • Last updated: {new Date(apiData.timestamp).toLocaleString()}
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Overview */}
        <div className="grid gap-6 mb-8">
          <div className="grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Health Status */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Asset Health</h2>
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 rounded-lg bg-green-100 flex items-center justify-center">
                  <span className="text-green-600 font-bold text-2xl">
                    {Math.round(apiData.health.health_score)}%
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Health Score</p>
                  <p className="text-xl font-bold text-gray-900">
                    {apiData.health.health_score.toFixed(1)}/100
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {getHealthStatus(apiData.health.health_score)}
                  </p>
                </div>
              </div>
            </div>

            {/* Risk Level */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Risk Assessment</h2>
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 rounded-lg
                  {getRiskLevelColor(apiData.risk.overall_risk_level)}
                  flex items-center justify-center">
                  <span className="text-white font-bold text-xl">
                    {apiData.risk.overall_risk_level}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Risk Level</p>
                  <p className="text-xl font-bold text-gray-900">
                    {apiData.risk.overall_risk_score}/5.0
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Confidence: {Math.round(apiData.risk.confidence * 100)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Remaining Life */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Remaining Life</h2>
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 rounded-lg bg-blue-100 flex items-center justify-center">
                  <span className="text-blue-600 font-bold text-2xl">
                    {Math.round(apiData.rul.rul_years)}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Years Remaining</p>
                  <p className="text-xl font-bold text-gray-900">
                    {apiData.rul.rul_years.toFixed(1)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    ({apiData.rul.percent_life_used.toFixed(1)}% used)
                  </p>
                </div>
              </div>
            </div>

            {/* Recommendation */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">AI Recommendation</h2>
              <div className="space-y-3">
                <p className="text-sm font-medium text-gray-600">Recommended Action</p>
                <p className="text-xl font-bold text-gray-900">
                  {apiData.decision.recommended_intervention}
                </p>
                <div className="mt-2 p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">
                    Score: {apiData.decision.optimal_intervention_score.toFixed(1)}/100
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Sections */}
        <div className="grid gap-8">
          {/* Health Details */}
          <section className="bg-white rounded-lg shadow">
            <div className="px-6 py-4">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Health Details</h2>
            </div>
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Failure Probability</h3>
                  <p className="text-lg font-bold text-gray-900">
                    {(apiData.health.failure_probability * 100).toFixed(2)}%
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Degradation Type</h3>
                  <p className="text-lg font-bold text-gray-900 text-capitalize">
                    {apiData.health.degradation_type.replace(/_/g, ' ')}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Anomaly Detected</h3>
                  <p className="text-lg font-bold text-gray-900">
                    {apiData.health.is_anomaly ? 'YES' : 'NO'}
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Risk Breakdown */}
          <section className="bg-white rounded-lg shadow">
            <div className="px-6 py-4">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Risk Analysis</h2>
            </div>
            <div className="px-6 py-4">
              <div className="space-y-4">
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Risk Contributions:</span>
                  <span className="text-sm font-medium text-gray-600">
                    {Object.keys(apiData.risk.risk_contributions_percent)
                      .map(key => `${key.charAt(0).toUpperCase() + key.slice(1)}: ${apiData.risk.risk_contributions_percent[key]}%`)
                      .join(' • ')}
                  </span>
                </div>
                <div className="space-y-2">
                  {Object.entries(apiData.risk.risk_scores).map(([riskType, score]) => (
                    <div key={riskType} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="font-medium text-gray-700">
                        {riskType.charAt(0).toUpperCase() + riskType.slice(1)} Risk
                      </span>
                      <span className="text-lg font-bold
                        {getRiskScoreColor(score)}
                      ">
                        {score}/5.0
                      </span>
                    </div>
                  ))}
                </div>
                {apiData.risk.primary_risk_drivers.length > 0 && (
                  <div className="mt-4 p-3 bg-red-50 rounded">
                    <h3 className="text-sm font-medium text-red-800 mb-2">Primary Risk Drivers</h3>
                    <p className="text-sm text-red-600">
                      {apiData.risk.primary_risk_drivers.map(driver =>
                        driver.charAt(0).toUpperCase() + driver.slice(1).replace(/_/g, ' ')
                      ).join(', ')}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Recommendation Details */}
          <section className="bg-white rounded-lg shadow">
            <div className="px-6 py-4">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Decision Analysis</h2>
            </div>
            <div className="px-6 py-4">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Intervention Scores</h3>
                <div className="space-y-2">
                  {Object.entries(apiData.decision.intervention_scores).map(([key, intervention]) => (
                    <div key={key} className="p-4 rounded-lg
                      {key === apiData.decision.recommended_intervention_key ? 'border-2 border-blue-500' : 'border'}">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-gray-800">{intervention.name}</h4>
                        <span className={`
                          text-xs font-bold
                          ${key === apiData.decision.recommended_intervention_key
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-200 text-gray-600'
                          }
                        `}>
                          {key === apiData.decision.recommended_intervention_key ? 'RECOMMENDED' : ''}
                        </span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2 text-sm">
                        <div>
                          <span className="text-gray-500">Risk:</span>
                          <span className="font-medium">{intervention.risk_score}/100</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Cost:</span>
                          <span className="font-medium">${intervention.cost_score.toFixed(0)}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Downtime:</span>
                          <span className="font-medium">{intervention.downtime_score.toFixed(0)}h</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Life Impact:</span>
                          <span className="font-medium">{intervention.life_impact_score}</span>x
                        </div>
                        <div className="col-span-2 mt-2 pt-2 bb b-gray-200">
                          <span className="text-gray-600">Total Score:</span>
                          <span className="font-bold text-lg">{intervention.total_score}/100</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Explanation */}
          <section className="bg-white rounded-lg shadow">
            <div className="px-6 py-4">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">AI Explanation</h2>
            </div>
            <div className="px-6 py-4">
              <div className="space-y-3">
                {apiData.decision.explanation.map((line, index) => (
                  <p key={index} className="text-sm text-gray-700 leading-relaxed">
                    {line}
                  </p>
                ))}
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Aegis Platform • Powered by AI Decision Intelligence •
            <a href="http://localhost:8000/docs" className="text-blue-600 hover:underline">
              API Documentation
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

// Helper functions
function getHealthStatus(score: number): string {
  if (score >= 85) return "Excellent";
  if (score >= 70) return "Good";
  if (score >= 55) return "Fair";
  if (score >= 40) return "Poor";
  return "Critical";
}

function getRiskLevelColor(level: string): string {
  switch (level) {
    case 'MINIMAL': return 'bg-green-100';
    case 'LOW': return 'bg-yellow-50';
    case 'MEDIUM': return 'bg-orange-50';
    case 'HIGH': return 'bg-red-50';
    case 'CRITICAL': return 'bg-red-100';
    default: return 'bg-gray-100';
  }
}

function getRiskScoreColor(score: number): string {
  if (score >= 4) return 'text-red-600';
  if (score >= 3) return 'text-orange-600';
  if (score >= 2) return 'text-yellow-600';
  return 'text-green-600';
}