type ChartPoint = {
  label: string;
  value: number;
};

type ChartProps = {
  title: string;
  data: ChartPoint[];
  emptyText?: string;
};

function formatLabel(value: string): string {
  if (value.length === 10) {
    return value.slice(5);
  }
  return value;
}

export function SimpleLineChart({
  title,
  data,
  emptyText = "No data yet",
}: ChartProps) {
  const width = 640;
  const height = 220;
  const paddingX = 42;
  const paddingY = 28;
  const maxValue = Math.max(...data.map((item) => item.value), 0);
  const safeMax = maxValue <= 0 ? 1 : maxValue;
  const innerWidth = width - paddingX * 2;
  const innerHeight = height - paddingY * 2;

  const points = data.map((item, index) => {
    const x =
      data.length === 1
        ? width / 2
        : paddingX + (index / (data.length - 1)) * innerWidth;
    const y = paddingY + innerHeight - (item.value / safeMax) * innerHeight;
    return { ...item, x, y };
  });

  const path = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3>{title}</h3>
        <span>Max: {maxValue}</span>
      </div>

      {data.length === 0 ? (
        <p className="muted">{emptyText}</p>
      ) : (
        <svg
          className="chart-svg"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={title}
        >
          <line
            x1={paddingX}
            y1={paddingY}
            x2={paddingX}
            y2={height - paddingY}
          />
          <line
            x1={paddingX}
            y1={height - paddingY}
            x2={width - paddingX}
            y2={height - paddingY}
          />
          <path d={path} className="chart-line" />
          {points.map((point) => (
            <g key={point.label}>
              <circle cx={point.x} cy={point.y} r="4" />
              <text x={point.x} y={height - 8} textAnchor="middle">
                {formatLabel(point.label)}
              </text>
              <text
                x={point.x}
                y={point.y - 10}
                textAnchor="middle"
                className="chart-value-label"
              >
                {point.value}
              </text>
            </g>
          ))}
        </svg>
      )}
    </div>
  );
}

export function SimpleBarChart({
  title,
  data,
  emptyText = "No data yet",
}: ChartProps) {
  const maxValue = Math.max(...data.map((item) => item.value), 0);
  const safeMax = maxValue <= 0 ? 1 : maxValue;

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3>{title}</h3>
        <span>Max: {maxValue}</span>
      </div>

      {data.length === 0 ? (
        <p className="muted">{emptyText}</p>
      ) : (
        <div className="bar-chart" role="img" aria-label={title}>
          {data.map((item) => (
            <div className="bar-row" key={item.label}>
              <span>{formatLabel(item.label)}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${Math.max(4, (item.value / safeMax) * 100)}%`,
                  }}
                />
              </div>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
