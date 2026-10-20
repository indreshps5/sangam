"""
Recommendation Strategy Interfaces

Defines the strategy pattern for generating different types of recommendations.
Each strategy is responsible for generating recommendations of a specific type.
"""

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from uuid import UUID

from sangam_api.recommendations.models import Recommendation


class RecommendationStrategy(ABC):
    """
    Abstract base class for recommendation strategies.
    
    Each strategy generates recommendations of a specific type by analyzing
    data from various services (inventory, forecasting, shipment, etc.).
    """
    
    @abstractmethod
    async def generate_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """
        Generate recommendations based on current system state.
        
        Args:
            context: Optional context data (e.g., specific depot, shipment)
        
        Returns:
            List of generated recommendations
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass
    
    @abstractmethod
    def get_recommendation_type(self) -> str:
        """Get the type of recommendations this strategy generates."""
        pass


class StockTransferStrategy(RecommendationStrategy):
    """
    Strategy for generating stock transfer recommendations.
    
    Analyzes inventory levels across depots and suggests transfers
    to balance stock and prevent shortages.
    """
    
    def __init__(self, inventory_service, forecast_service):
        self.inventory_service = inventory_service
        self.forecast_service = forecast_service
    
    async def generate_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Generate stock transfer recommendations."""
        recommendations = []
        
        # Get low stock alerts from inventory service
        low_stock_items = await self.inventory_service.get_low_stock_items()
        
        for item in low_stock_items:
            # Check if there's excess stock at other depots
            excess_depots = await self.inventory_service.find_excess_stock(
                item_id=item.id,
                min_excess=100  # Minimum excess to consider transfer
            )
            
            if excess_depots:
                # Get forecast for this item
                forecast = await self.forecast_service.get_demand_forecast(
                    item_id=item.id,
                    horizon_days=30
                )
                
                # Calculate recommended transfer quantity
                shortage = item.min_stock_level - item.quantity_available
                recommended_qty = min(shortage * 1.2, excess_depots[0]['quantity'])
                
                recommendation = Recommendation(
                    recommendation_type='stock_transfer',
                    category='inventory',
                    priority=2 if shortage > 100 else 3,
                    title=f"Transfer {item.name} from {excess_depots[0]['depot_name']}",
                    description=f"Transfer {recommended_qty:.0f} units of {item.name} "
                              f"from {excess_depots[0]['depot_name']} to {item.depot.name} "
                              f"to prevent stockout.",
                    rationale=f"Current stock at {item.depot.name} is {item.quantity_available:.0f} units, "
                             f"below minimum level of {item.min_stock_level:.0f}. "
                             f"Forecasted demand in next 30 days: {forecast.get('total_demand', 0):.0f} units. "
                             f"{excess_depots[0]['depot_name']} has excess stock of {excess_depots[0]['quantity']:.0f} units.",
                    suggested_action=f"Create shipment to transfer {recommended_qty:.0f} units "
                                   f"from {excess_depots[0]['depot_name']} to {item.depot.name}",
                    affected_depot_id=item.depot_id,
                    affected_inventory_item_id=item.id,
                    supporting_data={
                        'current_stock': item.quantity_available,
                        'min_stock_level': item.min_stock_level,
                        'shortage': shortage,
                        'source_depot': excess_depots[0]['depot_name'],
                        'source_stock': excess_depots[0]['quantity'],
                        'forecasted_demand': forecast.get('total_demand', 0)
                    },
                    assumptions={
                        'transfer_cost': 'Estimated $500',
                        'transfer_time': 'Estimated 2 days',
                        'demand_forecast_accuracy': '85%'
                    },
                    estimated_impact={
                        'prevented_stockout': True,
                        'cost_savings': shortage * item.unit_cost * 0.1,  # 10% savings vs emergency procurement
                        'service_level_improvement': '15%'
                    },
                    confidence_score=0.85,
                    source_service='stock_transfer_strategy',
                    source_records={
                        'inventory_item_id': str(item.id),
                        'source_depot_id': str(excess_depots[0]['depot_id']),
                        'forecast_id': forecast.get('id')
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def get_strategy_name(self) -> str:
        return "Stock Transfer Strategy"
    
    def get_recommendation_type(self) -> str:
        return "stock_transfer"


class ReplenishmentStrategy(RecommendationStrategy):
    """
    Strategy for generating replenishment recommendations.
    
    Analyzes inventory levels and forecasts to suggest when and how
    much to reorder.
    """
    
    def __init__(self, inventory_service, forecast_service):
        self.inventory_service = inventory_service
        self.forecast_service = forecast_service
    
    async def generate_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Generate replenishment recommendations."""
        recommendations = []
        
        # Get items approaching reorder point
        items_to_reorder = await self.inventory_service.get_items_near_reorder_point()
        
        for item in items_to_reorder:
            # Get forecast
            forecast = await self.forecast_service.get_demand_forecast(
                item_id=item.id,
                horizon_days=60
            )
            
            # Calculate reorder quantity (EOQ - Economic Order Quantity)
            daily_demand = forecast.get('avg_daily_demand', 10)
            lead_time_days = 7  # Default lead time
            safety_stock = item.min_stock_level * 0.5
            reorder_qty = (daily_demand * lead_time_days) + safety_stock - item.quantity_available
            
            if reorder_qty > 0:
                recommendation = Recommendation(
                    recommendation_type='replenishment',
                    category='inventory',
                    priority=1 if item.quantity_available < item.min_stock_level * 0.5 else 2,
                    title=f"Replenish {item.name} at {item.depot.name}",
                    description=f"Order {reorder_qty:.0f} units of {item.name} "
                              f"for {item.depot.name} to maintain adequate stock levels.",
                    rationale=f"Current stock: {item.quantity_available:.0f} units. "
                             f"Minimum level: {item.min_stock_level:.0f} units. "
                             f"Average daily demand: {daily_demand:.1f} units. "
                             f"Lead time: {lead_time_days} days. "
                             f"Without replenishment, stockout expected in "
                             f"{item.quantity_available / daily_demand:.1f} days.",
                    suggested_action=f"Place purchase order for {reorder_qty:.0f} units "
                                   f"of {item.name} (SKU: {item.sku})",
                    affected_depot_id=item.depot_id,
                    affected_inventory_item_id=item.id,
                    supporting_data={
                        'current_stock': item.quantity_available,
                        'min_stock_level': item.min_stock_level,
                        'daily_demand': daily_demand,
                        'lead_time_days': lead_time_days,
                        'safety_stock': safety_stock,
                        'reorder_quantity': reorder_qty,
                        'days_until_stockout': item.quantity_available / daily_demand
                    },
                    assumptions={
                        'lead_time': f'{lead_time_days} days',
                        'supplier_reliability': '95%',
                        'demand_stability': 'Stable'
                    },
                    estimated_impact={
                        'prevented_stockout': True,
                        'ordering_cost': reorder_qty * 10,  # Fixed ordering cost
                        'holding_cost': reorder_qty * item.unit_cost * 0.02 * 30,  # Monthly holding
                        'service_level': '98%'
                    },
                    confidence_score=0.90,
                    source_service='replenishment_strategy',
                    source_records={
                        'inventory_item_id': str(item.id),
                        'forecast_id': forecast.get('id')
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def get_strategy_name(self) -> str:
        return "Replenishment Strategy"
    
    def get_recommendation_type(self) -> str:
        return "replenishment"


class RouteOptimizationStrategy(RecommendationStrategy):
    """
    Strategy for generating route optimization recommendations.
    
    Analyzes shipment patterns and route performance to suggest
    alternative routes or route changes.
    """
    
    def __init__(self, shipment_service, route_service):
        self.shipment_service = shipment_service
        self.route_service = route_service
    
    async def generate_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Generate route optimization recommendations."""
        recommendations = []
        
        # Get delayed shipments
        delayed_shipments = await self.shipment_service.get_delayed_shipments()
        
        for shipment in delayed_shipments:
            # Find alternative routes
            alternatives = await self.route_service.find_alternative_routes(
                origin_depot_id=shipment.origin_depot_id,
                destination_depot_id=shipment.destination_depot_id
            )
            
            if alternatives:
                best_alt = alternatives[0]  # Best alternative
                
                recommendation = Recommendation(
                    recommendation_type='route_change',
                    category='route',
                    priority=1 if shipment.priority <= 2 else 2,
                    title=f"Reroute shipment {shipment.tracking_number} via {best_alt.name}",
                    description=f"Switch shipment {shipment.tracking_number} from current route "
                              f"to {best_alt.name} to reduce delay.",
                    rationale=f"Current shipment is delayed by {shipment.delay_hours:.1f} hours. "
                             f"Alternative route {best_alt.name} is {best_alt.distance_km:.0f} km "
                             f"and estimated to take {best_alt.estimated_duration_hours:.1f} hours. "
                             f"This could reduce delay by {shipment.delay_hours - best_alt.estimated_duration_hours:.1f} hours.",
                    suggested_action=f"Reassign shipment {shipment.tracking_number} to route {best_alt.name}",
                    affected_shipment_id=shipment.id,
                    affected_route_id=best_alt.id,
                    supporting_data={
                        'current_route': shipment.route.name if shipment.route else 'Unknown',
                        'current_delay_hours': shipment.delay_hours,
                        'alternative_route': best_alt.name,
                        'alternative_distance_km': best_alt.distance_km,
                        'alternative_duration_hours': best_alt.estimated_duration_hours,
                        'potential_time_savings': shipment.delay_hours - best_alt.estimated_duration_hours
                    },
                    assumptions={
                        'route_availability': 'Route is currently available',
                        'capacity': 'Route has sufficient capacity',
                        'traffic_conditions': 'Normal traffic expected'
                    },
                    estimated_impact={
                        'time_savings_hours': max(0, shipment.delay_hours - best_alt.estimated_duration_hours),
                        'cost_impact': best_alt.cost_per_km * best_alt.distance_km,
                        'customer_satisfaction': 'Improved'
                    },
                    confidence_score=0.75,
                    source_service='route_optimization_strategy',
                    source_records={
                        'shipment_id': str(shipment.id),
                        'current_route_id': str(shipment.route_id) if shipment.route_id else None,
                        'alternative_route_id': str(best_alt.id)
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def get_strategy_name(self) -> str:
        return "Route Optimization Strategy"
    
    def get_recommendation_type(self) -> str:
        return "route_change"


class ShipmentPriorityStrategy(RecommendationStrategy):
    """
    Strategy for generating shipment priority recommendations.
    
    Analyzes shipment delays and customer impact to suggest
    priority adjustments.
    """
    
    def __init__(self, shipment_service):
        self.shipment_service = shipment_service
    
    async def generate_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Generate shipment priority recommendations."""
        recommendations = []
        
        # Get shipments with high priority but delayed
        high_priority_delayed = await self.shipment_service.get_shipments_by_criteria(
            priority_threshold=2,
            status='delayed'
        )
        
        for shipment in high_priority_delayed:
            recommendation = Recommendation(
                recommendation_type='shipment_priority',
                category='shipment',
                priority=1,
                title=f"Expedite delayed high-priority shipment {shipment.tracking_number}",
                description=f"Shipment {shipment.tracking_number} is delayed and has high priority. "
                          f"Consider expediting to minimize customer impact.",
                rationale=f"Shipment priority: {shipment.priority}. "
                         f"Delay: {shipment.delay_hours:.1f} hours. "
                         f"Customer may be impacted. "
                         f"Expedited delivery could reduce delay by 50%.",
                suggested_action=f"Contact carrier to expedite shipment {shipment.tracking_number}. "
                               f"Consider premium shipping or dedicated transport.",
                affected_shipment_id=shipment.id,
                supporting_data={
                    'current_priority': shipment.priority,
                    'delay_hours': shipment.delay_hours,
                    'carrier': shipment.carrier_name,
                    'origin': shipment.origin_depot.name,
                    'destination': shipment.destination_depot.name
                },
                assumptions={
                    'expediting_cost': 'Estimated $1000',
                    'time_savings': '50% delay reduction',
                    'carrier_cooperation': 'Likely'
                },
                estimated_impact={
                    'delay_reduction_hours': shipment.delay_hours * 0.5,
                    'additional_cost': 1000,
                    'customer_satisfaction': 'Significantly improved'
                },
                confidence_score=0.80,
                source_service='shipment_priority_strategy',
                source_records={
                    'shipment_id': str(shipment.id)
                }
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_strategy_name(self) -> str:
        return "Shipment Priority Strategy"
    
    def get_recommendation_type(self) -> str:
        return "shipment_priority"


class ShortageReviewStrategy(RecommendationStrategy):
    """
    Strategy for generating shortage review recommendations.
    
    Analyzes forecasted shortages and suggests review actions.
    """
    
    def __init__(self, forecast_service, inventory_service):
        self.forecast_service = forecast_service
        self.inventory_service = inventory_service
    
    async def generate_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Generate shortage review recommendations."""
        recommendations = []
        
        # Get forecasted shortages
        shortages = await self.forecast_service.get_forecasted_shortages(horizon_days=30)
        
        for shortage in shortages:
            item = await self.inventory_service.get_item(shortage['inventory_item_id'])
            
            recommendation = Recommendation(
                recommendation_type='shortage_review',
                category='forecast',
                priority=1 if shortage['shortage_quantity'] > 500 else 2,
                title=f"Review predicted shortage of {item.name}",
                description=f"Forecast predicts shortage of {shortage['shortage_quantity']:.0f} units "
                          f"of {item.name} at {item.depot.name} in next 30 days.",
                rationale=f"Current stock: {item.quantity_available:.0f} units. "
                         f"Forecasted demand: {shortage['forecasted_demand']:.0f} units. "
                         f"Expected shortage: {shortage['shortage_quantity']:.0f} units. "
                         f"Confidence: {shortage['confidence']:.0%}.",
                suggested_action=f"Review demand forecast accuracy. "
                               f"Consider emergency procurement or demand management. "
                               f"Alert sales team about potential stockout.",
                affected_depot_id=item.depot_id,
                affected_inventory_item_id=item.id,
                supporting_data={
                    'current_stock': item.quantity_available,
                    'forecasted_demand': shortage['forecasted_demand'],
                    'shortage_quantity': shortage['shortage_quantity'],
                    'forecast_confidence': shortage['confidence'],
                    'forecast_horizon_days': 30
                },
                assumptions={
                    'forecast_accuracy': f"{shortage['confidence']:.0%}",
                    'demand_pattern': 'As forecasted',
                    'supply_chain_stability': 'Normal'
                },
                estimated_impact={
                    'potential_revenue_loss': shortage['shortage_quantity'] * item.unit_cost * 1.5,
                    'customer_impact': 'High' if shortage['shortage_quantity'] > 500 else 'Medium',
                    'mitigation_cost': shortage['shortage_quantity'] * 20  # Emergency procurement premium
                },
                confidence_score=shortage['confidence'],
                source_service='shortage_review_strategy',
                source_records={
                    'inventory_item_id': str(item.id),
                    'forecast_id': shortage.get('forecast_id')
                }
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_strategy_name(self) -> str:
        return "Shortage Review Strategy"
    
    def get_recommendation_type(self) -> str:
        return "shortage_review"
