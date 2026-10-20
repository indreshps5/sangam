# SANGAM ML Module
# Demand Forecasting & Model Evaluation

## Overview
This module contains machine learning models for demand forecasting,
route optimization, and supply chain analytics.

## Structure
```
ml/
├── src/
│   ├── forecasting/     # Time-series forecasting models
│   ├── optimization/    # Route & resource optimization
│   ├── evaluation/      # Model evaluation & metrics
│   └── features/        # Feature engineering pipelines
├── notebooks/           # Jupyter notebooks for exploration
├── tests/               # ML-specific tests
├── artifacts/           # Trained model artifacts (gitignored)
└── requirements.txt     # ML dependencies
```

## Models
- **ARIMA/SARIMA**: Baseline time-series forecasting
- **Prophet**: Seasonal demand forecasting
- **XGBoost**: Feature-based demand prediction
- **LSTM**: Deep learning sequence forecasting

## Usage
```python
from ml.src.forecasting.demand import DemandForecaster

forecaster = DemandForecaster(model_type="xgboost")
forecaster.fit(historical_data)
predictions = forecaster.predict(horizon_days=30)
```
