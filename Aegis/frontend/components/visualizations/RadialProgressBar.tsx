import { Circle } from 'recharts';

interface RadialProgressBarProps {
  progress: number; // 0-100
  label: string;
  size?: number;
}

const RadialProgressBar = ({ progress, label, size = 100 }: RadialProgressBarProps) => {
  // Determine color based on progress
  let progressColor = '#ef4444'; // red by default
  if (progress >= 80) progressColor = '#10b981'; // green
  else if (progress >= 60) progressColor = '#f59e0b'; // amber
  else if (progress >= 40) progressColor = '#f97316'; // orange

  const strokeDasharray = `${(progress / 100) * 2 * Math.PI * 40}, 251.2`;

  return (
    <div className="text-center">
      <h3 className="text-sm font-semibold text-gray-900 mb-2">{label}</h3>
      <div className="relative inline-flex h-[{size}] w-[{size}]">
        <svg className="h-[{size}] w-[{size}]" viewBox="0 0 100 100">
          {/* Background circle */}
          <Circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            strokeWidth="8"
            stroke="#e5e7eb"
          />
          {/* Progress circle */}
          <Circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            strokeWidth="8"
            stroke={progressColor}
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
            transform="rotate(-90 50 50)"
          />
          {/* Center text */}
          <text
            x="50"
            y="52"
            textAnchor="middle"
            fontSize="16"
            fontWeight="bold"
            fill="#374151"
          >
            {progress}%
          </text>
          <text
            x="50"
            y="70"
            textAnchor="middle"
            fontSize="10"
            fill="#6b7280"
          >
            {label.toLowerCase().includes('life') ? 'Remaining' : ''}
          </text>
        </svg>
      </div>
    </div>
  );
};

export default RadialProgressBar;