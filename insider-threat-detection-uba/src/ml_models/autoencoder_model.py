"""
Autoencoder model for anomaly detection using deep learning.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model, callbacks
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import os

from .base_model import BaseModel


class AutoencoderModel(BaseModel):
    """
    Autoencoder neural network model for detecting anomalies in user behavior.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Autoencoder specific parameters
        self.encoding_dim = config.get('encoding_dim', 32)
        self.hidden_layers = config.get('hidden_layers', [64, 32])
        self.epochs = config.get('epochs', 100)
        self.batch_size = config.get('batch_size', 32)
        self.learning_rate = config.get('learning_rate', 0.001)
        self.validation_split = config.get('validation_split', 0.2)
        self.patience = config.get('patience', 10)
        self.anomaly_threshold = config.get('anomaly_threshold', None)
        self.random_state = config.get('random_state', 42)
        
        # Set random seeds for reproducibility
        tf.random.set_seed(self.random_state)
        np.random.seed(self.random_state)
        
        # Model components
        self.encoder = None
        self.decoder = None
        self.autoencoder = None
        self.history = None
        
        # Threshold for anomaly detection
        self.threshold = None
    
    def get_model_name(self) -> str:
        return "Autoencoder"
    
    def _create_model(self, input_dim: int) -> Model:
        """
        Create and return the Autoencoder model.
        
        Args:
            input_dim: Input dimension size
            
        Returns:
            Keras Model instance
        """
        # Input layer
        input_layer = keras.Input(shape=(input_dim,))
        
        # Encoder layers
        encoded = input_layer
        for i, units in enumerate(self.hidden_layers):
            encoded = layers.Dense(units, activation='relu', 
                                 name=f'encoder_hidden_{i}')(encoded)
            encoded = layers.Dropout(0.2)(encoded)
        
        # Bottleneck layer (encoding)
        encoded = layers.Dense(self.encoding_dim, activation='relu', 
                             name='encoding')(encoded)
        
        # Create encoder model
        self.encoder = Model(input_layer, encoded, name='encoder')
        
        # Decoder layers (reverse of encoder)
        decoded = encoded
        for i, units in enumerate(reversed(self.hidden_layers)):
            decoded = layers.Dense(units, activation='relu', 
                                 name=f'decoder_hidden_{i}')(decoded)
            decoded = layers.Dropout(0.2)(decoded)
        
        # Output layer (reconstruction)
        decoded = layers.Dense(input_dim, activation='linear', 
                             name='reconstruction')(decoded)
        
        # Create decoder model
        decoder_input = keras.Input(shape=(self.encoding_dim,))
        decoder_layers = []
        for layer in self.autoencoder.layers:
            if 'decoder' in layer.name or 'reconstruction' in layer.name:
                decoder_layers.append(layer)
        
        # Create full autoencoder
        self.autoencoder = Model(input_layer, decoded, name='autoencoder')
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.autoencoder.compile(
            optimizer=optimizer,
            loss='mse',
            metrics=['mae']
        )
        
        return self.autoencoder
    
    def train(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Train the Autoencoder model.
        
        Args:
            X: Training features
            y: Not used for unsupervised learning
            
        Returns:
            Training metrics
        """
        if X.size == 0:
            raise ValueError("Training data is empty")
        
        input_dim = X.shape[1]
        self.logger.info(f"Training Autoencoder with {X.shape[0]} samples and {input_dim} features")
        
        try:
            # Create model
            self.model = self._create_model(input_dim)
            
            # Split data for validation
            X_train, X_val = train_test_split(
                X, test_size=self.validation_split, 
                random_state=self.random_state
            )
            
            # Callbacks
            callbacks_list = [
                callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=self.patience,
                    restore_best_weights=True
                ),
                callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-6
                )
            ]
            
            # Train the model
            self.history = self.model.fit(
                X_train, X_train,  # Autoencoder learns to reconstruct input
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_data=(X_val, X_val),
                callbacks=callbacks_list,
                verbose=1
            )
            
            self.is_trained = True
            
            # Calculate anomaly threshold
            self.threshold = self._calculate_threshold(X_train)
            
            # Calculate training metrics
            train_loss = self.model.evaluate(X_train, X_train, verbose=0)[0]
            val_loss = self.model.evaluate(X_val, X_val, verbose=0)[0]
            
            metrics = {
                'n_samples': X.shape[0],
                'n_features': input_dim,
                'encoding_dim': self.encoding_dim,
                'epochs_trained': len(self.history.history['loss']),
                'final_train_loss': float(train_loss),
                'final_val_loss': float(val_loss),
                'anomaly_threshold': float(self.threshold),
                'min_train_loss': float(min(self.history.history['loss'])),
                'min_val_loss': float(min(self.history.history['val_loss']))
            }
            
            self.logger.info(f"Training completed. Final train loss: {train_loss:.4f}, "
                           f"validation loss: {val_loss:.4f}")
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"Error training Autoencoder: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the trained model.
        
        Args:
            X: Features for prediction
            
        Returns:
            Predictions (1 for normal, -1 for anomaly)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        if X.size == 0:
            return np.array([])
        
        try:
            # Get reconstruction errors
            reconstruction_errors = self.get_reconstruction_errors(X)
            
            # Classify based on threshold
            predictions = np.where(reconstruction_errors > self.threshold, -1, 1)
            
            return predictions
        
        except Exception as e:
            self.logger.error(f"Error making predictions: {str(e)}")
            raise
    
    def get_reconstruction_errors(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate reconstruction errors for the input data.
        
        Args:
            X: Input features
            
        Returns:
            Reconstruction errors (MSE between input and reconstruction)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before calculating errors")
        
        try:
            # Get reconstructions
            reconstructions = self.model.predict(X, verbose=0)
            
            # Calculate MSE for each sample
            mse = np.mean(np.power(X - reconstructions, 2), axis=1)
            
            return mse
        
        except Exception as e:
            self.logger.error(f"Error calculating reconstruction errors: {str(e)}")
            raise
    
    def _calculate_threshold(self, X: np.ndarray) -> float:
        """
        Calculate anomaly threshold based on training data.
        
        Args:
            X: Training data
            
        Returns:
            Anomaly threshold
        """
        if self.anomaly_threshold is not None:
            return self.anomaly_threshold
        
        # Calculate reconstruction errors on training data
        reconstruction_errors = self.get_reconstruction_errors(X)
        
        # Use percentile-based threshold (e.g., 95th percentile)
        threshold = np.percentile(reconstruction_errors, 95)
        
        return threshold
    
    def detect_anomalies(self, X: np.ndarray, return_errors: bool = False) -> Dict[str, Any]:
        """
        Detect anomalies and return detailed results.
        
        Args:
            X: Features for anomaly detection
            return_errors: Whether to include reconstruction errors in results
            
        Returns:
            Dictionary containing anomaly detection results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        predictions = self.predict(X)
        errors = self.get_reconstruction_errors(X)
        
        # Identify anomalous indices
        anomaly_indices = np.where(predictions == -1)[0]
        normal_indices = np.where(predictions == 1)[0]
        
        results = {
            'total_samples': len(X),
            'anomaly_count': len(anomaly_indices),
            'normal_count': len(normal_indices),
            'anomaly_ratio': len(anomaly_indices) / len(X),
            'anomaly_indices': anomaly_indices.tolist(),
            'threshold': float(self.threshold),
            'mean_reconstruction_error': float(np.mean(errors)),
            'max_reconstruction_error': float(np.max(errors)),
            'min_reconstruction_error': float(np.min(errors))
        }
        
        if return_errors:
            results['reconstruction_errors'] = errors.tolist()
            results['anomalous_errors'] = errors[anomaly_indices].tolist()
            results['normal_errors'] = errors[normal_indices].tolist()
        
        return results
    
    def get_encoded_representations(self, X: np.ndarray) -> np.ndarray:
        """
        Get encoded (compressed) representations of the input data.
        
        Args:
            X: Input features
            
        Returns:
            Encoded representations
        """
        if not self.is_trained or self.encoder is None:
            raise ValueError("Model must be trained before getting encodings")
        
        try:
            encoded = self.encoder.predict(X, verbose=0)
            return encoded
        
        except Exception as e:
            self.logger.error(f"Error getting encoded representations: {str(e)}")
            raise
    
    def plot_training_history(self, save_path: Optional[str] = None) -> None:
        """
        Plot training history.
        
        Args:
            save_path: Path to save the plot (optional)
        """
        if self.history is None:
            raise ValueError("Model must be trained to plot history")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Plot loss
        ax1.plot(self.history.history['loss'], label='Training Loss')
        ax1.plot(self.history.history['val_loss'], label='Validation Loss')
        ax1.set_title('Model Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Plot MAE
        ax2.plot(self.history.history['mae'], label='Training MAE')
        ax2.plot(self.history.history['val_mae'], label='Validation MAE')
        ax2.set_title('Model MAE')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('MAE')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"Training history plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_reconstruction_errors(self, X: np.ndarray, save_path: Optional[str] = None) -> None:
        """
        Plot distribution of reconstruction errors.
        
        Args:
            X: Input data
            save_path: Path to save the plot (optional)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to plot reconstruction errors")
        
        errors = self.get_reconstruction_errors(X)
        predictions = self.predict(X)
        
        normal_errors = errors[predictions == 1]
        anomaly_errors = errors[predictions == -1]
        
        plt.figure(figsize=(10, 6))
        
        # Plot histograms
        plt.hist(normal_errors, bins=50, alpha=0.7, label='Normal', color='blue')
        plt.hist(anomaly_errors, bins=50, alpha=0.7, label='Anomaly', color='red')
        
        # Plot threshold line
        plt.axvline(x=self.threshold, color='black', linestyle='--', 
                   label=f'Threshold ({self.threshold:.4f})')
        
        plt.xlabel('Reconstruction Error')
        plt.ylabel('Frequency')
        plt.title('Distribution of Reconstruction Errors')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"Reconstruction errors plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def save_model(self, suffix: str = None) -> str:
        """
        Save the trained model to disk.
        
        Args:
            suffix: Optional suffix for the model filename
            
        Returns:
            Path to the saved model directory
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = self.get_model_name().lower().replace(' ', '_')
        
        if suffix:
            dirname = f"{model_name}_{suffix}_{timestamp}"
        else:
            dirname = f"{model_name}_{timestamp}"
        
        model_dir = os.path.join(self.model_path, dirname)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save the Keras model
        model_file = os.path.join(model_dir, 'autoencoder_model')
        self.model.save(model_file)
        
        # Save additional components using joblib
        import joblib
        additional_data = {
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'threshold': self.threshold,
            'config': self.config,
            'is_trained': self.is_trained,
            'history': self.history.history if self.history else None
        }
        
        # Save categorical encoders
        for attr_name in dir(self):
            if attr_name.endswith('_encoder'):
                encoder = getattr(self, attr_name)
                additional_data[attr_name] = encoder
        
        joblib_file = os.path.join(model_dir, 'additional_data.joblib')
        joblib.dump(additional_data, joblib_file)
        
        self.logger.info(f"Model saved to {model_dir}")
        
        return model_dir
    
    def load_model(self, model_dir: str) -> bool:
        """
        Load a trained model from disk.
        
        Args:
            model_dir: Path to the model directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the Keras model
            model_file = os.path.join(model_dir, 'autoencoder_model')
            self.model = keras.models.load_model(model_file)
            
            # Load additional data
            import joblib
            joblib_file = os.path.join(model_dir, 'additional_data.joblib')
            additional_data = joblib.load(joblib_file)
            
            self.scaler = additional_data['scaler']
            self.feature_columns = additional_data['feature_columns']
            self.threshold = additional_data['threshold']
            self.is_trained = additional_data.get('is_trained', True)
            
            # Load history if available
            history_data = additional_data.get('history')
            if history_data:
                # Recreate history object (simplified)
                self.history = type('History', (), {'history': history_data})()
            
            # Load categorical encoders
            for key, value in additional_data.items():
                if key.endswith('_encoder'):
                    setattr(self, key, value)
            
            # Recreate encoder from the full model
            if self.model:
                # Find the encoding layer
                for layer in self.model.layers:
                    if 'encoding' in layer.name:
                        encoding_output = layer.output
                        self.encoder = Model(
                            inputs=self.model.input, 
                            outputs=encoding_output
                        )
                        break
            
            self.logger.info(f"Model loaded from {model_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading model from {model_dir}: {str(e)}")
            return False
    
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
        error = self.get_reconstruction_errors(sample)[0]
        reconstruction = self.model.predict(sample, verbose=0)[0]
        
        explanation = {
            'sample_index': sample_index,
            'prediction': 'Anomaly' if prediction == -1 else 'Normal',
            'reconstruction_error': float(error),
            'threshold': float(self.threshold),
            'is_anomaly': prediction == -1,
            'original_features': X[sample_index].tolist(),
            'reconstructed_features': reconstruction.tolist()
        }
        
        # Calculate per-feature reconstruction errors
        if self.feature_columns and len(self.feature_columns) == len(X[sample_index]):
            feature_errors = {}
            for i, feature_name in enumerate(self.feature_columns):
                original_val = X[sample_index, i]
                reconstructed_val = reconstruction[i]
                feature_error = (original_val - reconstructed_val) ** 2
                feature_errors[feature_name] = {
                    'original': float(original_val),
                    'reconstructed': float(reconstructed_val),
                    'error': float(feature_error)
                }
            
            explanation['feature_errors'] = feature_errors
        
        return explanation