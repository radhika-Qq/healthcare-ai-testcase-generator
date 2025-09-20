"""
Predictive Test Prioritization Module

Uses AI/ML to analyze past defect data, requirement criticality, and code risk metrics
to automatically assign priority scores to generated test cases.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

logger = logging.getLogger(__name__)


@dataclass
class RiskFactor:
    """Individual risk factor for test prioritization."""
    factor_name: str
    factor_value: float
    weight: float
    impact: str  # high, medium, low
    description: str


@dataclass
class TestPriorityScore:
    """Test case priority score with risk factors."""
    test_case_id: str
    priority_score: float  # 0-100
    risk_level: str  # critical, high, medium, low
    risk_factors: List[RiskFactor]
    confidence: float  # 0-1
    recommendation: str
    generated_at: str


class PredictivePrioritizer:
    """AI/ML-based test case prioritization system."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the predictive prioritizer."""
        self.model_path = Path(model_path) if model_path else Path("models/priority_model.pkl")
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = []
        self.training_data = []
        
        # Risk factor weights (can be adjusted based on domain expertise)
        self.risk_weights = {
            'requirement_criticality': 0.25,
            'defect_history': 0.20,
            'code_complexity': 0.15,
            'compliance_impact': 0.20,
            'user_impact': 0.10,
            'change_frequency': 0.10
        }
        
    def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the priority prediction model.
        
        Args:
            training_data: Historical test case data with outcomes
            
        Returns:
            Training results and model performance metrics
        """
        logger.info("Training priority prediction model...")
        
        # Prepare training data
        X, y = self._prepare_training_data(training_data)
        
        if len(X) < 10:
            logger.warning("Insufficient training data. Using rule-based prioritization.")
            return self._create_rule_based_model()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train multiple models and select best
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        best_model = None
        best_score = -float('inf')
        best_model_name = None
        
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            score = r2_score(y_test, y_pred)
            
            if score > best_score:
                best_score = score
                best_model = model
                best_model_name = name
        
        self.model = best_model
        
        # Calculate performance metrics
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Save model
        self._save_model()
        
        results = {
            'model_name': best_model_name,
            'r2_score': r2,
            'mse': mse,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_importance': self._get_feature_importance()
        }
        
        logger.info(f"Model training completed. R² Score: {r2:.3f}")
        return results
    
    def predict_priority(self, test_case: Any, context: Dict[str, Any] = None) -> TestPriorityScore:
        """
        Predict priority score for a test case.
        
        Args:
            test_case: Test case object
            context: Additional context data
            
        Returns:
            Test priority score with risk factors
        """
        if context is None:
            context = {}
            
        # Extract features
        features = self._extract_features(test_case, context)
        
        if self.model is not None:
            # Use ML model
            features_scaled = self.scaler.transform([features])
            priority_score = self.model.predict(features_scaled)[0]
            confidence = self._calculate_confidence(features)
        else:
            # Use rule-based approach
            priority_score, confidence = self._rule_based_priority(features)
        
        # Ensure score is within bounds
        priority_score = max(0, min(100, priority_score))
        
        # Determine risk level
        risk_level = self._determine_risk_level(priority_score)
        
        # Generate risk factors
        risk_factors = self._generate_risk_factors(features, test_case, context)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(priority_score, risk_factors)
        
        return TestPriorityScore(
            test_case_id=getattr(test_case, 'id', 'unknown'),
            priority_score=priority_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            confidence=confidence,
            recommendation=recommendation,
            generated_at=datetime.now().isoformat()
        )
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for model training."""
        X = []
        y = []
        
        for data in training_data:
            features = self._extract_features_from_data(data)
            priority = data.get('actual_priority', data.get('priority_score', 50))
            
            X.append(features)
            y.append(priority)
        
        return np.array(X), np.array(y)
    
    def _extract_features(self, test_case: Any, context: Dict[str, Any]) -> List[float]:
        """Extract features for priority prediction."""
        features = []
        
        # Requirement criticality
        req_priority = getattr(test_case, 'priority', None)
        if req_priority:
            priority_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            if hasattr(req_priority, 'value'):
                criticality = priority_map.get(req_priority.value, 2)
            else:
                criticality = priority_map.get(str(req_priority).lower(), 2)
        else:
            criticality = 2  # Default medium
        
        features.append(criticality)
        
        # Test case type complexity
        tc_type = getattr(test_case, 'test_case_type', None)
        if tc_type:
            type_map = {
                'compliance': 4, 'security': 4, 'performance': 3,
                'integration': 3, 'boundary': 2, 'negative': 2, 'positive': 1
            }
            if hasattr(tc_type, 'value'):
                complexity = type_map.get(tc_type.value, 2)
            else:
                complexity = type_map.get(str(tc_type).lower(), 2)
        else:
            complexity = 2
        
        features.append(complexity)
        
        # Number of test steps
        test_steps = getattr(test_case, 'test_steps', [])
        step_count = len(test_steps)
        features.append(min(step_count / 10.0, 1.0))  # Normalize to 0-1
        
        # Compliance references count
        compliance_refs = getattr(test_case, 'compliance_refs', [])
        compliance_count = len(compliance_refs)
        features.append(min(compliance_count / 5.0, 1.0))  # Normalize to 0-1
        
        # Historical defect data
        defect_history = context.get('defect_history', {}).get(
            getattr(test_case, 'requirement_id', ''), 0
        )
        features.append(min(defect_history / 10.0, 1.0))  # Normalize to 0-1
        
        # Code complexity (if available)
        code_complexity = context.get('code_complexity', {}).get(
            getattr(test_case, 'requirement_id', ''), 0.5
        )
        features.append(code_complexity)
        
        # User impact score
        user_impact = context.get('user_impact', {}).get(
            getattr(test_case, 'requirement_id', ''), 0.5
        )
        features.append(user_impact)
        
        # Change frequency
        change_frequency = context.get('change_frequency', {}).get(
            getattr(test_case, 'requirement_id', ''), 0.1
        )
        features.append(change_frequency)
        
        return features
    
    def _extract_features_from_data(self, data: Dict[str, Any]) -> List[float]:
        """Extract features from training data dictionary."""
        features = []
        
        # Requirement criticality
        priority_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        criticality = priority_map.get(data.get('requirement_priority', 'medium').lower(), 2)
        features.append(criticality)
        
        # Test case type complexity
        type_map = {
            'compliance': 4, 'security': 4, 'performance': 3,
            'integration': 3, 'boundary': 2, 'negative': 2, 'positive': 1
        }
        complexity = type_map.get(data.get('test_case_type', 'positive').lower(), 2)
        features.append(complexity)
        
        # Number of test steps
        step_count = len(data.get('test_steps', []))
        features.append(min(step_count / 10.0, 1.0))
        
        # Compliance references count
        compliance_count = len(data.get('compliance_refs', []))
        features.append(min(compliance_count / 5.0, 1.0))
        
        # Historical defect data
        defect_history = data.get('defect_history', 0)
        features.append(min(defect_history / 10.0, 1.0))
        
        # Code complexity
        code_complexity = data.get('code_complexity', 0.5)
        features.append(code_complexity)
        
        # User impact score
        user_impact = data.get('user_impact', 0.5)
        features.append(user_impact)
        
        # Change frequency
        change_frequency = data.get('change_frequency', 0.1)
        features.append(change_frequency)
        
        return features
    
    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate confidence score for prediction."""
        # Simple confidence based on feature completeness and values
        non_zero_features = sum(1 for f in features if f > 0)
        completeness = non_zero_features / len(features)
        
        # Confidence based on feature value ranges
        normalized_features = [min(max(f, 0), 1) for f in features]
        variance = np.var(normalized_features)
        stability = 1 - variance  # Lower variance = higher stability
        
        confidence = (completeness + stability) / 2
        return max(0.1, min(1.0, confidence))
    
    def _rule_based_priority(self, features: List[float]) -> Tuple[float, float]:
        """Calculate priority using rule-based approach."""
        if len(features) < 8:
            return 50.0, 0.5  # Default medium priority
        
        criticality, complexity, step_count, compliance_count, defect_history, code_complexity, user_impact, change_frequency = features
        
        # Weighted score calculation
        score = (
            criticality * 25 +  # 0-100 scale
            complexity * 25 +
            step_count * 10 +
            compliance_count * 15 +
            defect_history * 10 +
            code_complexity * 10 +
            user_impact * 5
        )
        
        # Adjust for change frequency
        if change_frequency > 0.5:
            score *= 1.2  # Increase priority for frequently changed components
        
        confidence = 0.7  # Rule-based confidence
        return min(100, score), confidence
    
    def _determine_risk_level(self, priority_score: float) -> str:
        """Determine risk level based on priority score."""
        if priority_score >= 80:
            return 'critical'
        elif priority_score >= 60:
            return 'high'
        elif priority_score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _generate_risk_factors(self, features: List[float], test_case: Any, context: Dict[str, Any]) -> List[RiskFactor]:
        """Generate risk factors for the test case."""
        risk_factors = []
        
        if len(features) >= 8:
            criticality, complexity, step_count, compliance_count, defect_history, code_complexity, user_impact, change_frequency = features
            
            # Requirement criticality factor
            if criticality >= 3:
                risk_factors.append(RiskFactor(
                    factor_name="Requirement Criticality",
                    factor_value=criticality,
                    weight=self.risk_weights['requirement_criticality'],
                    impact="high" if criticality >= 3 else "medium",
                    description=f"Requirement has {['low', 'medium', 'high', 'critical'][int(criticality)-1]} criticality"
                ))
            
            # Defect history factor
            if defect_history > 0.3:
                risk_factors.append(RiskFactor(
                    factor_name="Defect History",
                    factor_value=defect_history,
                    weight=self.risk_weights['defect_history'],
                    impact="high" if defect_history > 0.7 else "medium",
                    description=f"Component has history of {defect_history:.1%} defect rate"
                ))
            
            # Code complexity factor
            if code_complexity > 0.7:
                risk_factors.append(RiskFactor(
                    factor_name="Code Complexity",
                    factor_value=code_complexity,
                    weight=self.risk_weights['code_complexity'],
                    impact="high" if code_complexity > 0.8 else "medium",
                    description=f"High code complexity ({code_complexity:.1%})"
                ))
            
            # Compliance impact factor
            if compliance_count > 0.6:
                risk_factors.append(RiskFactor(
                    factor_name="Compliance Impact",
                    factor_value=compliance_count,
                    weight=self.risk_weights['compliance_impact'],
                    impact="high",
                    description=f"Multiple compliance requirements ({compliance_count:.1%})"
                ))
            
            # User impact factor
            if user_impact > 0.7:
                risk_factors.append(RiskFactor(
                    factor_name="User Impact",
                    factor_value=user_impact,
                    weight=self.risk_weights['user_impact'],
                    impact="high" if user_impact > 0.8 else "medium",
                    description=f"High user impact ({user_impact:.1%})"
                ))
            
            # Change frequency factor
            if change_frequency > 0.5:
                risk_factors.append(RiskFactor(
                    factor_name="Change Frequency",
                    factor_value=change_frequency,
                    weight=self.risk_weights['change_frequency'],
                    impact="medium",
                    description=f"Frequently changed component ({change_frequency:.1%})"
                ))
        
        return risk_factors
    
    def _generate_recommendation(self, priority_score: float, risk_factors: List[RiskFactor]) -> str:
        """Generate recommendation based on priority score and risk factors."""
        if priority_score >= 80:
            return "Execute immediately - Critical priority with high risk factors"
        elif priority_score >= 60:
            return "Execute in next test cycle - High priority with significant risk factors"
        elif priority_score >= 40:
            return "Execute in regular test cycle - Medium priority with moderate risk factors"
        else:
            return "Execute when resources available - Low priority with minimal risk factors"
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model."""
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        feature_names = [
            'requirement_criticality', 'test_complexity', 'step_count',
            'compliance_count', 'defect_history', 'code_complexity',
            'user_impact', 'change_frequency'
        ]
        
        return dict(zip(feature_names, self.model.feature_importances_))
    
    def _save_model(self):
        """Save trained model and scaler."""
        self.model_path.parent.mkdir(exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'risk_weights': self.risk_weights,
            'trained_at': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, self.model_path)
        logger.info(f"Model saved to: {self.model_path}")
    
    def _load_model(self) -> bool:
        """Load trained model and scaler."""
        if not self.model_path.exists():
            return False
        
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data.get('feature_names', [])
            self.risk_weights = model_data.get('risk_weights', self.risk_weights)
            
            logger.info(f"Model loaded from: {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def _create_rule_based_model(self) -> Dict[str, Any]:
        """Create a rule-based model when insufficient training data."""
        logger.info("Creating rule-based prioritization model")
        
        return {
            'model_name': 'rule_based',
            'r2_score': 0.0,
            'mse': 0.0,
            'training_samples': 0,
            'test_samples': 0,
            'feature_importance': self.risk_weights
        }
    
    def batch_predict_priorities(self, test_cases: List[Any], context: Dict[str, Any] = None) -> List[TestPriorityScore]:
        """Predict priorities for multiple test cases."""
        if context is None:
            context = {}
        
        results = []
        for test_case in test_cases:
            try:
                priority_score = self.predict_priority(test_case, context)
                results.append(priority_score)
            except Exception as e:
                logger.error(f"Error predicting priority for {getattr(test_case, 'id', 'unknown')}: {e}")
                # Create default priority score
                results.append(TestPriorityScore(
                    test_case_id=getattr(test_case, 'id', 'unknown'),
                    priority_score=50.0,
                    risk_level='medium',
                    risk_factors=[],
                    confidence=0.5,
                    recommendation="Execute in regular test cycle - Default priority",
                    generated_at=datetime.now().isoformat()
                ))
        
        return results
    
    def generate_priority_report(self, priority_scores: List[TestPriorityScore]) -> Dict[str, Any]:
        """Generate comprehensive priority analysis report."""
        if not priority_scores:
            return {'error': 'No priority scores provided'}
        
        # Calculate statistics
        scores = [ps.priority_score for ps in priority_scores]
        confidences = [ps.confidence for ps in priority_scores]
        
        # Risk level distribution
        risk_levels = {}
        for ps in priority_scores:
            risk_levels[ps.risk_level] = risk_levels.get(ps.risk_level, 0) + 1
        
        # Top risk factors
        all_risk_factors = []
        for ps in priority_scores:
            all_risk_factors.extend(ps.risk_factors)
        
        factor_counts = {}
        for factor in all_risk_factors:
            factor_counts[factor.factor_name] = factor_counts.get(factor.factor_name, 0) + 1
        
        # Sort by frequency
        top_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'summary': {
                'total_test_cases': len(priority_scores),
                'average_priority_score': np.mean(scores),
                'median_priority_score': np.median(scores),
                'min_priority_score': np.min(scores),
                'max_priority_score': np.max(scores),
                'average_confidence': np.mean(confidences)
            },
            'risk_level_distribution': risk_levels,
            'top_risk_factors': top_factors,
            'high_priority_cases': [
                {
                    'test_case_id': ps.test_case_id,
                    'priority_score': ps.priority_score,
                    'risk_level': ps.risk_level,
                    'recommendation': ps.recommendation
                }
                for ps in priority_scores if ps.priority_score >= 70
            ],
            'generated_at': datetime.now().isoformat()
        }
