import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';

interface RiskFactor {
  name: string;
  value: number;
  color: string;
}

interface RiskFactorsChartProps {
  riskFactors: RiskFactor[];
  height?: number;
}

const RiskFactorsChart = ({ riskFactors, height = 200 }: RiskFactorsChartProps) => {
  if (!riskFactors || riskFactors.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-500">No risk factor data available</p>
      </div>
    );
  }

  const COLORS = ['#3b82f6', '#ef4444', '#f97316', '#10b981', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b'];

  const dataWithColors = riskFactors.map((factor, index) => ({
    ...factor,
    color: COLORS[index % COLORS.length],
  }));

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-900">Risk Factor Breakdown</h3>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={dataWithColors}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            labelLine={false}
            label={{ position: 'insideBottom' }}
          >
            {dataWithColors.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => `${value}%`}
            labelFormatter={(label) => `${label}`}
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', padding: '4px 8px' }}
          />
          <Legend
            verticalAlign="bottom"
            horizontalAlign="center"
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskFactorsChart;