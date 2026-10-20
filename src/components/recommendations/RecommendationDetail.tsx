/**
 * Recommendation Detail Component
 * 
 * Displays detailed information about a recommendation.
 */

import { useState } from 'react';
import {
  Lightbulb,
  CheckCircle,
  XCircle,
  Play,
  AlertCircle,
  TrendingUp,
  FileText,
} from 'lucide-react';

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

interface RecommendationDetailProps {
  recommendation: Recommendation;
  onApprove: (id: string) => void;
  onReject: (id: string, reason: string) => void;
  onExecute: (id: string) => void;
}

export function RecommendationDetail({
  recommendation,
  onApprove,
  onReject,
  onExecute,
}: RecommendationDetailProps) {
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      stock_transfer: 'Stock Transfer',
      replenishment: 'Replenishment',
      route_change: 'Route Change',
      shipment_priority: 'Shipment Priority',
      shortage_review: 'Shortage Review',
      capacity_optimization: 'Capacity Optimization',
      cost_reduction: 'Cost Reduction',
      risk_mitigation: 'Risk Mitigation',
    };
    return labels[type] || type;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityLabel = (priority: number) => {
    const labels: Record<number, string> = {
      1: 'Critical',
      2: 'High',
      3: 'Medium',
      4: 'Low',
      5: 'Minimal',
    };
    return labels[priority] || 'Unknown';
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return 'text-red-600 bg-red-50';
      case 2:
        return 'text-orange-600 bg-orange-50';
      case 3:
        return 'text-yellow-600 bg-yellow-50';
      case 4:
        return 'text-blue-600 bg-blue-50';
      case 5:
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const handleReject = () => {
    if (rejectionReason.trim()) {
      onReject(recommendation.id, rejectionReason);
      setShowRejectModal(false);
      setRejectionReason('');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h2 className="text-xl font-bold text-slate-900 mb-2">
              {recommendation.title}
            </h2>
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(recommendation.status)}`}>
                {recommendation.status.toUpperCase()}
              </span>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getPriorityColor(recommendation.priority)}`}>
                {getPriorityLabel(recommendation.priority)} Priority
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                {getTypeLabel(recommendation.recommendation_type)}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-500">Confidence</div>
            <div className="text-2xl font-bold text-slate-900">
              {(recommendation.confidence_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-4">{recommendation.description}</p>

        {/* Affected Entities */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          {recommendation.depot_name && (
            <div>
              <span className="text-slate-500">Depot:</span>{' '}
              <span className="font-medium">{recommendation.depot_name}</span>
            </div>
          )}
          {recommendation.shipment_tracking && (
            <div>
              <span className="text-slate-500">Shipment:</span>{' '}
              <span className="font-medium">{recommendation.shipment_tracking}</span>
            </div>
          )}
          {recommendation.inventory_item_name && (
            <div>
              <span className="text-slate-500">Item:</span>{' '}
              <span className="font-medium">{recommendation.inventory_item_name}</span>
            </div>
          )}
          {recommendation.route_name && (
            <div>
              <span className="text-slate-500">Route:</span>{' '}
              <span className="font-medium">{recommendation.route_name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Rationale */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
          <FileText size={20} className="text-blue-600" />
          Rationale
        </h3>
        <p className="text-sm text-slate-700">{recommendation.rationale}</p>
      </div>

      {/* Suggested Action */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
          <Lightbulb size={20} className="text-yellow-600" />
          Suggested Action
        </h3>
        <p className="text-sm text-slate-700">{recommendation.suggested_action}</p>
      </div>

      {/* Supporting Data */}
      {recommendation.supporting_data && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
            <TrendingUp size={20} className="text-green-600" />
            Supporting Data
          </h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(recommendation.supporting_data).map(([key, value]) => (
              <div key={key}>
                <span className="text-slate-500">{key.replace(/_/g, ' ')}:</span>{' '}
                <span className="font-medium">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assumptions */}
      {recommendation.assumptions && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">
            Assumptions
          </h3>
          <ul className="space-y-2">
            {Object.entries(recommendation.assumptions).map(([key, value]) => (
              <li key={key} className="flex items-start gap-2 text-sm">
                <AlertCircle size={16} className="text-yellow-600 mt-0.5" />
                <div>
                  <span className="font-medium">{key.replace(/_/g, ' ')}:</span>{' '}
                  <span className="text-slate-700">{String(value)}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Estimated Impact */}
      {recommendation.estimated_impact && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
            <TrendingUp size={20} className="text-purple-600" />
            Estimated Impact
          </h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(recommendation.estimated_impact).map(([key, value]) => (
              <div key={key}>
                <span className="text-slate-500">{key.replace(/_/g, ' ')}:</span>{' '}
                <span className="font-medium">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rejection Reason */}
      {recommendation.status === 'rejected' && recommendation.rejection_reason && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-red-900 mb-2">Rejection Reason</h3>
          <p className="text-sm text-red-800">{recommendation.rejection_reason}</p>
        </div>
      )}

      {/* Execution Result */}
      {recommendation.status === 'completed' && recommendation.execution_result && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Execution Result</h3>
          <pre className="text-xs text-blue-800 overflow-x-auto">
            {JSON.stringify(recommendation.execution_result, null, 2)}
          </pre>
        </div>
      )}

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center gap-3">
          {recommendation.status === 'pending' && (
            <>
              <button
                onClick={() => onApprove(recommendation.id)}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <CheckCircle size={18} />
                Approve
              </button>
              <button
                onClick={() => setShowRejectModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                <XCircle size={18} />
                Reject
              </button>
            </>
          )}
          {recommendation.status === 'approved' && (
            <button
              onClick={() => onExecute(recommendation.id)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Play size={18} />
              Execute
            </button>
          )}
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">
              Reject Recommendation
            </h3>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Enter reason for rejection..."
              rows={4}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500"
            />
            <div className="flex items-center gap-3 mt-4">
              <button
                onClick={handleReject}
                disabled={!rejectionReason.trim()}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectionReason('');
                }}
                className="flex-1 px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
