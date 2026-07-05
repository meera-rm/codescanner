"""
Predictive Analyzer - Phase 6.1.3
Predicts code quality, risks, and detects anomalies in patterns
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import time
from statistics import mean, stdev

from .codebase_learner import (
    CodebaseIntelligence,
    CodePatternType,
    get_codebase_intelligence
)


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class AnomalyType(str, Enum):
    """Types of anomalies detected"""
    UNUSUAL_COMPLEXITY = "unusual_complexity"
    PATTERN_DRIFT = "pattern_drift"
    REGRESSION = "regression"
    OUTLIER = "outlier"
    DEGRADATION = "degradation"


@dataclass
class QualityPrediction:
    """Code quality prediction"""
    pattern_id: str
    current_score: float
    predicted_score: float
    confidence: float
    improvement_potential: float
    key_factors: List[str]
    estimated_effort: str  # "low", "medium", "high"
    roi_estimate: float  # Return on Investment (0-1)


@dataclass
class RiskAssessment:
    """Risk assessment for refactoring"""
    pattern_id: str
    risk_level: RiskLevel
    risk_score: float  # 0-1
    breaking_risk: float
    performance_risk: float
    compatibility_risk: float
    recommendations: List[str]
    mitigation_strategies: List[str]


@dataclass
class AnomalyDetected:
    """Detected anomaly in pattern"""
    anomaly_id: str
    anomaly_type: AnomalyType
    pattern_id: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    confidence: float
    detected_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis over time"""
    language: str
    metric_name: str
    current_value: float
    historical_average: float
    trend_direction: str  # "improving", "degrading", "stable"
    trend_strength: float  # 0-1
    forecast_next_period: float
    confidence: float


class PredictiveAnalyzer:
    """Analyzes patterns and predicts code quality outcomes"""

    def __init__(self):
        self.intelligence = get_codebase_intelligence()
        self.anomalies: Dict[str, AnomalyDetected] = {}
        self.history_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.trend_cache: Dict[str, List[float]] = {}

    def predict_quality_improvement(
        self,
        pattern_id: str,
        target_language: str
    ) -> Optional[QualityPrediction]:
        """Predict quality improvement potential"""
        pattern = self.intelligence.patterns.get(pattern_id)
        if not pattern:
            return None

        # Get historical improvements
        improvements = self._get_historical_improvements(pattern_id)
        if not improvements:
            return None

        current_score = self._calculate_pattern_score(pattern)
        avg_improvement = mean(improvements) if improvements else 0
        predicted_score = min(1.0, current_score + avg_improvement)
        improvement_potential = predicted_score - current_score

        # Calculate confidence
        confidence = self._calculate_prediction_confidence(pattern, improvements)

        # Estimate effort
        estimated_effort = self._estimate_refactoring_effort(pattern)

        # Calculate ROI
        roi = improvement_potential / max(0.1, self._estimate_effort_score(estimated_effort))

        # Key factors
        key_factors = self._extract_key_factors(pattern, improvements)

        return QualityPrediction(
            pattern_id=pattern_id,
            current_score=current_score,
            predicted_score=predicted_score,
            confidence=confidence,
            improvement_potential=improvement_potential,
            key_factors=key_factors,
            estimated_effort=estimated_effort,
            roi_estimate=min(1.0, roi)
        )

    def assess_refactoring_risk(
        self,
        pattern_id: str,
        refactored_code: str
    ) -> Optional[RiskAssessment]:
        """Assess risk of refactoring"""
        pattern = self.intelligence.patterns.get(pattern_id)
        if not pattern:
            return None

        # Calculate risk factors
        breaking_risk = self._calculate_breaking_risk(pattern, refactored_code)
        performance_risk = self._calculate_performance_risk(pattern, refactored_code)
        compatibility_risk = self._calculate_compatibility_risk(pattern)

        # Overall risk score
        risk_score = (breaking_risk * 0.5 + performance_risk * 0.3 + compatibility_risk * 0.2)

        # Determine risk level
        risk_level = self._score_to_risk_level(risk_score)

        # Generate recommendations
        recommendations = self._generate_risk_recommendations(
            breaking_risk, performance_risk, compatibility_risk
        )

        # Mitigation strategies
        mitigations = self._generate_mitigations(pattern, risk_level)

        return RiskAssessment(
            pattern_id=pattern_id,
            risk_level=risk_level,
            risk_score=risk_score,
            breaking_risk=breaking_risk,
            performance_risk=performance_risk,
            compatibility_risk=compatibility_risk,
            recommendations=recommendations,
            mitigation_strategies=mitigations
        )

    def detect_anomalies(self, language: str) -> List[AnomalyDetected]:
        """Detect anomalies in codebase patterns"""
        detected = []

        # Get patterns for language
        patterns = [p for p in self.intelligence.patterns.values() if p.language == language]
        if not patterns:
            return detected

        # Calculate statistics
        complexities = [p.complexity for p in patterns]
        avg_complexity = mean(complexities)
        complexity_stdev = stdev(complexities) if len(complexities) > 1 else 0

        for pattern in patterns:
            # Check for unusual complexity
            if complexity_stdev > 0:
                z_score = (pattern.complexity - avg_complexity) / complexity_stdev
                if abs(z_score) > 1.5:  # Lower outlier threshold
                    anomaly = AnomalyDetected(
                        anomaly_id=f"anom_{pattern.pattern_id}_{int(time.time()*1000)}",
                        anomaly_type=AnomalyType.UNUSUAL_COMPLEXITY,
                        pattern_id=pattern.pattern_id,
                        severity="high" if abs(z_score) > 3 else "medium",
                        description=f"Complexity {pattern.complexity:.1f} is {abs(z_score):.1f} std devs from mean",
                        confidence=min(0.99, abs(z_score) / 4),
                        metadata={"z_score": z_score, "avg": avg_complexity}
                    )
                    detected.append(anomaly)
                    self.anomalies[anomaly.anomaly_id] = anomaly

            # Check for pattern drift (only if many occurrences)
            success_rate = self.intelligence._calculate_success_rate(pattern.pattern_id)
            if pattern.occurrences > 3 and success_rate < 0.4:
                anomaly = AnomalyDetected(
                    anomaly_id=f"anom_{pattern.pattern_id}_drift_{int(time.time()*1000)}",
                    anomaly_type=AnomalyType.PATTERN_DRIFT,
                    pattern_id=pattern.pattern_id,
                    severity="medium",
                    description=f"Pattern has low success rate ({success_rate:.0%}) despite {pattern.occurrences} occurrences",
                    confidence=success_rate,
                    metadata={"success_rate": success_rate, "occurrences": pattern.occurrences}
                )
                detected.append(anomaly)
                self.anomalies[anomaly.anomaly_id] = anomaly

        return detected

    def analyze_trends(self, language: str) -> List[TrendAnalysis]:
        """Analyze trends over time"""
        trends = []

        patterns = [p for p in self.intelligence.patterns.values() if p.language == language]
        if not patterns:
            return trends

        # Complexity trend
        complexities = [p.complexity for p in patterns]
        complexity_trend = self._calculate_trend(complexities)
        if complexity_trend:
            trends.append(TrendAnalysis(
                language=language,
                metric_name="complexity",
                current_value=complexities[-1] if complexities else 0,
                historical_average=mean(complexities),
                trend_direction=complexity_trend["direction"],
                trend_strength=complexity_trend["strength"],
                forecast_next_period=complexity_trend["forecast"],
                confidence=complexity_trend["confidence"]
            ))

        # Quality trend
        improvements = self._get_all_improvements(language)
        quality_trend = self._calculate_trend(improvements)
        if quality_trend:
            trends.append(TrendAnalysis(
                language=language,
                metric_name="quality_improvement",
                current_value=improvements[-1] if improvements else 0,
                historical_average=mean(improvements),
                trend_direction=quality_trend["direction"],
                trend_strength=quality_trend["strength"],
                forecast_next_period=quality_trend["forecast"],
                confidence=quality_trend["confidence"]
            ))

        return trends

    def get_risk_report(self, language: str) -> Dict[str, Any]:
        """Generate risk report for language"""
        patterns = [p for p in self.intelligence.patterns.values() if p.language == language]

        high_risk = 0
        medium_risk = 0
        low_risk = 0

        for pattern in patterns:
            assessment = self.assess_refactoring_risk(pattern.pattern_id, "")
            if assessment:
                if assessment.risk_level == RiskLevel.CRITICAL or assessment.risk_level == RiskLevel.HIGH:
                    high_risk += 1
                elif assessment.risk_level == RiskLevel.MEDIUM:
                    medium_risk += 1
                else:
                    low_risk += 1

        total = len(patterns)
        return {
            "language": language,
            "total_patterns": total,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "high_risk_percentage": (high_risk / total * 100) if total > 0 else 0,
            "anomaly_count": len([a for a in self.anomalies.values() if a.pattern_id in [p.pattern_id for p in patterns]]),
            "anomalies": self.detect_anomalies(language)
        }

    # Helper methods

    def _get_historical_improvements(self, pattern_id: str) -> List[float]:
        """Get historical quality improvements for pattern"""
        improvements = []
        for history in self.intelligence.refactoring_history.values():
            if history.pattern_id == pattern_id:
                improvements.append(history.quality_improvement)
        return improvements

    def _get_all_improvements(self, language: str) -> List[float]:
        """Get all improvements for language"""
        improvements = []
        for history in self.intelligence.refactoring_history.values():
            pattern = self.intelligence.patterns.get(history.pattern_id)
            if pattern and pattern.language == language:
                improvements.append(history.quality_improvement)
        return improvements

    def _calculate_pattern_score(self, pattern: Any) -> float:
        """Calculate pattern quality score"""
        # Score based on complexity and success rate
        max_complexity = 20
        complexity_score = max(0, 1 - (pattern.complexity / max_complexity))
        success_rate = self.intelligence._calculate_success_rate(pattern.pattern_id)
        return complexity_score * 0.6 + success_rate * 0.4

    def _calculate_prediction_confidence(self, pattern: Any, improvements: List[float]) -> float:
        """Calculate confidence in prediction"""
        if not improvements:
            return 0.3

        # More occurrences = more confidence
        occurrence_factor = min(pattern.occurrences / 10, 1.0)
        # More historical data = more confidence
        data_factor = min(len(improvements) / 5, 1.0)
        return min(0.95, (occurrence_factor * 0.5 + data_factor * 0.5))

    def _estimate_refactoring_effort(self, pattern: Any) -> str:
        """Estimate effort required"""
        loc = pattern.lines_of_code
        complexity = pattern.complexity

        effort_score = (loc / 50) * 0.5 + (complexity / 10) * 0.5

        if effort_score < 1:
            return "low"
        elif effort_score < 2:
            return "medium"
        else:
            return "high"

    def _estimate_effort_score(self, effort: str) -> float:
        """Convert effort string to numeric score"""
        return {"low": 0.3, "medium": 0.6, "high": 0.9}[effort]

    def _extract_key_factors(self, pattern: Any, improvements: List[float]) -> List[str]:
        """Extract key improvement factors"""
        factors = []

        if pattern.complexity > 10:
            factors.append("High complexity - potential for significant simplification")

        if len(improvements) > 0 and mean(improvements) > 0.2:
            factors.append("History shows strong improvement potential")

        if pattern.occurrences > 5:
            factors.append("Pattern appears frequently - wide impact")

        return factors

    def _calculate_breaking_risk(self, pattern: Any, refactored_code: str) -> float:
        """Calculate risk of breaking changes"""
        # Risk if removing features or changing API
        if len(refactored_code) < len(str(pattern)) * 0.7:
            return 0.4
        return 0.1

    def _calculate_performance_risk(self, pattern: Any, refactored_code: str) -> float:
        """Calculate performance regression risk"""
        # Risk based on complexity change
        if pattern.complexity > 15:
            return 0.3
        return 0.1

    def _calculate_compatibility_risk(self, pattern: Any) -> float:
        """Calculate compatibility risk"""
        # Risk increases with number of occurrences
        return min(0.5, pattern.occurrences / 20)

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to level"""
        if score > 0.8:
            return RiskLevel.CRITICAL
        elif score > 0.6:
            return RiskLevel.HIGH
        elif score > 0.4:
            return RiskLevel.MEDIUM
        elif score > 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    def _generate_risk_recommendations(
        self,
        breaking: float,
        performance: float,
        compatibility: float
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        if breaking > 0.3:
            recommendations.append("Add comprehensive tests before refactoring")

        if performance > 0.3:
            recommendations.append("Benchmark before and after refactoring")

        if compatibility > 0.3:
            recommendations.append("Update all dependent code")

        return recommendations or ["Proceed with standard precautions"]

    def _generate_mitigations(self, pattern: Any, risk_level: RiskLevel) -> List[str]:
        """Generate mitigation strategies"""
        strategies = ["Use version control to track changes"]

        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            strategies.extend([
                "Create feature branch for isolation",
                "Add automated tests",
                "Code review by senior engineer",
                "Staged rollout strategy"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            strategies.extend([
                "Code review required",
                "Test coverage > 80%"
            ])

        return strategies

    def _calculate_trend(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """Calculate trend from values"""
        if len(values) < 2:
            return None

        # Simple linear regression
        n = len(values)
        x = list(range(n))
        y = values

        x_mean = mean(x)
        y_mean = mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return None

        slope = numerator / denominator
        trend_strength = min(1.0, abs(slope) / 0.1)

        direction = "improving" if slope > 0.01 else "degrading" if slope < -0.01 else "stable"

        # Forecast next value
        next_x = n
        forecast = y_mean + slope * (next_x - x_mean)

        return {
            "direction": direction,
            "strength": trend_strength,
            "forecast": forecast,
            "confidence": min(0.9, trend_strength * 0.8 + 0.5)
        }


# Global instance
_global_predictive_analyzer = PredictiveAnalyzer()


def get_predictive_analyzer() -> PredictiveAnalyzer:
    """Get global predictive analyzer instance"""
    return _global_predictive_analyzer
