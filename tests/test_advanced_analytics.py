"""
Tests for Advanced Analytics & ML Models - Phase 10
"""

import pytest
from pathlib import Path
import sys
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.advanced_analytics import (
    AdvancedAnalyticsEngine,
    ModelType,
    TrendType,
)


class TestAdvancedAnalyticsEngine:
    """Test advanced analytics and ML models"""

    def test_time_series_analysis(self):
        """Test time series analysis"""
        engine = AdvancedAnalyticsEngine()

        values = [10, 12, 15, 18, 22, 25, 28, 32, 35, 38]
        result = engine.analyze_time_series("cpu_usage", values)

        assert "statistics" in result
        assert "trend" in result
        assert result["statistics"]["mean"] > 0
        assert result["data_points"] == 10

    def test_time_series_trend_improving(self):
        """Test time series trend detection - improving"""
        engine = AdvancedAnalyticsEngine()

        values = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
        result = engine.analyze_time_series("metric", values)

        assert result["trend"] == "improving"

    def test_time_series_trend_degrading(self):
        """Test time series trend detection - degrading"""
        engine = AdvancedAnalyticsEngine()

        values = [28, 26, 24, 22, 20, 18, 16, 14, 12, 10]
        result = engine.analyze_time_series("metric", values)

        assert result["trend"] == "degrading"

    def test_forecast_time_series(self):
        """Test time series forecasting"""
        engine = AdvancedAnalyticsEngine()

        values = [10, 12, 14, 16, 18, 20, 22, 24]
        forecast = engine.forecast_time_series("metric", values, periods=5)

        assert len(forecast.forecast_points) == 5
        assert len(forecast.confidence_interval_low) == 5
        assert len(forecast.confidence_interval_high) == 5
        assert forecast.method == "exponential_smoothing"

    def test_correlation_analysis_positive(self):
        """Test positive correlation analysis"""
        engine = AdvancedAnalyticsEngine()

        values_a = [1, 2, 3, 4, 5]
        values_b = [2, 4, 6, 8, 10]

        analysis = engine.analyze_correlation("metric_a", values_a, "metric_b", values_b)

        assert analysis is not None
        assert analysis.correlation_coefficient > 0.9
        assert analysis.direction == "positive"
        assert analysis.strength == "strong"

    def test_correlation_analysis_negative(self):
        """Test negative correlation analysis"""
        engine = AdvancedAnalyticsEngine()

        values_a = [1, 2, 3, 4, 5]
        values_b = [10, 8, 6, 4, 2]

        analysis = engine.analyze_correlation("metric_a", values_a, "metric_b", values_b)

        assert analysis is not None
        assert analysis.correlation_coefficient < -0.9
        assert analysis.direction == "negative"

    def test_correlation_weak(self):
        """Test weak correlation"""
        engine = AdvancedAnalyticsEngine()

        values_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        values_b = [10, 5, 9, 3, 8, 2, 7, 4, 6, 1]  # Nearly random

        analysis = engine.analyze_correlation("a", values_a, "b", values_b)

        assert analysis is not None
        # Should have weak or no correlation
        assert analysis.strength in ["weak", "moderate"] or abs(analysis.correlation_coefficient) < 0.5

    def test_cluster_anomalies(self):
        """Test anomaly clustering"""
        engine = AdvancedAnalyticsEngine()

        anomalies = [
            {"id": "anom_1", "value": 10, "frequency": 5},
            {"id": "anom_2", "value": 12, "frequency": 6},
            {"id": "anom_3", "value": 50, "frequency": 2},
            {"id": "anom_4", "value": 52, "frequency": 3},
        ]

        clusters = engine.cluster_anomalies(anomalies, num_clusters=2)

        assert len(clusters) > 0
        assert all(hasattr(c, "cluster_id") for c in clusters)

    def test_train_model(self):
        """Test model training"""
        engine = AdvancedAnalyticsEngine()

        features = [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]
        labels = [1, 2, 3, 4, 5]

        model = engine.train_model(ModelType.LINEAR_REGRESSION, features, labels)

        assert model.model_id.startswith("model_")
        assert model.model_type == ModelType.LINEAR_REGRESSION
        assert 0 <= model.accuracy <= 1
        assert 0 <= model.f1_score <= 1
        assert model.training_time_seconds >= 0

    def test_get_model_performance(self):
        """Test retrieving model performance"""
        engine = AdvancedAnalyticsEngine()

        features = [[1, 2], [2, 3], [3, 4]]
        labels = [1, 2, 3]

        model = engine.train_model(ModelType.DECISION_TREE, features, labels)
        retrieved = engine.get_model_performance(model.model_id)

        assert retrieved is not None
        assert retrieved.model_id == model.model_id

    def test_list_models(self):
        """Test listing trained models"""
        engine = AdvancedAnalyticsEngine()

        features = [[1, 2], [2, 3], [3, 4]]
        labels = [1, 2, 3]

        engine.train_model(ModelType.LINEAR_REGRESSION, features, labels)
        engine.train_model(ModelType.RANDOM_FOREST, features, labels)

        models = engine.list_models()

        assert len(models) == 2

    def test_predict_code_quality(self):
        """Test code quality prediction"""
        engine = AdvancedAnalyticsEngine()

        features = {
            "complexity": 5.0,
            "test_coverage": 85.0,
            "duplication": 10.0,
            "documentation": 90.0,
        }

        result = engine.predict_code_quality(features)

        assert "predicted_quality" in result
        assert 0 <= result["predicted_quality"] <= 100
        assert "confidence" in result
        assert "contributing_factors" in result

    def test_predict_refactoring_effort_low(self):
        """Test low refactoring effort prediction"""
        engine = AdvancedAnalyticsEngine()

        result = engine.predict_refactoring_effort(
            pattern_complexity=1.0,
            lines_of_code=20,
            number_of_dependencies=2
        )

        assert result["effort_level"] == "low"
        assert result["estimated_hours"] == 1

    def test_predict_refactoring_effort_high(self):
        """Test high refactoring effort prediction"""
        engine = AdvancedAnalyticsEngine()

        result = engine.predict_refactoring_effort(
            pattern_complexity=15.0,
            lines_of_code=500,
            number_of_dependencies=30
        )

        assert result["effort_level"] == "high"
        assert result["estimated_hours"] == 8

    def test_model_performance_serialization(self):
        """Test model performance to dict"""
        engine = AdvancedAnalyticsEngine()

        features = [[1, 2], [2, 3], [3, 4]]
        labels = [1, 2, 3]

        model = engine.train_model(ModelType.LINEAR_REGRESSION, features, labels)
        model_dict = model.to_dict()

        assert model_dict["type"] == "linear_regression"
        assert "accuracy" in model_dict
        assert "f1_score" in model_dict

    def test_correlation_serialization(self):
        """Test correlation analysis serialization"""
        engine = AdvancedAnalyticsEngine()

        values_a = [1, 2, 3, 4, 5]
        values_b = [2, 4, 6, 8, 10]

        analysis = engine.analyze_correlation("a", values_a, "b", values_b)
        analysis_dict = analysis.to_dict()

        assert analysis_dict["metric_a"] == "a"
        assert "correlation" in analysis_dict
        assert "strength" in analysis_dict

    def test_forecast_serialization(self):
        """Test forecast serialization"""
        engine = AdvancedAnalyticsEngine()

        values = [10, 12, 14, 16, 18]
        forecast = engine.forecast_time_series("metric", values, periods=3)

        forecast_dict = forecast.to_dict()

        assert forecast_dict["metric"] == "metric"
        assert len(forecast_dict["forecast"]) == 3
        assert "confidence_low" in forecast_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
