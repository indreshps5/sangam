"""
Recommendation Module Tests

Comprehensive tests for recommendation generation, approval workflows, and execution.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from sangam_api.recommendations.models import Recommendation, RecommendationAuditLog
from sangam_api.recommendations.schemas import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationStatus,
    RecommendationType,
    RecommendationCategory,
)
from sangam_api.recommendations.service import RecommendationService
from sangam_api.recommendations.strategies import (
    StockTransferStrategy,
    ReplenishmentStrategy,
    RouteOptimizationStrategy,
    ShipmentPriorityStrategy,
    ShortageReviewStrategy,
)
from sangam_api.core.exceptions import NotFoundException, ValidationException


class TestRecommendationService:
    """Tests for recommendation service."""
    
    @pytest.fixture
    def mock_repos(self):
        """Mock repositories."""
        class MockRecommendationRepo:
            def __init__(self):
                self.recommendations = {}
            
            async def get_by_id(self, rec_id):
                return self.recommendations.get(rec_id)
            
            async def create(self, recommendation):
                self.recommendations[recommendation.id] = recommendation
                return recommendation
            
            async def update(self, recommendation):
                self.recommendations[recommendation.id] = recommendation
                return recommendation
            
            async def list_recommendations(self, **kwargs):
                return list(self.recommendations.values())
            
            async def count_recommendations(self, **kwargs):
                return len(self.recommendations)
            
            async def get_pending_recommendations(self, **kwargs):
                return [r for r in self.recommendations.values() if r.status == 'pending']
            
            async def get_statistics(self):
                return {
                    'total': len(self.recommendations),
                    'pending': sum(1 for r in self.recommendations.values() if r.status == 'pending'),
                    'approved': sum(1 for r in self.recommendations.values() if r.status == 'approved'),
                    'rejected': sum(1 for r in self.recommendations.values() if r.status == 'rejected'),
                    'completed': sum(1 for r in self.recommendations.values() if r.status == 'completed'),
                    'by_type': {},
                    'by_category': {},
                    'by_priority': {},
                    'average_confidence_score': 0.0
                }
        
        class MockAuditLogRepo:
            def __init__(self):
                self.logs = []
            
            async def create(self, log):
                self.logs.append(log)
                return log
            
            async def list_by_recommendation(self, recommendation_id, **kwargs):
                return [l for l in self.logs if l.recommendation_id == recommendation_id]
            
            async def count_by_recommendation(self, recommendation_id):
                return len([l for l in self.logs if l.recommendation_id == recommendation_id])
        
        return MockRecommendationRepo(), MockAuditLogRepo()
    
    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mock repos."""
        rec_repo, audit_repo = mock_repos
        return RecommendationService(
            recommendation_repo=rec_repo,
            audit_log_repo=audit_repo,
            db=None,
            inventory_service=None,
            forecast_service=None,
            shipment_service=None,
            route_service=None
        )
    
    @pytest.mark.asyncio
    async def test_create_recommendation(self, service, mock_repos):
        """Test creating a recommendation."""
        rec_repo, _ = mock_repos
        
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy'
        )
        
        created = await service.recommendation_repo.create(recommendation)
        
        assert created.id == recommendation.id
        assert created.status == 'pending'
        assert recommendation.id in rec_repo.recommendations
    
    @pytest.mark.asyncio
    async def test_approve_recommendation(self, service, mock_repos):
        """Test approving a recommendation."""
        rec_repo, audit_repo = mock_repos
        
        # Create a pending recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy',
            status='pending'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # Approve it
        user_id = uuid4()
        approved = await service.approve_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User',
            notes='Approved for testing'
        )
        
        assert approved.status == 'approved'
        assert approved.approved_by == user_id
        assert approved.approved_at is not None
        
        # Check audit log
        assert len(audit_repo.logs) == 1
        assert audit_repo.logs[0].action == 'approved'
    
    @pytest.mark.asyncio
    async def test_cannot_approve_non_pending(self, service, mock_repos):
        """Test that non-pending recommendations cannot be approved."""
        rec_repo, _ = mock_repos
        
        # Create an approved recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy',
            status='approved'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # Try to approve it
        with pytest.raises(ValidationException, match="Cannot approve"):
            await service.approve_recommendation(
                recommendation_id=recommendation.id,
                user_id=uuid4(),
                user_name='Test User'
            )
    
    @pytest.mark.asyncio
    async def test_reject_recommendation(self, service, mock_repos):
        """Test rejecting a recommendation."""
        rec_repo, audit_repo = mock_repos
        
        # Create a pending recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy',
            status='pending'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # Reject it
        user_id = uuid4()
        rejected = await service.reject_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User',
            reason='Not feasible at this time'
        )
        
        assert rejected.status == 'rejected'
        assert rejected.rejection_reason == 'Not feasible at this time'
        
        # Check audit log
        assert len(audit_repo.logs) == 1
        assert audit_repo.logs[0].action == 'rejected'
    
    @pytest.mark.asyncio
    async def test_execute_approved_recommendation(self, service, mock_repos):
        """Test executing an approved recommendation."""
        rec_repo, audit_repo = mock_repos
        
        # Create an approved recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy',
            status='approved'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # Execute it
        user_id = uuid4()
        executed = await service.execute_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User',
            notes='Executed for testing'
        )
        
        assert executed.status == 'completed'
        assert executed.executed_by == user_id
        assert executed.executed_at is not None
        assert executed.execution_result is not None
        assert executed.execution_result['simulated'] is True
        
        # Check audit log
        assert len(audit_repo.logs) == 1
        assert audit_repo.logs[0].action == 'executed'
    
    @pytest.mark.asyncio
    async def test_cannot_execute_non_approved(self, service, mock_repos):
        """Test that non-approved recommendations cannot be executed."""
        rec_repo, _ = mock_repos
        
        # Create a pending recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy',
            status='pending'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # Try to execute it
        with pytest.raises(ValidationException, match="Cannot execute"):
            await service.execute_recommendation(
                recommendation_id=recommendation.id,
                user_id=uuid4(),
                user_name='Test User'
            )
    
    @pytest.mark.asyncio
    async def test_cannot_approve_expired_recommendation(self, service, mock_repos):
        """Test that expired recommendations cannot be approved."""
        rec_repo, _ = mock_repos
        
        # Create an expired recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy',
            status='pending',
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # Try to approve it
        with pytest.raises(ValidationException, match="expired"):
            await service.approve_recommendation(
                recommendation_id=recommendation.id,
                user_id=uuid4(),
                user_name='Test User'
            )


class TestRecommendationStrategies:
    """Tests for recommendation strategies."""
    
    def test_stock_transfer_strategy_name(self):
        """Test stock transfer strategy metadata."""
        strategy = StockTransferStrategy(None, None)
        assert strategy.get_strategy_name() == "Stock Transfer Strategy"
        assert strategy.get_recommendation_type() == "stock_transfer"
    
    def test_replenishment_strategy_name(self):
        """Test replenishment strategy metadata."""
        strategy = ReplenishmentStrategy(None, None)
        assert strategy.get_strategy_name() == "Replenishment Strategy"
        assert strategy.get_recommendation_type() == "replenishment"
    
    def test_route_optimization_strategy_name(self):
        """Test route optimization strategy metadata."""
        strategy = RouteOptimizationStrategy(None, None)
        assert strategy.get_strategy_name() == "Route Optimization Strategy"
        assert strategy.get_recommendation_type() == "route_change"
    
    def test_shipment_priority_strategy_name(self):
        """Test shipment priority strategy metadata."""
        strategy = ShipmentPriorityStrategy(None)
        assert strategy.get_strategy_name() == "Shipment Priority Strategy"
        assert strategy.get_recommendation_type() == "shipment_priority"
    
    def test_shortage_review_strategy_name(self):
        """Test shortage review strategy metadata."""
        strategy = ShortageReviewStrategy(None, None)
        assert strategy.get_strategy_name() == "Shortage Review Strategy"
        assert strategy.get_recommendation_type() == "shortage_review"


class TestRecommendationSchemas:
    """Tests for recommendation schemas."""
    
    def test_recommendation_create_schema(self):
        """Test recommendation creation schema."""
        data = RecommendationCreate(
            recommendation_type=RecommendationType.STOCK_TRANSFER,
            category=RecommendationCategory.INVENTORY,
            priority=2,
            title='Test Recommendation',
            description='Test description',
            rationale='Test rationale',
            suggested_action='Test action',
            confidence_score=0.85,
            source_service='test_strategy'
        )
        
        assert data.recommendation_type == RecommendationType.STOCK_TRANSFER
        assert data.priority == 2
        assert data.confidence_score == 0.85
    
    def test_recommendation_create_invalid_priority(self):
        """Test that invalid priority is rejected."""
        with pytest.raises(ValueError):
            RecommendationCreate(
                recommendation_type=RecommendationType.STOCK_TRANSFER,
                category=RecommendationCategory.INVENTORY,
                priority=10,  # Invalid: must be 1-5
                title='Test',
                description='Test',
                rationale='Test',
                suggested_action='Test',
                confidence_score=0.85,
                source_service='test'
            )
    
    def test_recommendation_create_invalid_confidence(self):
        """Test that invalid confidence score is rejected."""
        with pytest.raises(ValueError):
            RecommendationCreate(
                recommendation_type=RecommendationType.STOCK_TRANSFER,
                category=RecommendationCategory.INVENTORY,
                priority=2,
                title='Test',
                description='Test',
                rationale='Test',
                suggested_action='Test',
                confidence_score=1.5,  # Invalid: must be 0.0-1.0
                source_service='test'
            )
    
    def test_recommendation_update_schema(self):
        """Test recommendation update schema."""
        data = RecommendationUpdate(
            status=RecommendationStatus.APPROVED,
            priority=1
        )
        
        assert data.status == RecommendationStatus.APPROVED
        assert data.priority == 1


class TestRecommendationWorkflow:
    """Tests for recommendation workflow."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, service, mock_repos):
        """Test complete recommendation workflow."""
        rec_repo, audit_repo = mock_repos
        
        # 1. Create recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Transfer Stock',
            description='Transfer stock between depots',
            rationale='Low stock at destination',
            suggested_action='Create shipment',
            confidence_score=0.85,
            source_service='test_strategy',
            status='pending'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # 2. Approve recommendation
        user_id = uuid4()
        await service.approve_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User'
        )
        
        assert recommendation.status == 'approved'
        
        # 3. Execute recommendation
        await service.execute_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User'
        )
        
        assert recommendation.status == 'completed'
        
        # 4. Check audit trail
        assert len(audit_repo.logs) == 2
        assert audit_repo.logs[0].action == 'approved'
        assert audit_repo.logs[1].action == 'executed'
    
    @pytest.mark.asyncio
    async def test_rejection_workflow(self, service, mock_repos):
        """Test rejection workflow."""
        rec_repo, audit_repo = mock_repos
        
        # Create recommendation
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Transfer Stock',
            description='Transfer stock between depots',
            rationale='Low stock at destination',
            suggested_action='Create shipment',
            confidence_score=0.85,
            source_service='test_strategy',
            status='pending'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        # Reject recommendation
        user_id = uuid4()
        await service.reject_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User',
            reason='Not feasible'
        )
        
        assert recommendation.status == 'rejected'
        assert recommendation.rejection_reason == 'Not feasible'
        
        # Check audit trail
        assert len(audit_repo.logs) == 1
        assert audit_repo.logs[0].action == 'rejected'


class TestRecommendationAudit:
    """Tests for recommendation audit logging."""
    
    @pytest.mark.asyncio
    async def test_audit_log_creation(self, service, mock_repos):
        """Test that audit logs are created for all actions."""
        rec_repo, audit_repo = mock_repos
        
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test',
            description='Test',
            rationale='Test',
            suggested_action='Test',
            confidence_score=0.85,
            source_service='test',
            status='pending'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        user_id = uuid4()
        
        # Approve
        await service.approve_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User'
        )
        
        # Execute
        await service.execute_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User'
        )
        
        # Check audit logs
        assert len(audit_repo.logs) == 2
        
        # Check first log (approval)
        assert audit_repo.logs[0].action == 'approved'
        assert audit_repo.logs[0].previous_status == 'pending'
        assert audit_repo.logs[0].new_status == 'approved'
        assert audit_repo.logs[0].user_id == user_id
        
        # Check second log (execution)
        assert audit_repo.logs[1].action == 'executed'
        assert audit_repo.logs[1].previous_status == 'approved'
        assert audit_repo.logs[1].new_status == 'completed'
        assert audit_repo.logs[1].user_id == user_id
    
    @pytest.mark.asyncio
    async def test_audit_log_metadata(self, service, mock_repos):
        """Test that audit logs include metadata."""
        rec_repo, audit_repo = mock_repos
        
        recommendation = Recommendation(
            id=uuid4(),
            recommendation_type='stock_transfer',
            category='inventory',
            priority=2,
            title='Test',
            description='Test',
            rationale='Test',
            suggested_action='Test',
            confidence_score=0.85,
            source_service='test',
            status='approved'
        )
        rec_repo.recommendations[recommendation.id] = recommendation
        
        user_id = uuid4()
        
        # Execute with metadata
        await service.execute_recommendation(
            recommendation_id=recommendation.id,
            user_id=user_id,
            user_name='Test User',
            notes='Executed for testing',
            parameters={'param1': 'value1'}
        )
        
        # Check audit log metadata
        assert len(audit_repo.logs) == 1
        assert audit_repo.logs[0].notes == 'Executed for testing'
        assert audit_repo.logs[0].metadata is not None
        assert 'execution_result' in audit_repo.logs[0].metadata
