"""
Simulation Engines

Read-only simulation engines for different scenario types.
These engines calculate impacts without modifying operational data.
"""

import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.models.shipment import Shipment, Route
from sangam_api.models.inventory import InventoryItem
from sangam_api.models.depot import Depot
from sangam_api.simulation.schemas import (
    SimulationResults,
    ShipmentImpact,
    InventoryImpact,
    RouteImpact,
    RouteClosureParams,
    ShipmentDelayParams,
    IncreasedDemandParams,
    ReducedStockParams,
    DelayedReplenishmentParams,
    StorageConditionsParams,
)


class BaseSimulationEngine(ABC):
    """
    Base class for simulation engines.
    
    All engines are read-only and do not modify operational data.
    """
    
    def __init__(self, db: AsyncSession, random_seed: Optional[int] = None):
        self.db = db
        self.random = random.Random(random_seed)
    
    @abstractmethod
    async def simulate(self, parameters: Dict[str, Any]) -> SimulationResults:
        """
        Execute simulation with given parameters.
        
        This method must be read-only and not modify any operational data.
        """
        pass
    
    @abstractmethod
    async def capture_baseline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture baseline state before simulation.
        
        Returns a snapshot of relevant data before simulation.
        """
        pass


class RouteClosureEngine(BaseSimulationEngine):
    """
    Simulates route closure and its impacts.
    
    Calculates:
    - Affected shipments
    - Estimated arrival changes
    - Alternative routes (if available)
    """
    
    async def capture_baseline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Capture baseline state for route closure."""
        params = RouteClosureParams(**parameters)
        
        # Get route
        result = await self.db.execute(
            select(Route).where(Route.id == params.route_id)
        )
        route = result.scalar_one_or_none()
        
        if not route:
            raise ValueError(f"Route {params.route_id} not found")
        
        # Get shipments on this route
        shipments_result = await self.db.execute(
            select(Shipment).where(
                Shipment.route_id == params.route_id,
                Shipment.status.in_(['planned', 'dispatched', 'in_transit'])
            )
        )
        shipments = shipments_result.scalars().all()
        
        # Get alternative routes
        alternatives_result = await self.db.execute(
            select(Route).where(
                Route.origin_depot_id == route.origin_depot_id,
                Route.destination_depot_id == route.destination_depot_id,
                Route.id != route.id,
                Route.status == 'active'
            )
        )
        alternatives = alternatives_result.scalars().all()
        
        return {
            "route": {
                "id": str(route.id),
                "name": route.name,
                "status": route.status,
                "distance_km": route.distance_km,
            },
            "affected_shipments": [
                {
                    "id": str(s.id),
                    "tracking_number": s.tracking_number,
                    "status": s.status,
                    "estimated_arrival": s.estimated_arrival.isoformat() if s.estimated_arrival else None,
                }
                for s in shipments
            ],
            "alternative_routes": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "distance_km": r.distance_km,
                }
                for r in alternatives
            ]
        }
    
    async def simulate(self, parameters: Dict[str, Any]) -> SimulationResults:
        """Simulate route closure."""
        params = RouteClosureParams(**parameters)
        
        # Get route
        result = await self.db.execute(
            select(Route).where(Route.id == params.route_id)
        )
        route = result.scalar_one_or_none()
        
        if not route:
            raise ValueError(f"Route {params.route_id} not found")
        
        # Get affected shipments
        shipments_result = await self.db.execute(
            select(Shipment).where(
                Shipment.route_id == params.route_id,
                Shipment.status.in_(['planned', 'dispatched', 'in_transit'])
            )
        )
        shipments = shipments_result.scalars().all()
        
        # Get alternative routes
        alternatives_result = await self.db.execute(
            select(Route).where(
                Route.origin_depot_id == route.origin_depot_id,
                Route.destination_depot_id == route.destination_depot_id,
                Route.id != route.id,
                Route.status == 'active'
            )
        )
        alternatives = alternatives_result.scalars().all()
        
        # Calculate impacts
        shipment_impacts = []
        for shipment in shipments:
            # Calculate delay (assume 2x duration for rerouting)
            delay_hours = params.duration_hours * 0.5
            
            # Find best alternative
            best_alternative = None
            if alternatives:
                best_alternative = min(alternatives, key=lambda r: r.distance_km or float('inf'))
            
            simulated_arrival = None
            if shipment.estimated_arrival:
                simulated_arrival = shipment.estimated_arrival + timedelta(hours=delay_hours)
            
            impact = ShipmentImpact(
                shipment_id=shipment.id,
                tracking_number=shipment.tracking_number,
                baseline_arrival=shipment.estimated_arrival,
                simulated_arrival=simulated_arrival,
                delay_hours=delay_hours,
                status_change="delayed" if delay_hours > 0 else None,
                alternative_route_id=best_alternative.id if best_alternative else None,
                alternative_route_name=best_alternative.name if best_alternative else None,
                impact_description=f"Shipment delayed by {delay_hours:.1f} hours due to route closure"
            )
            shipment_impacts.append(impact)
        
        # Route impact
        route_impacts = []
        if route:
            route_impact = RouteImpact(
                route_id=route.id,
                route_name=route.name,
                baseline_status=route.status,
                simulated_status="closed",
                affected_shipments=len(shipments),
                alternative_routes=[
                    {"id": str(r.id), "name": r.name, "distance_km": r.distance_km}
                    for r in alternatives
                ],
                impact_description=f"Route closed for {params.duration_hours} hours. {len(shipments)} shipments affected."
            )
            route_impacts.append(route_impact)
        
        # Generate recommendations
        recommendations = []
        if alternatives:
            recommendations.append(f"Reroute {len(shipments)} shipments to alternative route: {alternatives[0].name}")
        else:
            recommendations.append("No alternative routes available. Consider delaying shipments or finding manual routes.")
        
        if params.duration_hours > 24:
            recommendations.append("Extended closure detected. Consider notifying customers of potential delays.")
        
        return SimulationResults(
            summary={
                "scenario_type": "route_closure",
                "route_closed": route.name,
                "duration_hours": params.duration_hours,
                "affected_shipments": len(shipments),
                "alternative_routes_available": len(alternatives),
                "total_delay_hours": sum(s.delay_hours or 0 for s in shipment_impacts),
            },
            shipment_impacts=shipment_impacts,
            route_impacts=route_impacts,
            recommendations=recommendations,
            assumptions=[
                "Rerouting adds 50% of closure duration as delay",
                "Alternative routes are assumed to be operational",
                "No capacity constraints on alternative routes"
            ],
            limitations=[
                "Does not account for traffic or weather conditions",
                "Alternative route capacity not validated",
                "Driver availability not considered"
            ]
        )


class ShipmentDelayEngine(BaseSimulationEngine):
    """
    Simulates shipment delay and its impacts.
    
    Calculates:
    - New estimated arrival
    - Downstream inventory impacts
    """
    
    async def capture_baseline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Capture baseline state for shipment delay."""
        params = ShipmentDelayParams(**parameters)
        
        # Get shipment
        result = await self.db.execute(
            select(Shipment).where(Shipment.id == params.shipment_id)
        )
        shipment = result.scalar_one_or_none()
        
        if not shipment:
            raise ValueError(f"Shipment {params.shipment_id} not found")
        
        return {
            "shipment": {
                "id": str(shipment.id),
                "tracking_number": shipment.tracking_number,
                "status": shipment.status,
                "estimated_arrival": shipment.estimated_arrival.isoformat() if shipment.estimated_arrival else None,
                "destination_depot_id": str(shipment.destination_depot_id),
            }
        }
    
    async def simulate(self, parameters: Dict[str, Any]) -> SimulationResults:
        """Simulate shipment delay."""
        params = ShipmentDelayParams(**parameters)
        
        # Get shipment
        result = await self.db.execute(
            select(Shipment).where(Shipment.id == params.shipment_id)
        )
        shipment = result.scalar_one_or_none()
        
        if not shipment:
            raise ValueError(f"Shipment {params.shipment_id} not found")
        
        # Calculate new arrival
        simulated_arrival = None
        if shipment.estimated_arrival:
            simulated_arrival = shipment.estimated_arrival + timedelta(hours=params.delay_hours)
        
        # Create shipment impact
        shipment_impacts = [
            ShipmentImpact(
                shipment_id=shipment.id,
                tracking_number=shipment.tracking_number,
                baseline_arrival=shipment.estimated_arrival,
                simulated_arrival=simulated_arrival,
                delay_hours=params.delay_hours,
                status_change="delayed",
                impact_description=f"Shipment delayed by {params.delay_hours} hours"
            )
        ]
        
        return SimulationResults(
            summary={
                "scenario_type": "shipment_delay",
                "shipment_id": str(shipment.id),
                "delay_hours": params.delay_hours,
                "new_estimated_arrival": simulated_arrival.isoformat() if simulated_arrival else None,
            },
            shipment_impacts=shipment_impacts,
            recommendations=[
                f"Notify destination depot of {params.delay_hours} hour delay",
                "Update customer with new estimated delivery time"
            ],
            assumptions=[
                "Delay is applied to estimated arrival time",
                "No downstream inventory impacts calculated"
            ],
            limitations=[
                "Does not calculate inventory stockout risk",
                "Does not consider alternative shipments"
            ]
        )


class IncreasedDemandEngine(BaseSimulationEngine):
    """
    Simulates increased demand and its impacts.
    
    Calculates:
    - Stock depletion rate
    - Stockout risk
    - Reorder recommendations
    """
    
    async def capture_baseline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Capture baseline state for increased demand."""
        params = IncreasedDemandParams(**parameters)
        
        # Get inventory item
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == params.inventory_item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Inventory item {params.inventory_item_id} not found")
        
        return {
            "inventory_item": {
                "id": str(item.id),
                "name": item.name,
                "sku": item.sku,
                "quantity_on_hand": item.quantity_on_hand,
                "quantity_reserved": item.quantity_reserved,
                "min_stock_level": item.min_stock_level,
                "avg_daily_consumption": 10.0,  # Placeholder
            }
        }
    
    async def simulate(self, parameters: Dict[str, Any]) -> SimulationResults:
        """Simulate increased demand."""
        params = IncreasedDemandParams(**parameters)
        
        # Get inventory item
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == params.inventory_item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Inventory item {params.inventory_item_id} not found")
        
        # Calculate impacts
        available_stock = item.quantity_on_hand - item.quantity_reserved
        baseline_daily_consumption = 10.0  # Placeholder - should come from forecasting
        increased_daily_consumption = baseline_daily_consumption * (1 + params.demand_increase_percent / 100)
        
        # Calculate days until stockout
        days_until_stockout = available_stock / increased_daily_consumption if increased_daily_consumption > 0 else float('inf')
        
        # Calculate final stock after duration
        total_consumption = increased_daily_consumption * params.duration_days
        simulated_stock = max(0, available_stock - total_consumption)
        
        stockout_risk = simulated_stock <= 0
        reorder_recommended = simulated_stock < item.min_stock_level
        
        inventory_impacts = [
            InventoryImpact(
                inventory_item_id=item.id,
                item_name=item.name,
                sku=item.sku,
                depot_name="Depot",  # Should get from relationship
                baseline_stock=available_stock,
                simulated_stock=simulated_stock,
                stock_change=simulated_stock - available_stock,
                stockout_risk=stockout_risk,
                days_until_stockout=days_until_stockout if stockout_risk else None,
                reorder_recommended=reorder_recommended,
                impact_description=f"Stock reduced by {abs(simulated_stock - available_stock):.0f} units over {params.duration_days} days"
            )
        ]
        
        recommendations = []
        if stockout_risk:
            recommendations.append(f"URGENT: Stockout in {days_until_stockout:.1f} days. Increase replenishment immediately.")
        if reorder_recommended:
            recommendations.append("Place reorder to maintain minimum stock levels")
        recommendations.append(f"Monitor demand closely for {params.duration_days} days")
        
        return SimulationResults(
            summary={
                "scenario_type": "increased_demand",
                "inventory_item_id": str(item.id),
                "demand_increase_percent": params.demand_increase_percent,
                "duration_days": params.duration_days,
                "stockout_risk": stockout_risk,
                "days_until_stockout": days_until_stockout if stockout_risk else None,
            },
            inventory_impacts=inventory_impacts,
            recommendations=recommendations,
            assumptions=[
                "Baseline daily consumption is 10 units (placeholder)",
                "Demand increase is sustained for entire duration",
                "No additional replenishment during simulation period"
            ],
            limitations=[
                "Baseline consumption is estimated, not from historical data",
                "Does not account for seasonal variations",
                "Does not consider lead time for replenishment"
            ]
        )


class ReducedStockEngine(BaseSimulationEngine):
    """
    Simulates reduced stock and its impacts.
    
    Calculates:
    - Stockout risk
    - Affected shipments
    - Reorder urgency
    """
    
    async def capture_baseline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Capture baseline state for reduced stock."""
        params = ReducedStockParams(**parameters)
        
        # Get inventory item
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == params.inventory_item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Inventory item {params.inventory_item_id} not found")
        
        return {
            "inventory_item": {
                "id": str(item.id),
                "name": item.name,
                "sku": item.sku,
                "quantity_on_hand": item.quantity_on_hand,
                "quantity_reserved": item.quantity_reserved,
                "min_stock_level": item.min_stock_level,
            }
        }
    
    async def simulate(self, parameters: Dict[str, Any]) -> SimulationResults:
        """Simulate reduced stock."""
        params = ReducedStockParams(**parameters)
        
        # Get inventory item
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == params.inventory_item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Inventory item {params.inventory_item_id} not found")
        
        # Calculate impacts
        available_stock = item.quantity_on_hand - item.quantity_reserved
        reduction_amount = available_stock * (params.stock_reduction_percent / 100)
        simulated_stock = available_stock - reduction_amount
        
        stockout_risk = simulated_stock <= 0
        below_minimum = simulated_stock < item.min_stock_level
        
        inventory_impacts = [
            InventoryImpact(
                inventory_item_id=item.id,
                item_name=item.name,
                sku=item.sku,
                depot_name="Depot",  # Should get from relationship
                baseline_stock=available_stock,
                simulated_stock=simulated_stock,
                stock_change=-reduction_amount,
                stockout_risk=stockout_risk,
                days_until_stockout=None,
                reorder_recommended=below_minimum,
                impact_description=f"Stock reduced by {reduction_amount:.0f} units ({params.stock_reduction_percent}%)"
            )
        ]
        
        recommendations = []
        if stockout_risk:
            recommendations.append("CRITICAL: Stock depleted. Expedite replenishment or halt outbound shipments.")
        elif below_minimum:
            recommendations.append("Stock below minimum level. Place emergency reorder.")
        else:
            recommendations.append("Monitor stock levels closely")
        
        return SimulationResults(
            summary={
                "scenario_type": "reduced_stock",
                "inventory_item_id": str(item.id),
                "stock_reduction_percent": params.stock_reduction_percent,
                "reduction_amount": reduction_amount,
                "stockout_risk": stockout_risk,
            },
            inventory_impacts=inventory_impacts,
            recommendations=recommendations,
            assumptions=[
                "Reduction is immediate and permanent",
                "No incoming shipments during simulation"
            ],
            limitations=[
                "Does not calculate time to stockout",
                "Does not consider demand forecasts"
            ]
        )


class DelayedReplenishmentEngine(BaseSimulationEngine):
    """
    Simulates delayed replenishment and its impacts.
    
    Calculates:
    - Stock depletion timeline
    - Stockout risk
    - Impact on operations
    """
    
    async def capture_baseline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Capture baseline state for delayed replenishment."""
        params = DelayedReplenishmentParams(**parameters)
        
        # Get inventory item
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == params.inventory_item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Inventory item {params.inventory_item_id} not found")
        
        return {
            "inventory_item": {
                "id": str(item.id),
                "name": item.name,
                "sku": item.sku,
                "quantity_on_hand": item.quantity_on_hand,
                "min_stock_level": item.min_stock_level,
            }
        }
    
    async def simulate(self, parameters: Dict[str, Any]) -> SimulationResults:
        """Simulate delayed replenishment."""
        params = DelayedReplenishmentParams(**parameters)
        
        # Get inventory item
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == params.inventory_item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Inventory item {params.inventory_item_id} not found")
        
        # Calculate impacts
        available_stock = item.quantity_on_hand - item.quantity_reserved
        baseline_daily_consumption = 10.0  # Placeholder
        
        # Calculate days until stockout with current stock
        days_until_stockout = available_stock / baseline_daily_consumption if baseline_daily_consumption > 0 else float('inf')
        
        stockout_risk = params.delay_days > days_until_stockout
        
        inventory_impacts = [
            InventoryImpact(
                inventory_item_id=item.id,
                item_name=item.name,
                sku=item.sku,
                depot_name="Depot",
                baseline_stock=available_stock,
                simulated_stock=max(0, available_stock - (baseline_daily_consumption * params.delay_days)),
                stock_change=-(baseline_daily_consumption * params.delay_days),
                stockout_risk=stockout_risk,
                days_until_stockout=days_until_stockout,
                reorder_recommended=True,
                impact_description=f"Replenishment delayed by {params.delay_days} days"
            )
        ]
        
        recommendations = []
        if stockout_risk:
            recommendations.append(f"CRITICAL: Stockout in {days_until_stockout:.1f} days. Find alternative supplier or expedite shipment.")
        else:
            recommendations.append(f"Monitor stock levels. Current stock lasts {days_until_stockout:.1f} days.")
        
        return SimulationResults(
            summary={
                "scenario_type": "delayed_replenishment",
                "inventory_item_id": str(item.id),
                "delay_days": params.delay_days,
                "stockout_risk": stockout_risk,
                "days_until_stockout": days_until_stockout,
            },
            inventory_impacts=inventory_impacts,
            recommendations=recommendations,
            assumptions=[
                "Baseline daily consumption is 10 units (placeholder)",
                "No other shipments affect stock during delay period"
            ],
            limitations=[
                "Baseline consumption is estimated",
                "Does not consider alternative suppliers"
            ]
        )


class StorageConditionsEngine(BaseSimulationEngine):
    """
    Simulates storage condition changes and their impacts.
    
    Calculates:
    - Affected inventory items
    - Quality degradation risk
    - Potential losses
    """
    
    async def capture_baseline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Capture baseline state for storage conditions."""
        params = StorageConditionsParams(**parameters)
        
        # Get depot
        result = await self.db.execute(
            select(Depot).where(Depot.id == params.depot_id)
        )
        depot = result.scalar_one_or_none()
        
        if not depot:
            raise ValueError(f"Depot {params.depot_id} not found")
        
        # Get inventory items in depot
        items_result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.depot_id == params.depot_id)
        )
        items = items_result.scalars().all()
        
        return {
            "depot": {
                "id": str(depot.id),
                "name": depot.name,
                "inventory_items_count": len(items),
            }
        }
    
    async def simulate(self, parameters: Dict[str, Any]) -> SimulationResults:
        """Simulate storage condition changes."""
        params = StorageConditionsParams(**parameters)
        
        # Get depot
        result = await self.db.execute(
            select(Depot).where(Depot.id == params.depot_id)
        )
        depot = result.scalar_one_or_none()
        
        if not depot:
            raise ValueError(f"Depot {params.depot_id} not found")
        
        # Get inventory items in depot
        items_result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.depot_id == params.depot_id)
        )
        items = items_result.scalars().all()
        
        # For demo, assume 10% of items are temperature-sensitive
        sensitive_items = items[:max(1, len(items) // 10)]
        
        inventory_impacts = []
        for item in sensitive_items:
            # Estimate quality loss (5-15% depending on conditions)
            quality_loss_percent = 5 + (abs(params.temperature_change or 0) * 2)
            quality_loss_percent = min(quality_loss_percent, 15)
            
            available_stock = item.quantity_on_hand - item.quantity_reserved
            lost_stock = available_stock * (quality_loss_percent / 100)
            
            impact = InventoryImpact(
                inventory_item_id=item.id,
                item_name=item.name,
                sku=item.sku,
                depot_name=depot.name,
                baseline_stock=available_stock,
                simulated_stock=available_stock - lost_stock,
                stock_change=-lost_stock,
                stockout_risk=False,
                days_until_stockout=None,
                reorder_recommended=False,
                impact_description=f"Quality degradation: {quality_loss_percent:.1f}% stock loss due to condition change"
            )
            inventory_impacts.append(impact)
        
        recommendations = []
        if params.temperature_change:
            recommendations.append(f"Temperature change of {params.temperature_change}°C detected. Inspect sensitive inventory.")
        if params.humidity_change:
            recommendations.append(f"Humidity change of {params.humidity_change}% detected. Check packaging integrity.")
        recommendations.append("Review storage conditions and HVAC systems")
        
        return SimulationResults(
            summary={
                "scenario_type": "storage_conditions",
                "depot_id": str(depot.id),
                "depot_name": depot.name,
                "duration_hours": params.duration_hours,
                "affected_items": len(sensitive_items),
                "total_quality_loss_percent": sum(abs(i.stock_change) / i.baseline_stock * 100 for i in inventory_impacts) / len(inventory_impacts) if inventory_impacts else 0,
            },
            inventory_impacts=inventory_impacts,
            recommendations=recommendations,
            assumptions=[
                "10% of inventory items are condition-sensitive",
                "Quality loss is proportional to condition deviation",
                "Loss is permanent and cannot be recovered"
            ],
            limitations=[
                "Sensitive item identification is simplified",
                "Quality loss calculation is estimated",
                "Does not account for item-specific tolerances"
            ]
        )


# Engine factory
def get_simulation_engine(scenario_type: str, db: AsyncSession, random_seed: Optional[int] = None) -> BaseSimulationEngine:
    """Get appropriate simulation engine for scenario type."""
    engines = {
        "route_closure": RouteClosureEngine,
        "shipment_delay": ShipmentDelayEngine,
        "increased_demand": IncreasedDemandEngine,
        "reduced_stock": ReducedStockEngine,
        "delayed_replenishment": DelayedReplenishmentEngine,
        "storage_conditions": StorageConditionsEngine,
    }
    
    engine_class = engines.get(scenario_type)
    if not engine_class:
        raise ValueError(f"Unknown scenario type: {scenario_type}")
    
    return engine_class(db, random_seed)
