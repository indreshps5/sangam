"""
Shortage Risk Analysis
Calculates stock depletion risk, reorder recommendations, and contributing factors.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ShortageRiskLevel(str, Enum):
    """Shortage risk classification levels."""
    CRITICAL = "critical"      # < 3 days of stock
    HIGH = "high"              # 3-7 days of stock
    MEDIUM = "medium"          # 7-14 days of stock
    LOW = "low"                # 14-30 days of stock
    ADEQUATE = "adequate"      # > 30 days of stock
    UNKNOWN = "unknown"        # Insufficient data


class ShortageRiskAnalyzer:
    """
    Analyzes shortage risk based on current stock, forecasts, and supply chain parameters.
    
    Provides:
    - Days of stock remaining
    - Risk level classification
    - Shortage quantity estimates
    - Reorder timing recommendations
    - Contributing factor analysis
    """
    
    def __init__(
        self,
        lead_time_days: int = 7,
        safety_stock_days: int = 3,
        reorder_threshold_days: int = 14
    ):
        """
        Initialize shortage risk analyzer.
        
        Args:
            lead_time_days: Days required for new stock to arrive
            safety_stock_days: Minimum safety stock to maintain
            reorder_threshold_days: Days of stock at which to trigger reorder
        """
        self.lead_time_days = lead_time_days
        self.safety_stock_days = safety_stock_days
        self.reorder_threshold_days = reorder_threshold_days
        
        logger.info(
            f"Initialized ShortageRiskAnalyzer: lead_time={lead_time_days}d, "
            f"safety_stock={safety_stock_days}d, reorder_threshold={reorder_threshold_days}d"
        )
    
    def calculate_days_of_stock(
        self,
        current_stock: float,
        forecast_data: pd.DataFrame,
        incoming_shipments: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Calculate estimated days of stock remaining.
        
        Args:
            current_stock: Current available stock (units)
            forecast_data: DataFrame with 'date' and 'predicted_demand' columns
            incoming_shipments: Optional DataFrame with 'date' and 'quantity' columns
            
        Returns:
            Dictionary with days of stock calculation
        """
        logger.info(f"Calculating days of stock. Current stock: {current_stock}")
        
        if current_stock <= 0:
            return {
                'days_of_stock': 0,
                'status': 'depleted',
                'message': 'Stock is depleted'
            }
        
        # Sort forecast by date
        forecast_data = forecast_data.sort_values('date').copy()
        
        # Calculate net daily consumption (forecast - incoming)
        remaining_stock = current_stock
        days_covered = 0
        
        # Prepare incoming shipments lookup
        incoming_by_date = {}
        if incoming_shipments is not None and len(incoming_shipments) > 0:
            incoming_shipments = incoming_shipments.copy()
            incoming_shipments['date'] = pd.to_datetime(incoming_shipments['date'])
            incoming_by_date = incoming_shipments.groupby('date')['quantity'].sum().to_dict()
        
        # Simulate day-by-day consumption
        for _, row in forecast_data.iterrows():
            forecast_date = pd.to_datetime(row['date'])
            daily_demand = row['predicted_demand']
            
            # Add incoming shipments for this date
            daily_incoming = incoming_by_date.get(forecast_date, 0)
            
            # Net consumption
            net_consumption = daily_demand - daily_incoming
            
            if remaining_stock >= net_consumption:
                remaining_stock -= net_consumption
                days_covered += 1
            else:
                # Stock will run out partway through this day
                if net_consumption > 0:
                    partial_day = remaining_stock / net_consumption
                    days_covered += partial_day
                break
        
        # Determine status
        if days_covered == 0:
            status = 'depleted'
            message = 'Stock is depleted or insufficient for even one day'
        elif days_covered < self.safety_stock_days:
            status = 'critical'
            message = f'Critical: Only {days_covered:.1f} days of stock remaining'
        elif days_covered < self.reorder_threshold_days:
            status = 'low'
            message = f'Low stock: {days_covered:.1f} days remaining'
        else:
            status = 'adequate'
            message = f'Adequate stock: {days_covered:.1f} days remaining'
        
        result = {
            'days_of_stock': float(days_covered),
            'status': status,
            'message': message,
            'current_stock': float(current_stock),
            'average_daily_demand': float(forecast_data['predicted_demand'].mean()),
            'incoming_shipments_total': float(sum(incoming_by_date.values())) if incoming_by_date else 0.0
        }
        
        logger.info(f"Days of stock calculation: {days_covered:.1f} days ({status})")
        
        return result
    
    def classify_risk_level(self, days_of_stock: float) -> ShortageRiskLevel:
        """
        Classify shortage risk level based on days of stock.
        
        Args:
            days_of_stock: Estimated days of stock remaining
            
        Returns:
            ShortageRiskLevel enum value
        """
        if days_of_stock < 0:
            return ShortageRiskLevel.CRITICAL
        elif days_of_stock < 3:
            return ShortageRiskLevel.CRITICAL
        elif days_of_stock < 7:
            return ShortageRiskLevel.HIGH
        elif days_of_stock < 14:
            return ShortageRiskLevel.MEDIUM
        elif days_of_stock < 30:
            return ShortageRiskLevel.LOW
        else:
            return ShortageRiskLevel.ADEQUATE
    
    def estimate_shortage_quantity(
        self,
        current_stock: float,
        forecast_data: pd.DataFrame,
        horizon_days: int = 30,
        incoming_shipments: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Estimate shortage quantity over the forecast horizon.
        
        Args:
            current_stock: Current available stock
            forecast_data: Forecast DataFrame
            horizon_days: Number of days to project
            incoming_shipments: Expected incoming shipments
            
        Returns:
            Dictionary with shortage estimates
        """
        logger.info(f"Estimating shortage quantity over {horizon_days} days")
        
        forecast_data = forecast_data.sort_values('date').copy()
        
        # Limit to horizon
        if len(forecast_data) > horizon_days:
            forecast_data = forecast_data.head(horizon_days)
        
        # Calculate total forecast demand
        total_demand = float(forecast_data['predicted_demand'].sum())
        
        # Calculate total incoming
        total_incoming = 0.0
        if incoming_shipments is not None and len(incoming_shipments) > 0:
            incoming_shipments = incoming_shipments.copy()
            incoming_shipments['date'] = pd.to_datetime(incoming_shipments['date'])
            
            # Filter to horizon
            max_date = forecast_data['date'].max()
            incoming_shipments = incoming_shipments[incoming_shipments['date'] <= max_date]
            
            total_incoming = float(incoming_shipments['quantity'].sum())
        
        # Calculate net requirement
        net_requirement = total_demand - current_stock - total_incoming
        shortage = max(0, net_requirement)
        
        result = {
            'total_demand_forecast': total_demand,
            'current_stock': float(current_stock),
            'incoming_shipments': total_incoming,
            'net_requirement': float(net_requirement),
            'shortage_quantity': float(shortage),
            'horizon_days': horizon_days,
            'has_shortage': shortage > 0
        }
        
        if shortage > 0:
            logger.warning(f"Shortage estimated: {shortage:.2f} units over {horizon_days} days")
        else:
            logger.info(f"No shortage expected over {horizon_days} days")
        
        return result
    
    def recommend_reorder_timing(
        self,
        days_of_stock: float,
        lead_time_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Recommend when to place a reorder.
        
        Args:
            days_of_stock: Current days of stock remaining
            lead_time_days: Override lead time (uses instance default if None)
            
        Returns:
            Dictionary with reorder recommendations
        """
        if lead_time_days is None:
            lead_time_days = self.lead_time_days
        
        # Calculate reorder point
        reorder_point_days = lead_time_days + self.safety_stock_days
        
        # Determine urgency
        if days_of_stock <= reorder_point_days:
            should_reorder = True
            urgency = 'immediate' if days_of_stock <= lead_time_days else 'soon'
            days_until_reorder = 0
            message = f"Reorder immediately. Stock will deplete in {days_of_stock:.1f} days, but lead time is {lead_time_days} days."
        else:
            should_reorder = False
            urgency = 'not_yet'
            days_until_reorder = days_of_stock - reorder_point_days
            message = f"No reorder needed yet. Can wait {days_until_reorder:.1f} days before reordering."
        
        result = {
            'should_reorder': should_reorder,
            'urgency': urgency,
            'days_until_reorder': float(max(0, days_until_reorder)),
            'recommended_reorder_date': (
                datetime.now() + timedelta(days=max(0, days_until_reorder))
            ).isoformat(),
            'lead_time_days': lead_time_days,
            'safety_stock_days': self.safety_stock_days,
            'reorder_point_days': reorder_point_days,
            'message': message
        }
        
        logger.info(f"Reorder recommendation: {urgency} ({message})")
        
        return result
    
    def analyze_contributing_factors(
        self,
        current_stock: float,
        forecast_data: pd.DataFrame,
        historical_data: Optional[pd.DataFrame] = None,
        incoming_shipments: Optional[pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze factors contributing to shortage risk.
        
        Args:
            current_stock: Current stock level
            forecast_data: Forecast data
            historical_data: Historical consumption data
            incoming_shipments: Expected incoming shipments
            
        Returns:
            List of contributing factors with explanations
        """
        logger.info("Analyzing contributing factors")
        
        factors = []
        
        # Factor 1: Current stock level
        if current_stock <= 0:
            factors.append({
                'factor': 'stock_depleted',
                'severity': 'critical',
                'description': 'Stock is completely depleted',
                'impact': 'Immediate shortage risk',
                'recommendation': 'Expedite incoming shipments or emergency procurement'
            })
        elif current_stock < forecast_data['predicted_demand'].mean() * 7:
            factors.append({
                'factor': 'low_stock_level',
                'severity': 'high',
                'description': f'Current stock ({current_stock:.0f} units) is less than 7 days of forecasted demand',
                'impact': 'High risk of stockout within a week',
                'recommendation': 'Place reorder immediately'
            })
        
        # Factor 2: Demand trend
        if len(forecast_data) >= 7:
            recent_demand = forecast_data['predicted_demand'].tail(7).mean()
            earlier_demand = forecast_data['predicted_demand'].head(7).mean() if len(forecast_data) > 7 else recent_demand
            
            if recent_demand > earlier_demand * 1.2:
                factors.append({
                    'factor': 'increasing_demand',
                    'severity': 'medium',
                    'description': f'Demand is increasing by {((recent_demand/earlier_demand - 1) * 100):.1f}%',
                    'impact': 'Stock will deplete faster than expected',
                    'recommendation': 'Consider increasing order quantities'
                })
            elif recent_demand < earlier_demand * 0.8:
                factors.append({
                    'factor': 'decreasing_demand',
                    'severity': 'low',
                    'description': f'Demand is decreasing by {((1 - recent_demand/earlier_demand) * 100):.1f}%',
                    'impact': 'Stock will last longer than expected',
                    'recommendation': 'May reduce future order quantities'
                })
        
        # Factor 3: Demand variability
        if len(forecast_data) >= 7:
            demand_std = forecast_data['predicted_demand'].std()
            demand_mean = forecast_data['predicted_demand'].mean()
            
            if demand_mean > 0:
                cv = demand_std / demand_mean  # Coefficient of variation
                
                if cv > 0.5:
                    factors.append({
                        'factor': 'high_demand_variability',
                        'severity': 'medium',
                        'description': f'High demand variability (CV={cv:.2f})',
                        'impact': 'Difficult to predict exact stockout timing',
                        'recommendation': 'Increase safety stock levels'
                    })
        
        # Factor 4: Insufficient incoming shipments
        if incoming_shipments is not None and len(incoming_shipments) > 0:
            total_incoming = incoming_shipments['quantity'].sum()
            total_demand = forecast_data['predicted_demand'].sum()
            
            coverage_ratio = (current_stock + total_incoming) / total_demand if total_demand > 0 else 0
            
            if coverage_ratio < 0.8:
                factors.append({
                    'factor': 'insufficient_incoming',
                    'severity': 'high',
                    'description': f'Incoming shipments ({total_incoming:.0f} units) cover only {coverage_ratio*100:.1f}% of forecasted demand',
                    'impact': 'Will face shortage even with incoming shipments',
                    'recommendation': 'Expedite additional shipments or increase order quantities'
                })
        elif len(forecast_data) > 0:
            factors.append({
                'factor': 'no_incoming_shipments',
                'severity': 'high',
                'description': 'No incoming shipments scheduled',
                'impact': 'Stock will deplete based on current consumption only',
                'recommendation': 'Schedule incoming shipments immediately'
            })
        
        # Factor 5: Historical consumption pattern
        if historical_data is not None and len(historical_data) >= 14:
            recent_consumption = historical_data.tail(7)['consumption'].mean()
            avg_consumption = historical_data['consumption'].mean()
            
            if recent_consumption > avg_consumption * 1.3:
                factors.append({
                    'factor': 'recent_consumption_spike',
                    'severity': 'medium',
                    'description': f'Recent consumption ({recent_consumption:.1f} units/day) is {((recent_consumption/avg_consumption - 1) * 100):.1f}% above average',
                    'impact': 'Stock depleting faster than historical average',
                    'recommendation': 'Investigate cause of consumption increase'
                })
        
        # If no factors identified
        if not factors:
            factors.append({
                'factor': 'normal_operations',
                'severity': 'low',
                'description': 'No significant risk factors identified',
                'impact': 'Stock levels are within expected range',
                'recommendation': 'Continue monitoring'
            })
        
        logger.info(f"Identified {len(factors)} contributing factors")
        
        return factors
    
    def generate_risk_assessment(
        self,
        current_stock: float,
        forecast_data: pd.DataFrame,
        historical_data: Optional[pd.DataFrame] = None,
        incoming_shipments: Optional[pd.DataFrame] = None,
        lead_time_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive shortage risk assessment.
        
        Args:
            current_stock: Current available stock
            forecast_data: Forecast DataFrame
            historical_data: Historical consumption data
            incoming_shipments: Expected incoming shipments
            lead_time_days: Override lead time
            
        Returns:
            Complete risk assessment dictionary
        """
        logger.info("Generating comprehensive risk assessment")
        
        # Calculate days of stock
        days_of_stock_result = self.calculate_days_of_stock(
            current_stock, forecast_data, incoming_shipments
        )
        
        # Classify risk level
        risk_level = self.classify_risk_level(days_of_stock_result['days_of_stock'])
        
        # Estimate shortage quantity
        shortage_estimate = self.estimate_shortage_quantity(
            current_stock, forecast_data, horizon_days=30, incoming_shipments=incoming_shipments
        )
        
        # Recommend reorder timing
        reorder_recommendation = self.recommend_reorder_timing(
            days_of_stock_result['days_of_stock'], lead_time_days
        )
        
        # Analyze contributing factors
        contributing_factors = self.analyze_contributing_factors(
            current_stock, forecast_data, historical_data, incoming_shipments
        )
        
        # Compile assessment
        assessment = {
            'risk_level': risk_level.value,
            'risk_score': self._calculate_risk_score(risk_level, days_of_stock_result['days_of_stock']),
            'days_of_stock': days_of_stock_result,
            'shortage_estimate': shortage_estimate,
            'reorder_recommendation': reorder_recommendation,
            'contributing_factors': contributing_factors,
            'summary': self._generate_summary(risk_level, days_of_stock_result, shortage_estimate),
            'assessment_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Risk assessment complete. Risk level: {risk_level.value}")
        
        return assessment
    
    def _calculate_risk_score(self, risk_level: ShortageRiskLevel, days_of_stock: float) -> float:
        """
        Calculate numerical risk score (0-100).
        
        Args:
            risk_level: Categorized risk level
            days_of_stock: Days of stock remaining
            
        Returns:
            Risk score from 0 (no risk) to 100 (critical)
        """
        # Base score from risk level
        level_scores = {
            ShortageRiskLevel.CRITICAL: 90,
            ShortageRiskLevel.HIGH: 70,
            ShortageRiskLevel.MEDIUM: 50,
            ShortageRiskLevel.LOW: 30,
            ShortageRiskLevel.ADEQUATE: 10,
            ShortageRiskLevel.UNKNOWN: 50
        }
        
        base_score = level_scores.get(risk_level, 50)
        
        # Adjust based on days of stock
        if days_of_stock < 1:
            adjustment = 10
        elif days_of_stock < 3:
            adjustment = 5
        elif days_of_stock > 30:
            adjustment = -5
        else:
            adjustment = 0
        
        score = max(0, min(100, base_score + adjustment))
        
        return float(score)
    
    def _generate_summary(
        self,
        risk_level: ShortageRiskLevel,
        days_of_stock_result: Dict[str, Any],
        shortage_estimate: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable summary of risk assessment.
        
        Args:
            risk_level: Categorized risk level
            days_of_stock_result: Days of stock calculation
            shortage_estimate: Shortage quantity estimate
            
        Returns:
            Summary string
        """
        days = days_of_stock_result['days_of_stock']
        
        if risk_level == ShortageRiskLevel.CRITICAL:
            summary = f"CRITICAL: Stock will deplete in {days:.1f} days. "
            if shortage_estimate['has_shortage']:
                summary += f"Estimated shortage of {shortage_estimate['shortage_quantity']:.0f} units over 30 days. "
            summary += "Immediate action required."
        
        elif risk_level == ShortageRiskLevel.HIGH:
            summary = f"HIGH RISK: Stock will deplete in {days:.1f} days. "
            if shortage_estimate['has_shortage']:
                summary += f"Expected shortage of {shortage_estimate['shortage_quantity']:.0f} units. "
            summary += "Reorder recommended soon."
        
        elif risk_level == ShortageRiskLevel.MEDIUM:
            summary = f"MEDIUM RISK: Stock will last {days:.1f} days. "
            summary += "Monitor closely and plan reorder."
        
        elif risk_level == ShortageRiskLevel.LOW:
            summary = f"LOW RISK: Stock will last {days:.1f} days. "
            summary += "No immediate action needed, but plan for future replenishment."
        
        else:  # ADEQUATE
            summary = f"ADEQUATE: Stock will last {days:.1f} days. "
            summary += "Stock levels are healthy."
        
        return summary
