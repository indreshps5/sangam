/**
 * Stock by Commodity Chart
 * Donut chart showing inventory distribution by category
 */

import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Package, Loader2 } from 'lucide-react';
import { apiClient } from '../../lib/api';

interface CommodityData {
  name: string;
  value: number;
  color: string;
}

interface InventoryItem {
  id: string;
  category: string | null;
  quantity_on_hand: number;
}

export function CommodityChart() {
  const [data, setData] = useState<CommodityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  useEffect(() => {
    const fetchCommodityData = async () => {
      try {
        // Fetch inventory items and group by category
        const response = await apiClient.request<{ items: InventoryItem[] }>('/inventory/items', {
          params: { limit: 1000 },
        });

        // Group by category
        const categoryMap = new Map<string, number>();
        response.items.forEach((item) => {
          const category = item.category || 'Uncategorized';
          const current = categoryMap.get(category) || 0;
          categoryMap.set(category, current + item.quantity_on_hand);
        });

        // Convert to chart data
        const chartData: CommodityData[] = Array.from(categoryMap.entries()).map(
          ([name, value], index) => ({
            name,
            value,
            color: COLORS[index % COLORS.length],
          })
        );

        setData(chartData);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load commodity data');
        setLoading(false);
      }
    };

    fetchCommodityData();
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

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="flex items-center justify-center h-80 text-slate-500">
          <p>No inventory data available</p>
        </div>
      </div>
    );
  }

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="bg-white rounded-xl border border-blue-100 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
          <Package className="text-blue-600" size={20} />
          Stock by Commodity
        </h3>
        <p className="text-sm text-slate-500 mt-1">
          Inventory distribution by category
        </p>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value: number) => [value.toLocaleString(), '']}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div key={item.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              ></div>
              <span className="text-slate-700">{item.name}</span>
            </div>
            <span className="text-slate-500 font-medium">
              {((item.value / total) * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
