/**
 * Recommendation List Component
 * 
 * Displays a list of recommendations with status indicators.
 */

interface RecommendationListProps {
  recommendations: any[];
  selectedRecommendation: any;
  onSelectRecommendation: (rec: any) => void;
  getStatusIcon: (status: string) => React.ReactNode;
  getStatusColor: (status: string) => string;
}

export function RecommendationList({
  recommendations,
  selectedRecommendation,
  onSelectRecommendation,
  getStatusIcon,
  getStatusColor,
}: RecommendationListProps) {
  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      stock_transfer: 'Stock Transfer',
      replenishment: 'Replenishment',
      route_change: 'Route Change',
      shipment_priority: 'Priority',
      shortage_review: 'Shortage Review',
    };
    return labels[type] || type;
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return 'text-red-600';
      case 2:
        return 'text-orange-600';
      case 3:
        return 'text-yellow-600';
      case 4:
        return 'text-blue-600';
      case 5:
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  if (recommendations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <p className="text-slate-500">No recommendations found</p>
        <p className="text-sm text-slate-400 mt-2">
          Generate recommendations or adjust filters
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      <div className="p-4 border-b border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900">
          Recommendations ({recommendations.length})
        </h2>
      </div>
      <div className="divide-y divide-slate-200 max-h-[600px] overflow-y-auto">
        {recommendations.map((rec) => {
          const isSelected = selectedRecommendation?.id === rec.id;

          return (
            <div
              key={rec.id}
              onClick={() => onSelectRecommendation(rec)}
              className={`p-4 cursor-pointer transition-colors ${
                isSelected ? 'bg-blue-50' : 'hover:bg-slate-50'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 flex-1">
                  {getStatusIcon(rec.status)}
                  <h3 className="font-semibold text-slate-900 text-sm flex-1">
                    {rec.title}
                  </h3>
                </div>
                <span className={`text-xs font-bold ${getPriorityColor(rec.priority)}`}>
                  P{rec.priority}
                </span>
              </div>

              <div className="flex items-center gap-2 mb-2">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(rec.status)}`}>
                  {rec.status}
                </span>
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
                  {getTypeLabel(rec.recommendation_type)}
                </span>
              </div>

              <div className="text-xs text-slate-500 space-y-1">
                {rec.depot_name && (
                  <div>Depot: {rec.depot_name}</div>
                )}
                {rec.shipment_tracking && (
                  <div>Shipment: {rec.shipment_tracking}</div>
                )}
                {rec.inventory_item_name && (
                  <div>Item: {rec.inventory_item_name}</div>
                )}
                {rec.route_name && (
                  <div>Route: {rec.route_name}</div>
                )}
                <div className="flex items-center justify-between pt-1">
                  <span>Confidence: {(rec.confidence_score * 100).toFixed(0)}%</span>
                  <span>{new Date(rec.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
