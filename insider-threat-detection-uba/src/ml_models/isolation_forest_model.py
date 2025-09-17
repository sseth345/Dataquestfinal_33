"""
Isolation Forest model for anomaly detection.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import GridSearchCV
import joblib

from .base_model import BaseModel


class IsolationForestModel(BaseModel):
    """
    Isolation Forest model for detecting anomalies in user behavior.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Isolation Forest specific parameters
        self.n_estimators = config.get('n_estimators', 100)
        self.contamination = config.get('contamination', 0.1)
        self.max_samples = config.get('max_samples', 'auto')
        self.max_features = config.get('max_features', 1.0)
        self.random_state = config.get('random_state', 42)
        
        # Create model
        self.model = self._create_model()
    
    def get_model_name(self) -> str:
        return "Isolation Forest"
    
    def _create_model(self) -> IsolationForest:
        """
        Create and return the Isolation Forest model.
        
        Returns:
            IsolationForest model instance
        """
        return IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            max_samples=self.max_samples,
            max_features=self.max_features,
            random_state=self.random_state,
            n_jobs=-1
        )
    
    def train(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Train the Isolation Forest model.
        
        Args:
            X: Training features
            y: Not used for unsupervised learning
            
        Returns:
            Training metrics
        """
        if X.size == 0:
            raise ValueError("Training data is empty")
        
        self.logger.info(f"Training Isolation Forest with {X.shape[0]} samples and {X.shape[1]} features")
        
        try:
            # Fit the model
            self.model.fit(X)
            self.is_trained = True
            
            # Calculate training metrics
            train_predictions = self.predict(X)
            train_scores = self.model.score_samples(X)
            
            metrics = {
                'n_samples': X.shape[0],
                'n_features': X.shape[1],
                'n_estimators': self.n_estimators,
                'contamination': self.contamination,
                'anomaly_count': np.sum(train_predictions == -1),
                'anomaly_ratio': np.mean(train_predictions == -1),
                'avg_anomaly_score': np.mean(train_scores),
                'min_anomaly_score': np.min(train_scores),
                'max_anomaly_score': np.max(train_scores)
            }
            
            self.logger.info(f"Training completed. Detected {metrics['anomaly_count']} anomalies "
                           f"({metrics['anomaly_ratio']:.2%} of data)")
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"Error training Isolation Forest: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the trained model.
        
        Args:
            X: Features for prediction
            
        Returns:
            Predictions (-1 for anomaly, 1 for normal)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        if X.size == 0:
            return np.array([])
        
        try:
            predictions = self.model.predict(X)
            return predictions
        
        except Exception as e:
            self.logger.error(f"Error making predictions: {str(e)}")
            raise
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get anomaly scores for the samples.
        
        Args:
            X: Features for prediction
            
        Returns:
            Anomaly scores (lower scores indicate more anomalous)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        if X.size == 0:
            return np.array([])
        
        try:
            scores = self.model.score_samples(X)
            return scores
        
        except Exception as e:
            self.logger.error(f"Error getting anomaly scores: {str(e)}")
            raise
    
    def get_anomaly_threshold(self) -> float:
        """
        Get the anomaly threshold used by the model.
        
        Returns:
            Anomaly threshold value
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to get threshold")
        
        return self.model.threshold_
    
    def detect_anomalies(self, X: np.ndarray, return_scores: bool = False) -> Dict[str, Any]:
        """
        Detect anomalies and return detailed results.
        
        Args:
            X: Features for anomaly detection
            return_scores: Whether to include anomaly scores in results
            
        Returns:
            Dictionary containing anomaly detection results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        predictions = self.predict(X)
        scores = self.predict_proba(X)
        
        # Identify anomalous indices
        anomaly_indices = np.where(predictions == -1)[0]
        normal_indices = np.where(predictions == 1)[0]
        
        results = {
            'total_samples': len(X),
            'anomaly_count': len(anomaly_indices),
            'normal_count': len(normal_indices),
            'anomaly_ratio': len(anomaly_indices) / len(X),
            'anomaly_indices': anomaly_indices.tolist(),
            'threshold': self.get_anomaly_threshold()
        }
        
        if return_scores:
            results['anomaly_scores'] = scores.tolist()
            results['anomalous_scores'] = scores[anomaly_indices].tolist()
            results['normal_scores'] = scores[normal_indices].tolist()
        
        return results
    
    def tune_hyperparameters(self, X: np.ndarray, param_grid: Optional[Dict[str, List]] = None) -> Dict[str, Any]:
        """
        Tune hyperparameters using grid search.
        
        Args:
            X: Training data
            param_grid: Parameter grid for grid search
            
        Returns:
            Best parameters and scores
        """
        if param_grid is None:
            param_grid = {
                'n_estimators': [50, 100, 200],
                'contamination': [0.05, 0.1, 0.15, 0.2],
                'max_features': [0.5, 0.7, 1.0]
            }
        
        self.logger.info("Starting hyperparameter tuning...")
        
        # Create a scoring function for anomaly detection
        def anomaly_score(estimator, X):
            """Custom scoring function for anomaly detection."""
            predictions = estimator.predict(X)
            scores = estimator.score_samples(X)
            
            # Return negative mean score (higher is better for GridSearchCV)
            return -np.mean(scores)
        
        try:
            # Perform grid search
            grid_search = GridSearchCV(
                estimator=IsolationForest(random_state=self.random_state, n_jobs=1),
                param_grid=param_grid,
                scoring=anomaly_score,
                cv=3,  # 3-fold cross validation
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X)
            
            # Update model with best parameters
            self.model = grid_search.best_estimator_
            self.n_estimators = grid_search.best_params_['n_estimators']
            self.contamination = grid_search.best_params_['contamination']
            self.max_features = grid_search.best_params_['max_features']
            
            self.is_trained = True
            
            results = {
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'cv_results': grid_search.cv_results_
            }
            
            self.logger.info(f"Hyperparameter tuning completed. Best params: {grid_search.best_params_}")
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error during hyperparameter tuning: {str(e)}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance based on how features contribute to anomaly detection.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            return {}
        
        # For Isolation Forest, we can approximate feature importance
        # by analyzing the path lengths in decision trees
        feature_importance = {}
        
        if hasattr(self.model, 'estimators_') and self.feature_columns:
            n_features = len(self.feature_columns)
            importance_scores = np.zeros(n_features)
            
            # Calculate average feature importance across all trees
            for tree in self.model.estimators_:
                if hasattr(tree, 'feature_importances_'):
                    importance_scores += tree.feature_importances_
            
            # Normalize
            importance_scores /= len(self.model.estimators_)
            
            # Create feature importance dictionary
            for i, feature_name in enumerate(self.feature_columns):
                feature_importance[feature_name] = float(importance_scores[i])
        
        return feature_importance
    
    def explain_anomaly(self, X: np.ndarray, sample_index: int) -> Dict[str, Any]:
        """
        Explain why a specific sample was classified as an anomaly.
        
        Args:
            X: Feature matrix
            sample_index: Index of the sample to explain
            
        Returns:
            Explanation dictionary
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before explaining anomalies")
        
        if sample_index >= len(X):
            raise ValueError("Sample index out of range")
        
        sample = X[sample_index:sample_index+1]
        prediction = self.predict(sample)[0]
        score = self.predict_proba(sample)[0]
        
        explanation = {
            'sample_index': sample_index,
            'prediction': 'Anomaly' if prediction == -1 else 'Normal',
            'anomaly_score': float(score),
            'threshold': float(self.get_anomaly_threshold()),
            'is_anomaly': prediction == -1,
            'features': {}
        }
        
        # Add feature values
        if self.feature_columns:
            for i, feature_name in enumerate(self.feature_columns):
                if i < X.shape[1]:
                    explanation['features'][feature_name] = float(X[sample_index, i])
        
        # Get feature importance for context
        feature_importance = self.get_feature_importance()
        if feature_importance:
            explanation['feature_importance'] = feature_importance
        
        return explanation