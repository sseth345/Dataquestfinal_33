"""
Base model class for all machine learning models.
"""

import os
import json
import joblib
import logging
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import sqlite3


class BaseModel(ABC):
    """
    Abstract base class for all ML models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.is_trained = False
        self.model_path = config.get('model_path', 'models/')
        self.db_path = config.get('database_path', 'data/threat_detection.db')
        
        # Ensure model directory exists
        os.makedirs(self.model_path, exist_ok=True)
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of this model.
        
        Returns:
            Model name as string
        """
        pass
    
    @abstractmethod
    def _create_model(self) -> Any:
        """
        Create and return the ML model instance.
        
        Returns:
            ML model instance
        """
        pass
    
    @abstractmethod
    def train(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            X: Training features
            y: Training labels (for supervised learning)
            
        Returns:
            Training metrics
        """
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the trained model.
        
        Args:
            X: Features for prediction
            
        Returns:
            Predictions
        """
        pass
    
    def load_data_from_db(self, query: Optional[str] = None, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> pd.DataFrame:
        """
        Load data from the database.
        
        Args:
            query: Custom SQL query (optional)
            start_time: Filter events after this time
            end_time: Filter events before this time
            
        Returns:
            DataFrame containing the loaded data
        """
        if query is None:
            query = """
                SELECT user_id, event_type, timestamp, source_ip, machine_name, 
                       event_data, risk_score
                FROM user_events
                WHERE 1=1
            """
            
            params = []
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC"
        else:
            params = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                self.logger.info(f"Loaded {len(df)} records from database")
                return df
        
        except Exception as e:
            self.logger.error(f"Error loading data from database: {str(e)}")
            return pd.DataFrame()
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Preprocess the data for training/prediction.
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            Tuple of (features, labels)
        """
        if df.empty:
            return np.array([]), None
        
        # Parse JSON event data
        df = self._parse_event_data(df)
        
        # Extract features
        features = self._extract_features(df)
        
        # Handle missing values
        features = self._handle_missing_values(features)
        
        # Scale features
        if hasattr(self.scaler, 'mean_'):
            # Scaler is already fitted
            X_scaled = self.scaler.transform(features)
        else:
            # Fit and transform
            X_scaled = self.scaler.fit_transform(features)
        
        # Extract labels if available
        labels = None
        if 'is_anomaly' in df.columns:
            labels = df['is_anomaly'].values
        elif 'risk_score' in df.columns:
            # Convert risk scores to binary labels
            labels = (df['risk_score'] > 0.5).astype(int).values
        
        return X_scaled, labels
    
    def _parse_event_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse JSON event data into separate columns.
        
        Args:
            df: DataFrame with event_data column
            
        Returns:
            DataFrame with parsed event data
        """
        if 'event_data' not in df.columns:
            return df
        
        parsed_data = []
        for idx, row in df.iterrows():
            try:
                event_data = json.loads(row['event_data']) if isinstance(row['event_data'], str) else row['event_data']
                parsed_row = row.to_dict()
                
                # Add parsed fields
                for key, value in event_data.items():
                    if key not in parsed_row:
                        parsed_row[f"event_{key}"] = value
                
                parsed_data.append(parsed_row)
            
            except (json.JSONDecodeError, TypeError):
                parsed_data.append(row.to_dict())
        
        return pd.DataFrame(parsed_data)
    
    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from the parsed data.
        
        Args:
            df: Parsed data DataFrame
            
        Returns:
            Feature DataFrame
        """
        features = pd.DataFrame()
        
        # Time-based features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            features['hour'] = df['timestamp'].dt.hour
            features['day_of_week'] = df['timestamp'].dt.dayofweek
            features['is_weekend'] = (df['timestamp'].dt.dayofweek >= 5).astype(int)
            features['is_off_hours'] = ((df['timestamp'].dt.hour < 7) | 
                                      (df['timestamp'].dt.hour > 19)).astype(int)
        
        # User-based features
        if 'user_id' in df.columns:
            user_encoded = self._encode_categorical(df['user_id'], 'user_id')
            features['user_encoded'] = user_encoded
        
        # Event type features
        if 'event_type' in df.columns:
            event_type_encoded = self._encode_categorical(df['event_type'], 'event_type')
            features['event_type_encoded'] = event_type_encoded
        
        # Risk score
        if 'risk_score' in df.columns:
            features['risk_score'] = df['risk_score'].fillna(0.0)
        
        # Application-specific features
        if 'event_application_name' in df.columns:
            app_encoded = self._encode_categorical(df['event_application_name'], 'application_name')
            features['application_encoded'] = app_encoded
        
        # File-specific features
        if 'event_file_extension' in df.columns:
            ext_encoded = self._encode_categorical(df['event_file_extension'], 'file_extension')
            features['file_extension_encoded'] = ext_encoded
        
        if 'event_file_size' in df.columns:
            features['file_size_log'] = np.log1p(pd.to_numeric(df['event_file_size'], errors='coerce').fillna(0))
        
        # Command-specific features
        if 'event_command' in df.columns:
            features['command_length'] = df['event_command'].astype(str).str.len()
            features['has_high_risk_command'] = df['event_command'].astype(str).str.contains(
                'rm|del|format|wget|curl|ssh|scp', case=False, na=False
            ).astype(int)
        
        # Network-specific features
        if 'source_ip' in df.columns:
            features['is_local_ip'] = df['source_ip'].str.contains(
                '^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|127\.)', na=False
            ).astype(int)
        
        # Store feature columns for later use
        self.feature_columns = features.columns.tolist()
        
        return features
    
    def _encode_categorical(self, series: pd.Series, column_name: str) -> np.ndarray:
        """
        Encode categorical variables.
        
        Args:
            series: Pandas series with categorical data
            column_name: Name of the column for encoder naming
            
        Returns:
            Encoded array
        """
        # Create encoder for this column if it doesn't exist
        encoder_name = f"{column_name}_encoder"
        
        if not hasattr(self, encoder_name):
            encoder = LabelEncoder()
            setattr(self, encoder_name, encoder)
        else:
            encoder = getattr(self, encoder_name)
        
        # Handle unknown values
        series_clean = series.fillna('unknown').astype(str)
        
        try:
            if hasattr(encoder, 'classes_'):
                # Encoder is already fitted
                # Handle unseen labels
                mask = series_clean.isin(encoder.classes_)
                result = np.zeros(len(series_clean), dtype=int)
                result[mask] = encoder.transform(series_clean[mask])
                # Assign unknown class for unseen labels
                result[~mask] = len(encoder.classes_)  # Use max+1 for unknown
                return result
            else:
                # Fit and transform
                return encoder.fit_transform(series_clean)
        
        except Exception as e:
            self.logger.warning(f"Error encoding {column_name}: {str(e)}")
            return np.zeros(len(series_clean), dtype=int)
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in features.
        
        Args:
            df: Feature DataFrame
            
        Returns:
            DataFrame with missing values handled
        """
        # Fill numeric columns with median
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        
        # Fill categorical columns with mode
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns
        for col in categorical_columns:
            df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 0)
        
        return df
    
    def save_model(self, suffix: str = None) -> str:
        """
        Save the trained model to disk.
        
        Args:
            suffix: Optional suffix for the model filename
            
        Returns:
            Path to the saved model file
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = self.get_model_name().lower().replace(' ', '_')
        
        if suffix:
            filename = f"{model_name}_{suffix}_{timestamp}.joblib"
        else:
            filename = f"{model_name}_{timestamp}.joblib"
        
        filepath = os.path.join(self.model_path, filename)
        
        # Save model and associated objects
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'config': self.config,
            'is_trained': self.is_trained
        }
        
        # Save categorical encoders
        for attr_name in dir(self):
            if attr_name.endswith('_encoder'):
                encoder = getattr(self, attr_name)
                model_data[attr_name] = encoder
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"Model saved to {filepath}")
        
        return filepath
    
    def load_model(self, filepath: str) -> bool:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to the model file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data.get('is_trained', True)
            
            # Load categorical encoders
            for key, value in model_data.items():
                if key.endswith('_encoder'):
                    setattr(self, key, value)
            
            self.logger.info(f"Model loaded from {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading model from {filepath}: {str(e)}")
            return False
    
    def evaluate_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate the model performance.
        
        Args:
            X: Test features
            y: True labels
            
        Returns:
            Evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        predictions = self.predict(X)
        
        # Handle different prediction formats
        if len(predictions.shape) > 1:
            # For anomaly detection, predictions might be anomaly scores
            y_pred = (predictions > 0.5).astype(int)
        else:
            y_pred = predictions
        
        # Calculate metrics
        try:
            report = classification_report(y, y_pred, output_dict=True)
            cm = confusion_matrix(y, y_pred)
            
            metrics = {
                'accuracy': report['accuracy'],
                'precision': report['macro avg']['precision'],
                'recall': report['macro avg']['recall'],
                'f1_score': report['macro avg']['f1-score'],
                'confusion_matrix': cm.tolist(),
                'classification_report': report
            }
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            return {'error': str(e)}
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance if available.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            return {}
        
        importance_dict = {}
        
        # Try to get feature importance from the model
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            for i, col in enumerate(self.feature_columns):
                importance_dict[col] = float(importances[i])
        
        elif hasattr(self.model, 'coef_'):
            # For linear models
            coef = np.abs(self.model.coef_)
            if len(coef.shape) > 1:
                coef = coef[0]  # Take first class for binary classification
            
            for i, col in enumerate(self.feature_columns):
                importance_dict[col] = float(coef[i])
        
        return importance_dict