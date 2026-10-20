/**
 * Recommendation Stats Component
 * 
 * Displays statistics about recommendations.
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface RecommendationStatsProps {
  stats: {
    total: number;
    pending: number;
    approved: number;
    rejected: number;
    completed: number;
    by_type: Record<string, number>;
    by_category: Record<string, number>;
    by_priority: Record<number, number>;
    average_confidence_score: number;
  };
}

export function RecommendationStats({ stats }: RecommendationStatsProps) {
  const statusData = [
    { name: 'Pending', value: stats.pending, color: '#fbbf24' },
    { name: 'Approved', value: stats.approved, color: '#10b981' },
    { name: 'Rejected', value: stats.rejected, color: '#ef4444' },
    { name: 'Completed', value: stats.completed, color: '#3b82f6' },
  ];

  const priorityData = Object.entries(stats.by_priority).map(([priority, count]) => ({
    name: `P${priority}`,
    count,
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Total Recommendations */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-sm text-slate-500 mb-1">Total</div>
        <div className="text-3xl font-bold text-slate-900">{stats.total}</div>
        <div className="text-xs text-slate-500 mt-2">
          Avg Confidence: {(stats.average_confidence_score * 100).toFixed(0)}%
        </div>
      </div>

      {/* Pending */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-sm text-slate-500 mb-1">Pending</div>
        <div className="text-3xl font-bold text-yellow-600">{stats.pending}</div>
        <div className="text-xs text-slate-500 mt-2">Awaiting approval</div>
      </div>

      {/* Approved */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-sm text-slate-500 mb-1">Approved</div>
        <div className="text-3xl font-bold text-green-600">{stats.approved}</div>
        <div className="text-xs text-slate-500 mt-2">Ready for execution</div>
      </div>

      {/* Completed */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-sm text-slate-500 mb-1">Completed</div>
        <div className="text-3xl font-bold text-blue-600">{stats.completed}</div>
        <div className="text-xs text-slate-500 mt-2">Successfully executed</div>
      </div>

      {/* Status Distribution */}
      <div className="bg-white rounded-lg shadow-lg p-6 md:col-span-2">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Status Distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={statusData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
            >
              {statusData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex justify-center gap-4 mt-2">
          {statusData.map((item) => (
            <div key={item.name} className="flex items-center gap-1 text-xs">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
              <span>{item.name}: {item.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Priority Distribution */}
      <div className="bg-white rounded-lg shadow-lg p-6 md:col-span-2">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Priority Distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={priorityData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
