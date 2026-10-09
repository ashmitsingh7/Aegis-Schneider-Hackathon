import { ArcChart, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface HealthGaugeProps {
  healthScore: number;
  size?: number;
}

const HealthGauge = ({ healthScore, size = 120 }: HealthGaugeProps) => {
  // Determine color based on health score
  let gaugeColor = '#ef4444'; // red by default
  if (healthScore >= 80) gaugeColor = '#10b981'; // green
  else if (healthScore >= 60) gaugeColor = '#f59e0b'; // amber
  else if (healthScore >= 40) gaugeColor = '#f97316'; // orange

  return (
    <div className="text-center">
      <h3 className="text-sm font-semibold text-gray-900 mb-2">Asset Health</h3>
      <ResponsiveContainer width={size} height={size}>
        <ArcChart
          data={{ value: healthScore }}
          innerRadius={60}
          outerRadius={80}
          startAngle={180}
          endAngle={0}
        >
          <Cell dataKey="value" fill={gaugeColor} />
          <tooltip>
            <div className="text-left">
              <div className="font-bold">Health Score</div>
              <div className="text-gray-600">{healthScore}/100</div>
            </div>
          </tooltip>
        </ArcChart>
      </ResponsiveContainer>
      <div className="mt-2">
        <p className="text-lg font-bold text-gray-900">{healthScore}/100</p>
        <p className="text-xs text-gray-500">
          {healthScore >= 80 ? 'Excellent' : healthScore >= 60 ? 'Good' : healthScore >= 40 ? 'Fair' : 'Poor'}
        </p>
      </div>
    </div>
  );
};

export default HealthGauge;