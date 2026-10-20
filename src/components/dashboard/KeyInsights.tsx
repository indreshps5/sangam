/**
 * Key Insights Component
 * Displays AI-generated insights and recommendations
 */

import { useEffect, useState } from 'react';
import { Lightbulb, TrendingUp, TrendingDown, AlertCircle, Loader2 } from 'lucide-react';
import { apiClient } from '../../lib/api';

interface Insight {
  id: string;
  type: 'opportunity' | 'risk' | 'recommendation';
  title: string;
  description: string;
  impact: string;
  priority: 'high' | 'medium' | 'low';
}

export function KeyInsights() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        // Simulated insights - in production, fetch from /recommendations
        const simulatedInsights: Insight[] = [
          {
            id: '1',
            type: 'opportunity',
            title: 'Optimize Mumbai-Delhi Route',
            description: 'Consolidate shipments to reduce costs by 15%',
            impact: 'Save $12,500/month',
            priority: 'high',
          },
          {
            id: '2',
            type: 'risk',
            title: 'Perishables Stock Critical',
            description: 'Bangalore cold storage below minimum threshold',
            impact: 'Risk of stockout in 3 days',
            priority: 'high',
          },
          {
            id: '3',
            type: 'recommendation',
            title: 'Increase Electronics Stock',
            description: 'Demand forecast shows 20% increase next month',
            impact: 'Capture additional $45K revenue',
            priority: 'medium',
          },
          {
            id: '4',
            type: 'opportunity',
            title: 'Negotiate Better Rates',
            description: 'High volume on Mumbai-Bangalore route',
            impact: 'Potential 8% cost reduction',
            priority: 'medium',
          },
        ];

        setInsights(simulatedInsights);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load insights');
        setLoading(false);
      }
    };

    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-blue-100 p-6">
        <div className="flex items-center justify-center h-96">
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

  const getIcon = (type: Insight['type']) => {
    switch (type) {
      case 'opportunity':
        return <TrendingUp className="text-green-600" size={20} />;
      case 'risk':
        return <AlertCircle className="text-red-600" size={20} />;
      case 'recommendation':
        return <Lightbulb className="text-blue-600" size={20} />;
    }
  };

  const getBgColor = (type: Insight['type']) => {
    switch (type) {
      case 'opportunity':
        return 'bg-green-50 border-green-200';
      case 'risk':
        return 'bg-red-50 border-red-200';
      case 'recommendation':
        return 'bg-blue-50 border-blue-200';
    }
  };

  const getPriorityColor = (priority: Insight['priority']) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700';
      case 'medium':
        return 'bg-orange-100 text-orange-700';
      case 'low':
        return 'bg-green-100 text-green-700';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-blue-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <Lightbulb className="text-blue-600" size={20} />
            Key Insights
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            AI-powered recommendations and alerts
          </p>
        </div>
      </div>

      {insights.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-slate-500">
          <Lightbulb size={48} className="mb-3 text-slate-300" />
          <p className="text-sm">No insights available</p>
          <p className="text-xs text-slate-400 mt-1">
            Insights will appear as patterns are detected
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {insights.map((insight) => (
            <div
              key={insight.id}
              className={`p-4 rounded-lg border ${getBgColor(insight.type)}`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">{getIcon(insight.type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <h4 className="font-semibold text-slate-900 text-sm">
                      {insight.title}
                    </h4>
                    <span
                      className={`px-2 py-0.5 text-xs font-semibold rounded-full whitespace-nowrap ${getPriorityColor(
                        insight.priority
                      )}`}
                    >
                      {insight.priority}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mb-2">{insight.description}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-700">
                      Impact:
                    </span>
                    <span className="text-xs text-slate-600">{insight.impact}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-500 text-center">
          Insights are generated from simulated data for demonstration purposes
        </p>
      </div>
    </div>
  );
}
