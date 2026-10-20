"""
Data Preprocessing and Feature Engineering
Handles data validation, cleaning, and feature preparation for forecasting.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Handles data preprocessing for forecasting models.
    
    Responsibilities:
    - Validate input data structure
    - Handle missing values
    - Detect and handle outliers
    - Generate features for modeling
    - Split data for training/testing
    """
    
    @staticmethod
    def validate_consumption_data(data: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate consumption data structure and content.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required columns
        required_cols = ['date', 'consumption']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            return False, f"Missing required columns: {missing_cols}"
        
        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(data['date']):
            try:
                data['date'] = pd.to_datetime(data['date'])
            except Exception as e:
                return False, f"Cannot parse 'date' column: {str(e)}"
        
        if not pd.api.types.is_numeric_dtype(data['consumption']):
            return False, "'consumption' column must be numeric"
        
        # Check for negative values
        if (data['consumption'] < 0).any():
            logger.warning("Found negative consumption values, treating as zero")
        
        # Check data length
        if len(data) < 3:
            return False, f"Insufficient data points: {len(data)} (minimum 3 required)"
        
        return True, ""
    
    @staticmethod
    def clean_consumption_data(
        data: pd.DataFrame,
        fill_method: str = 'ffill',
        remove_outliers: bool = True,
        outlier_threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Clean consumption data by handling missing values and outliers.
        
        Args:
            data: Input DataFrame
            fill_method: Method to fill missing values ('ffill', 'bfill', 'mean', 'zero')
            remove_outliers: Whether to remove/cap outliers
            outlier_threshold: Number of standard deviations for outlier detection
            
        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning data with {len(data)} rows")
        
        cleaned = data.copy()
        
        # Sort by date
        cleaned = cleaned.sort_values('date')
        
        # Handle negative values
        cleaned.loc[cleaned['consumption'] < 0, 'consumption'] = 0
        
        # Handle missing values
        if cleaned['consumption'].isna().any():
            logger.info(f"Found {cleaned['consumption'].isna().sum()} missing values")
            
            if fill_method == 'ffill':
                cleaned['consumption'] = cleaned['consumption'].fillna(method='ffill')
                cleaned['consumption'] = cleaned['consumption'].fillna(0)
            elif fill_method == 'bfill':
                cleaned['consumption'] = cleaned['consumption'].fillna(method='bfill')
                cleaned['consumption'] = cleaned['consumption'].fillna(0)
            elif fill_method == 'mean':
                mean_val = cleaned['consumption'].mean()
                cleaned['consumption'] = cleaned['consumption'].fillna(mean_val)
            elif fill_method == 'zero':
                cleaned['consumption'] = cleaned['consumption'].fillna(0)
        
        # Handle outliers
        if remove_outliers and len(cleaned) > 10:
            mean = cleaned['consumption'].mean()
            std = cleaned['consumption'].std()
            
            if std > 0:
                z_scores = np.abs((cleaned['consumption'] - mean) / std)
                outlier_mask = z_scores > outlier_threshold
                
                if outlier_mask.any():
                    logger.info(f"Found {outlier_mask.sum()} outliers, capping at {outlier_threshold} std dev")
                    upper_bound = mean + outlier_threshold * std
                    cleaned.loc[outlier_mask, 'consumption'] = upper_bound
        
        # Remove duplicate dates
        cleaned = cleaned.drop_duplicates(subset=['date'], keep='last')
        
        logger.info(f"Data cleaning complete. Final shape: {cleaned.shape}")
        
        return cleaned
    
    @staticmethod
    def generate_features(data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate features for forecasting models.
        
        Args:
            data: Cleaned consumption data
            
        Returns:
            DataFrame with additional features
        """
        logger.info("Generating features")
        
        features = data.copy()
        
        # Time-based features
        features['day_of_week'] = features['date'].dt.dayofweek
        features['day_of_month'] = features['date'].dt.day
        features['month'] = features['date'].dt.month
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Lag features
        for lag in [1, 3, 7, 14]:
            features[f'lag_{lag}'] = features['consumption'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            if len(features) >= window:
                features[f'rolling_mean_{window}'] = features['consumption'].rolling(window=window).mean()
                features[f'rolling_std_{window}'] = features['consumption'].rolling(window=window).std()
        
        # Trend features
        if len(features) >= 7:
            features['trend_7'] = features['consumption'].rolling(window=7).apply(
                lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == 7 else 0,
                raw=True
            )
        
        # Fill NaN values created by lag/rolling
        features = features.fillna(method='bfill')
        features = features.fillna(0)
        
        logger.info(f"Generated {len(features.columns) - 2} features")
        
        return features
    
    @staticmethod
    def split_train_test(
        data: pd.DataFrame,
        test_size: float = 0.2,
        sort_by_date: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into training and test sets.
        
        Args:
            data: Input DataFrame
            test_size: Proportion of data for testing
            sort_by_date: Whether to sort by date before splitting
            
        Returns:
            Tuple of (train_data, test_data)
        """
        if sort_by_date and 'date' in data.columns:
            data = data.sort_values('date')
        
        split_idx = int(len(data) * (1 - test_size))
        
        train_data = data.iloc[:split_idx].copy()
        test_data = data.iloc[split_idx:].copy()
        
        logger.info(f"Split data: {len(train_data)} train, {len(test_data)} test")
        
        return train_data, test_data
    
    @staticmethod
    def check_data_sufficiency(
        data: pd.DataFrame,
        min_days: int = 30,
        min_data_points: int = 20
    ) -> Dict[str, Any]:
        """
        Check if data is sufficient for forecasting.
        
        Args:
            data: Input DataFrame
            min_days: Minimum number of days required
            min_data_points: Minimum number of data points required
            
        Returns:
            Dictionary with sufficiency assessment
        """
        if len(data) == 0:
            return {
                'sufficient': False,
                'reason': 'No data available',
                'data_points': 0,
                'days_covered': 0
            }
        
        # Calculate date range
        if 'date' in data.columns:
            date_range = (data['date'].max() - data['date'].min()).days
        else:
            date_range = len(data)
        
        # Check sufficiency
        sufficient = len(data) >= min_data_points and date_range >= min_days
        
        result = {
            'sufficient': sufficient,
            'data_points': len(data),
            'days_covered': date_range,
            'min_required_points': min_data_points,
            'min_required_days': min_days
        }
        
        if not sufficient:
            if len(data) < min_data_points:
                result['reason'] = f'Insufficient data points: {len(data)} < {min_data_points}'
            else:
                result['reason'] = f'Insufficient time coverage: {date_range} days < {min_days} days'
        
        return result
    
    @staticmethod
    def resample_to_daily(data: pd.DataFrame) -> pd.DataFrame:
        """
        Resample data to daily frequency.
        
        Args:
            data: Input DataFrame with 'date' column
            
        Returns:
            DataFrame with daily frequency
        """
        if 'date' not in data.columns:
            raise ValueError("Data must contain 'date' column")
        
        data = data.copy()
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date')
        
        # Resample to daily, summing consumption
        if 'consumption' in data.columns:
            daily = data.resample('D').sum()
        else:
            daily = data.resample('D').first()
        
        # Fill missing dates
        daily = daily.fillna(0)
        
        # Reset index
        daily = daily.reset_index()
        
        logger.info(f"Resampled to {len(daily)} daily records")
        
        return daily
