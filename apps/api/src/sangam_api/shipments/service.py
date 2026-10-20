"""
Shipment Service

Business logic for shipment management with state transition validation.
"""

import json
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from sangam_api.models.shipment import Shipment
from sangam_api.shipments.repository import ShipmentRepositoryInterface
from sangam_api.shipments.schemas import (
    ShipmentCreate,
    ShipmentUpdate,
    StatusUpdateRequest,
    LocationUpdateRequest,
    ShipmentResponse,
    ShipmentListItem,
    ShipmentDetailResponse,
    ShipmentListResponse,
    ShipmentStats,
    ShipmentAlert,
    ShipmentAlertListResponse,
    StatusChange,
    LocationData
)
from sangam_api.core.exceptions import (
    NotFoundException,
    ValidationException,
    ConflictException
)
from sangam_api.services.audit_service import AuditService


# Valid state transitions
VALID_TRANSITIONS = {
    "planned": ["dispatched", "cancelled"],
    "dispatched": ["in_transit", "cancelled"],
    "in_transit": ["delayed", "delivered", "cancelled"],
    "delayed": ["in_transit", "delivered", "cancelled"],
    "delivered": [],  # Terminal state
    "cancelled": []   # Terminal state
}


class ShipmentService:
    """Service for shipment management operations."""
    
    def __init__(self, repository: ShipmentRepositoryInterface, audit_service: AuditService):
        self.repository = repository
        self.audit_service = audit_service
    
    async def get_shipment(self, shipment_id: UUID) -> ShipmentDetailResponse:
        """Get shipment by ID with full details."""
        shipment = await self.repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment", str(shipment_id))
        
        return self._to_detail_response(shipment)
    
    async def get_shipment_by_tracking(self, tracking_number: str) -> ShipmentDetailResponse:
        """Get shipment by tracking number."""
        shipment = await self.repository.get_by_tracking_number(tracking_number)
        if not shipment:
            raise NotFoundException("Shipment", tracking_number)
        
        return self._to_detail_response(shipment)
    
    async def list_shipments(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        origin_depot_id: Optional[UUID] = None,
        destination_depot_id: Optional[UUID] = None,
        priority: Optional[int] = None,
        is_delayed: Optional[bool] = None
    ) -> ShipmentListResponse:
        """List shipments with filtering and pagination."""
        shipments = await self.repository.list_shipments(
            skip=skip,
            limit=limit,
            status=status,
            origin_depot_id=origin_depot_id,
            destination_depot_id=destination_depot_id,
            priority=priority,
            is_delayed=is_delayed
        )
        
        total = await self.repository.count_shipments(
            status=status,
            origin_depot_id=origin_depot_id,
            destination_depot_id=destination_depot_id,
            priority=priority,
            is_delayed=is_delayed
        )
        
        items = [self._to_list_item(s) for s in shipments]
        
        return ShipmentListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def create_shipment(
        self,
         ShipmentCreate,
        user_id: Optional[UUID] = None
    ) -> ShipmentResponse:
        """Create a new shipment with idempotency protection."""
        # Check idempotency key if provided
        if data.idempotency_key:
            existing = await self.repository.get_by_idempotency_key(data.idempotency_key)
            if existing:
                # Return existing shipment (idempotent)
                return self._to_response(existing)
        
        # Validate inventory item if provided
        if data.inventory_item_id:
            # TODO: Validate inventory item exists and has sufficient stock
            pass
        
        # Create shipment
        shipment = await self.repository.create(data)
        
        # Log audit
        await self.audit_service.log_shipment_created(
            shipment_id=shipment.id,
            user_id=user_id,
            origin_depot_id=data.origin_depot_id,
            destination_depot_id=data.destination_depot_id
        )
        
        return self._to_response(shipment)
    
    async def update_shipment(
        self,
        shipment_id: UUID,
         ShipmentUpdate,
        user_id: Optional[UUID] = None
    ) -> ShipmentResponse:
        """Update shipment details."""
        shipment = await self.repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment", str(shipment_id))
        
        # Prevent updates to terminal states
        if shipment.status in ["delivered", "cancelled"]:
            raise ValidationException(
                f"Cannot update shipment in {shipment.status} status"
            )
        
        # Update shipment
        updated = await self.repository.update(shipment_id, data)
        if not updated:
            raise NotFoundException("Shipment", str(shipment_id))
        
        # Log audit
        await self.audit_service.log_shipment_updated(
            shipment_id=shipment_id,
            user_id=user_id,
            changes=data.model_dump(exclude_unset=True)
        )
        
        return self._to_response(updated)
    
    async def update_status(
        self,
        shipment_id: UUID,
         StatusUpdateRequest,
        user_id: Optional[UUID] = None
    ) -> ShipmentResponse:
        """Update shipment status with validation."""
        shipment = await self.repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment", str(shipment_id))
        
        # Validate state transition
        current_status = shipment.status
        new_status = request.status.value
        
        if new_status not in VALID_TRANSITIONS.get(current_status, []):
            raise ValidationException(
                f"Invalid state transition from {current_status} to {new_status}"
            )
        
        # Additional validations
        if new_status == "delayed" and not request.delay_reason:
            raise ValidationException(
                "Delay reason is required when marking shipment as delayed"
            )
        
        # Update status
        updated = await self.repository.update_status(
            shipment_id=shipment_id,
            status=new_status,
            changed_by=user_id or request.changed_by,
            notes=request.notes,
            delay_reason=request.delay_reason
        )
        
        if not updated:
            raise NotFoundException("Shipment", str(shipment_id))
        
        # Log audit
        await self.audit_service.log_shipment_status_changed(
            shipment_id=shipment_id,
            user_id=user_id,
            old_status=current_status,
            new_status=new_status,
            notes=request.notes
        )
        
        return self._to_response(updated)
    
    async def update_location(
        self,
        shipment_id: UUID,
         LocationUpdateRequest
    ) -> ShipmentResponse:
        """Update shipment GPS location (simulation)."""
        shipment = await self.repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment", str(shipment_id))
        
        # Only allow location updates for active shipments
        if shipment.status in ["delivered", "cancelled", "planned"]:
            raise ValidationException(
                f"Cannot update location for shipment in {shipment.status} status"
            )
        
        # Update location
        updated = await self.repository.update_location(
            shipment_id=shipment_id,
            latitude=request.latitude,
            longitude=request.longitude,
            accuracy_meters=request.accuracy_meters,
            timestamp=request.timestamp
        )
        
        if not updated:
            raise NotFoundException("Shipment", str(shipment_id))
        
        return self._to_response(updated)
    
    async def get_statistics(self) -> ShipmentStats:
        """Get shipment statistics for dashboard."""
        stats = await self.repository.get_statistics()
        
        return ShipmentStats(**stats)
    
    async def get_shipment_alerts(
        self,
        overdue_threshold_hours: float = 24.0,
        at_risk_threshold_hours: float = 6.0
    ) -> ShipmentAlertListResponse:
        """Get shipment alerts for overdue and at-risk shipments."""
        alerts = []
        now = datetime.now(timezone.utc)
        
        # Get delayed shipments
        delayed_shipments = await self.repository.get_delayed_shipments()
        for shipment in delayed_shipments:
            alerts.append(ShipmentAlert(
                shipment_id=shipment.id,
                tracking_number=shipment.tracking_number,
                status=shipment.status,
                severity="critical" if shipment.priority <= 2 else "warning",
                alert_type="delayed",
                message=f"Shipment is delayed: {shipment.delay_reason or 'No reason provided'}",
                estimated_arrival=shipment.estimated_arrival,
                origin_depot_name=shipment.origin_depot.name if shipment.origin_depot else None,
                destination_depot_name=shipment.destination_depot.name if shipment.destination_depot else None
            ))
        
        # Get overdue shipments
        overdue_shipments = await self.repository.get_overdue_shipments(overdue_threshold_hours)
        for shipment in overdue_shipments:
            if shipment.estimated_arrival:
                hours_overdue = (now - shipment.estimated_arrival).total_seconds() / 3600
                
                alerts.append(ShipmentAlert(
                    shipment_id=shipment.id,
                    tracking_number=shipment.tracking_number,
                    status=shipment.status,
                    severity="critical",
                    alert_type="overdue",
                    message=f"Shipment is {hours_overdue:.1f} hours overdue",
                    estimated_arrival=shipment.estimated_arrival,
                    hours_overdue=hours_overdue,
                    origin_depot_name=shipment.origin_depot.name if shipment.origin_depot else None,
                    destination_depot_name=shipment.destination_depot.name if shipment.destination_depot else None
                ))
        
        # Get at-risk shipments (approaching estimated arrival)
        in_transit_shipments = await self.repository.get_shipments_by_status("in_transit")
        for shipment in in_transit_shipments:
            if shipment.estimated_arrival:
                hours_until_arrival = (shipment.estimated_arrival - now).total_seconds() / 3600
                
                if 0 < hours_until_arrival <= at_risk_threshold_hours:
                    alerts.append(ShipmentAlert(
                        shipment_id=shipment.id,
                        tracking_number=shipment.tracking_number,
                        status=shipment.status,
                        severity="warning",
                        alert_type="at_risk",
                        message=f"Shipment arriving in {hours_until_arrival:.1f} hours",
                        estimated_arrival=shipment.estimated_arrival,
                        hours_at_risk=hours_until_arrival,
                        origin_depot_name=shipment.origin_depot.name if shipment.origin_depot else None,
                        destination_depot_name=shipment.destination_depot.name if shipment.destination_depot else None
                    ))
        
        return ShipmentAlertListResponse(
            alerts=alerts,
            total=len(alerts)
        )
    
    async def simulate_shipment_progress(self, shipment_id: UUID) -> ShipmentResponse:
        """
        Simulate shipment progress for demonstration.
        
        This is a user-triggered simulation, not a permanent tracking loop.
        Clearly labeled as simulated data.
        """
        shipment = await self.repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment", str(shipment_id))
        
        # Simulate based on current status
        if shipment.status == "planned":
            # Move to dispatched
            await self.update_status(
                shipment_id,
                StatusUpdateRequest(
                    status="dispatched",
                    notes="Simulated: Shipment dispatched from origin"
                )
            )
        elif shipment.status == "dispatched":
            # Move to in_transit
            await self.update_status(
                shipment_id,
                StatusUpdateRequest(
                    status="in_transit",
                    notes="Simulated: Shipment in transit"
                )
            )
            # Update location (simulate midpoint)
            if shipment.origin_depot and shipment.destination_depot:
                mid_lat = (shipment.origin_depot.latitude + shipment.destination_depot.latitude) / 2
                mid_lng = (shipment.origin_depot.longitude + shipment.destination_depot.longitude) / 2
                await self.update_location(
                    shipment_id,
                    LocationUpdateRequest(
                        latitude=mid_lat,
                        longitude=mid_lng,
                        accuracy_meters=100
                    )
                )
        elif shipment.status == "in_transit":
            # Move to delivered
            await self.update_status(
                shipment_id,
                StatusUpdateRequest(
                    status="delivered",
                    notes="Simulated: Shipment delivered to destination"
                )
            )
            # Update location to destination
            if shipment.destination_depot:
                await self.update_location(
                    shipment_id,
                    LocationUpdateRequest(
                        latitude=shipment.destination_depot.latitude,
                        longitude=shipment.destination_depot.longitude,
                        accuracy_meters=10
                    )
                )
        else:
            raise ValidationException(
                f"Cannot simulate progress for shipment in {shipment.status} status"
            )
        
        # Return updated shipment
        updated = await self.repository.get_by_id(shipment_id)
        return self._to_response(updated)
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _to_response(self, shipment: Shipment) -> ShipmentResponse:
        """Convert Shipment model to response schema."""
        # Parse status history
        status_history = []
        if shipment.status_history:
            try:
                history_data = json.loads(shipment.status_history)
                status_history = [StatusChange(**h) for h in history_data]
            except:
                status_history = []
        
        # Parse current location
        current_location = None
        if shipment.current_location:
            try:
                location_data = json.loads(shipment.current_location)
                current_location = LocationData(**location_data)
            except:
                current_location = None
        
        # Calculate computed fields
        is_delayed, delay_hours = self._calculate_delay(shipment)
        progress = self._calculate_progress(shipment)
        
        return ShipmentResponse(
            id=shipment.id,
            origin_depot_id=shipment.origin_depot_id,
            destination_depot_id=shipment.destination_depot_id,
            route_id=shipment.route_id,
            inventory_item_id=shipment.inventory_item_id,
            status=shipment.status,
            weight_kg=shipment.weight_kg,
            volume_m3=shipment.volume_m3,
            quantity=shipment.quantity,
            priority=shipment.priority,
            shipment_type=shipment.shipment_type,
            carrier_name=shipment.carrier_name,
            tracking_number=shipment.tracking_number,
            estimated_departure=shipment.estimated_departure,
            actual_departure=shipment.actual_departure,
            estimated_arrival=shipment.estimated_arrival,
            actual_arrival=shipment.actual_arrival,
            status_history=status_history,
            current_location=current_location,
            delay_reason=shipment.delay_reason,
            idempotency_key=shipment.idempotency_key,
            notes=shipment.notes,
            created_at=shipment.created_at,
            updated_at=shipment.updated_at,
            is_delayed=is_delayed,
            delay_hours=delay_hours,
            progress_percentage=progress
        )
    
    def _to_list_item(self, shipment: Shipment) -> ShipmentListItem:
        """Convert Shipment model to list item schema."""
        is_delayed, _ = self._calculate_delay(shipment)
        
        return ShipmentListItem(
            id=shipment.id,
            origin_depot_id=shipment.origin_depot_id,
            destination_depot_id=shipment.destination_depot_id,
            status=shipment.status,
            priority=shipment.priority,
            shipment_type=shipment.shipment_type,
            carrier_name=shipment.carrier_name,
            tracking_number=shipment.tracking_number,
            estimated_departure=shipment.estimated_departure,
            estimated_arrival=shipment.estimated_arrival,
            is_delayed=is_delayed,
            created_at=shipment.created_at
        )
    
    def _to_detail_response(self, shipment: Shipment) -> ShipmentDetailResponse:
        """Convert Shipment model to detail response schema."""
        base_response = self._to_response(shipment)
        
        return ShipmentDetailResponse(
            **base_response.model_dump(),
            origin_depot_name=shipment.origin_depot.name if shipment.origin_depot else None,
            destination_depot_name=shipment.destination_depot.name if shipment.destination_depot else None,
            route_name=shipment.route.name if shipment.route else None,
            inventory_item_name=shipment.inventory_item.name if shipment.inventory_item else None,
            inventory_item_sku=shipment.inventory_item.sku if shipment.inventory_item else None
        )
    
    def _calculate_delay(self, shipment: Shipment) -> tuple[bool, Optional[float]]:
        """Calculate if shipment is delayed and delay hours."""
        now = datetime.now(timezone.utc)
        
        # Explicitly delayed
        if shipment.status == "delayed":
            if shipment.estimated_arrival and shipment.actual_arrival:
                delay_hours = (shipment.actual_arrival - shipment.estimated_arrival).total_seconds() / 3600
                return True, max(0, delay_hours)
            return True, None
        
        # Implicitly delayed (past estimated arrival)
        if shipment.estimated_arrival and shipment.estimated_arrival < now:
            if shipment.status in ["in_transit", "dispatched"] and not shipment.actual_arrival:
                delay_hours = (now - shipment.estimated_arrival).total_seconds() / 3600
                return True, delay_hours
        
        return False, None
    
    def _calculate_progress(self, shipment: Shipment) -> Optional[float]:
        """Calculate shipment progress percentage."""
        if shipment.status == "planned":
            return 0.0
        elif shipment.status == "dispatched":
            return 10.0
        elif shipment.status == "in_transit":
            # Estimate based on time
            if shipment.estimated_departure and shipment.estimated_arrival:
                now = datetime.now(timezone.utc)
                total_duration = (shipment.estimated_arrival - shipment.estimated_departure).total_seconds()
                elapsed = (now - shipment.estimated_departure).total_seconds()
                
                if total_duration > 0:
                    progress = min(90, (elapsed / total_duration) * 80 + 10)
                    return progress
            return 50.0  # Default midpoint
        elif shipment.status == "delayed":
            return 50.0  # Assume midpoint
        elif shipment.status == "delivered":
            return 100.0
        elif shipment.status == "cancelled":
            return None
        
        return None
