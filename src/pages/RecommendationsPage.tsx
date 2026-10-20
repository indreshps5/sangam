/**
 * Recommendations Page
 * 
 * Main page for viewing and managing recommendations.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';
import {
  Lightbulb,
  CheckCircle,
  XCircle,
  Clock,
  Play,
  Filter,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { RecommendationList } from '../components/recommendations/RecommendationList';
import { RecommendationDetail } from '../components/recommendations/RecommendationDetail';
import { RecommendationStats } from '../components/recommendations/RecommendationStats';

interface Recommendation {
  id: string;
  recommendation_type: string;
  category: string;
  priority: number;
  status: string;
  title: string;
  description: string;
  rationale: string;
  suggested_action: string;
  confidence_score: number;
  created_at: string;
  expires_at: string | null;
  affected_depot_id: string | null;
  affected_shipment_id: string | null;
  affected_inventory_item_id: string | null;
  affected_route_id: string | null;
  depot_name: string | null;
  shipment_tracking: string | null;
  inventory_item_name: string | null;
  route_name: string | null;
  supporting_data: any;
  assumptions: any;
  estimated_impact: any;
  source_service: string;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
  executed_at: string | null;
  execution_result: any;
}

interface RecommendationStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  completed: number;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
  by_priority: Record<number, number>;
  average_confidence_score: number;
}

export function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [stats, setStats] = useState<RecommendationStats | null>(null);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadData();
  }, [statusFilter, typeFilter]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load recommendations
      const params: any = { limit: 100 };
      if (statusFilter !== 'all') params.status = statusFilter;
      if (typeFilter !== 'all') params.recommendation_type = typeFilter;

      const recsResponse = await apiClient.request<{ items: Recommendation[] }>(
        '/recommendations',
        { params }
      );
      setRecommendations(recsResponse.items);

      // Load stats
      const statsResponse = await apiClient.request<RecommendationStats>('/recommendations/stats');
      setStats(statsResponse);

      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await apiClient.request('/recommendations/generate', {
        method: 'POST',
      });
      await loadData();
      setGenerating(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recommendations');
      setGenerating(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await apiClient.request(`/recommendations/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ notes: 'Approved via UI' }),
      });
      await loadData();
      if (selectedRecommendation?.id === id) {
        setSelectedRecommendation({ ...selectedRecommendation, status: 'approved' });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve recommendation');
    }
  };

  const handleReject = async (id: string, reason: string) => {
    try {
      await apiClient.request(`/recommendations/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ reason }),
      });
      await loadData();
      if (selectedRecommendation?.id === id) {
        const updated = recommendations.find(r => r.id === id);
        if (updated) setSelectedRecommendation({ ...updated, status: 'rejected' });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject recommendation');
    }
  };

  const handleExecute = async (id: string) => {
    try {
      await apiClient.request(`/recommendations/${id}/execute`, {
        method: 'POST',
        body: JSON.stringify({ notes: 'Executed via UI' }),
      });
      await loadData();
      if (selectedRecommendation?.id === id) {
        const updated = recommendations.find(r => r.id === id);
        if (updated) setSelectedRecommendation({ ...updated, status: 'completed' });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute recommendation');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock size={16} className="text-yellow-500" />;
      case 'approved':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'rejected':
        return <XCircle size={16} className="text-red-500" />;
      case 'completed':
        return <Play size={16} className="text-blue-500" />;
      default:
        return <Clock size={16} className="text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                <Lightbulb className="text-yellow-500" size={28} />
                Recommendations
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                AI-driven logistics recommendations with approval workflows
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="flex items-center gap-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
              >
                <Lightbulb size={18} />
                {generating ? 'Generating...' : 'Generate Recommendations'}
              </button>
              <button
                onClick={loadData}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <RefreshCw size={18} />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-3 text-red-800">
              <AlertCircle size={20} />
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Stats */}
        {stats && <RecommendationStats stats={stats} />}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Filter size={18} className="text-slate-500" />
              <span className="text-sm font-medium text-slate-700">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-1 border border-slate-300 rounded-lg text-sm"
              >
                <option value="all">All</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-slate-700">Type:</span>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-3 py-1 border border-slate-300 rounded-lg text-sm"
              >
                <option value="all">All Types</option>
                <option value="stock_transfer">Stock Transfer</option>
                <option value="replenishment">Replenishment</option>
                <option value="route_change">Route Change</option>
                <option value="shipment_priority">Shipment Priority</option>
                <option value="shortage_review">Shortage Review</option>
              </select>
            </div>
          </div>
        </div>

        {/* Recommendations Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* List */}
          <div className="lg:col-span-1">
            <RecommendationList
              recommendations={recommendations}
              selectedRecommendation={selectedRecommendation}
              onSelectRecommendation={(rec) => setSelectedRecommendation(rec)}
              getStatusIcon={getStatusIcon}
              getStatusColor={getStatusColor}
            />
          </div>

          {/* Detail */}
          <div className="lg:col-span-2">
            {selectedRecommendation ? (
              <RecommendationDetail
                recommendation={selectedRecommendation}
                onApprove={handleApprove}
                onReject={handleReject}
                onExecute={handleExecute}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                <Lightbulb size={64} className="mx-auto mb-4 text-slate-300" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  No Recommendation Selected
                </h3>
                <p className="text-sm text-slate-600">
                  Select a recommendation from the list to view details
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Info Notice */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-xs text-blue-800">
            <strong>Note:</strong> Recommendations are AI-generated suggestions based on current system state.
            All recommendations require approval before execution. Execution is simulated in the prototype.
          </p>
        </div>
      </div>
    </div>
  );
}
