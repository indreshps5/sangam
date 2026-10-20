/**
 * Stock vs Forecast Demand Chart
 * Line chart showing historical stock levels vs predicted demand
 */

import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, Loader2 } from 'lucide-react';

interface ChartDataPoint {
  date: string;
  stock: number;
  forecast: number;
}

export function StockForecastChart() {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        // Simulated data - in production, fetch from /forecasts/historical
        const simulatedData: ChartDataPoint[] = [
          { date: 'Jan 1', stock: 45000, forecast: 42000 },
          { date: 'Jan 5', stock: 48000, forecast: 45000 },
          { date: 'Jan 10', stock: 52000, forecast: 48000 },
          { date: 'Jan 15', stock: 49000, forecast: 51000 },
          { date: 'Jan 20', stock: 53000, forecast: 54000 },
          { date: 'Jan 25', stock: 56000, forecast: 57000 },
          { date: 'Jan 30', stock: 58000, forecast: 59000 },
          { date: 'Feb 5', stock: 61000, forecast: 62000 },
          { date: 'Feb 10', stock: 64000, forecast: 65000 },
          { date: 'Feb 15', stock: 67000, forecast: 68000 },
          { date: 'Feb 20', stock: 70000, forecast: 71000 },
          { date: 'Feb 25', stock: 73000, forecast: 74000 },
        ];

        setData(simulatedData);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load chart data');
        setLoading(false);
      }
    };

    fetchChartData();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="flex items-center justify-center h-80">
          <Loader2 className="animate-spin text-blue-600" size={32} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-blue-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <TrendingUp className="text-blue-600" size={20} />
            Stock vs. Forecast Demand
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Historical stock levels compared to predicted demand (simulated data)
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#64748b"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value: number) => [value.toLocaleString(), '']}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
          />
          <Line
            type="monotone"
            dataKey="stock"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            name="Actual Stock"
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#10b981"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ fill: '#10b981', r: 4 }}
            name="Forecast Demand"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
