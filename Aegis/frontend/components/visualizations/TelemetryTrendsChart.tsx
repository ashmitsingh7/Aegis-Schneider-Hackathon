import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Label,
} from 'recharts';

interface TelemetryDataPoint {
  timestamp: string;
  load: number;
  oilTemp: number;
  windingTemp: number;
  vibration: number;
}

interface TelemetryTrendsChartProps {
  data: TelemetryDataPoint[];
  height?: number;
}

const TelemetryTrendsChart = ({ data, height = 200 }: TelemetryTrendsChartProps) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-500">No telemetry data available</p>
      </div>
    );
  }

  // Format timestamp for display
  const formattedData = data.map((item) => ({
    ...item,
    timestamp: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  }));

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-900">Telemetry Trends (24h)</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={formattedData}
          margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tick={false} />
          <YAxis
            tick={false}
            domain=['auto', 'auto']
            orientation="left"
          >
            <Label value="Value" position="insideLeft" angle=-90 />
          </YAxis>
          <Tooltip
            formatter={(value) => `${value}`}
            labelFormatter={(label) => label}
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', padding: '4px 8px' }}
            separator={':'}
          />
          <Legend
            verticalAlign="top"
            horizontalAlign="right"
          />
          <Line
            type="monotone"
            dataKey="load"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          >
            <Label
              value="Load (%)"
              position="topLeft"
              offset={[0, -8]}
            />
          </Line>
          <Line
            type="monotone"
            dataKey="oilTemp"
            stroke="#ef4444"
            strokeWidth={2}
            dot={false}
          >
            <Label
              value="Oil Temp (°C)"
              position="topLeft"
              offset={[0, 10]}
            />
          </Line>
          <Line
            type="monotone"
            dataKey="windingTemp"
            stroke="#f97316"
            strokeWidth={2}
            dot={false}
          >
            <Label
              value="Winding Temp (°C)"
              position="topLeft"
              offset={[0, 28]}
            />
          </Line>
          <Line
            type="monotone"
            dataKey="vibration"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={false}
          >
            <Label
              value="Vibration (mm/s)"
              position="topLeft"
              offset={[0, 46]}
            />
          </Line>
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TelemetryTrendsChart;