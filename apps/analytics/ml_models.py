"""
Machine Learning models for risk scoring and threat analysis.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from django.conf import settings
import joblib
import os
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class RiskScoringModel:
    """
    Machine Learning model for calculating risk scores for security alerts.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'risk_scoring_model.pkl')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'risk_scaler.pkl')
        self.encoders_path = os.path.join(settings.BASE_DIR, 'ml_models', 'risk_encoders.pkl')
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def prepare_features(self, alerts_data: List[Dict]) -> np.ndarray:
        """
        Prepare features for the risk scoring model.
        
        Args:
            alerts_data: List of alert dictionaries
            
        Returns:
            numpy array of features
        """
        df = pd.DataFrame(alerts_data)
        
        # Define feature columns
        feature_columns = [
            'severity_numeric', 'alert_type_numeric', 'source_port',
            'destination_port', 'has_source_ip', 'has_destination_ip',
            'description_length', 'tag_count', 'raw_data_size',
            'time_since_detection', 'client_alert_frequency'
        ]
        
        # Convert severity to numeric
        severity_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        df['severity_numeric'] = df['severity'].map(severity_mapping).fillna(0)
        
        # Convert alert type to numeric
        if 'alert_type' in df.columns:
            if 'alert_type' not in self.label_encoders:
                self.label_encoders['alert_type'] = LabelEncoder()
                df['alert_type_numeric'] = self.label_encoders['alert_type'].fit_transform(df['alert_type'].fillna('unknown'))
            else:
                df['alert_type_numeric'] = self.label_encoders['alert_type'].transform(df['alert_type'].fillna('unknown'))
        else:
            df['alert_type_numeric'] = 0
        
        # Network features
        df['has_source_ip'] = df['source_ip'].notna().astype(int)
        df['has_destination_ip'] = df['destination_ip'].notna().astype(int)
        df['source_port'] = pd.to_numeric(df['source_port'], errors='coerce').fillna(0)
        df['destination_port'] = pd.to_numeric(df['destination_port'], errors='coerce').fillna(0)
        
        # Text features
        df['description_length'] = df['description'].str.len().fillna(0)
        df['tag_count'] = df['tags'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df['raw_data_size'] = df['raw_data'].apply(lambda x: len(str(x)) if x else 0)
        
        # Time features
        if 'detected_at' in df.columns:
            df['detected_at'] = pd.to_datetime(df['detected_at'])
            df['time_since_detection'] = (pd.Timestamp.now() - df['detected_at']).dt.total_seconds() / 3600  # hours
        else:
            df['time_since_detection'] = 0
        
        # Client frequency (simplified)
        df['client_alert_frequency'] = df.groupby('client_id')['client_id'].transform('count')
        
        # Select and fill missing values
        features = df[feature_columns].fillna(0)
        
        return features.values
    
    def train(self, alerts_data: List[Dict], risk_scores: List[float]) -> Dict[str, float]:
        """
        Train the risk scoring model.
        
        Args:
            alerts_data: List of alert dictionaries
            risk_scores: List of corresponding risk scores
            
        Returns:
            Dictionary with training metrics
        """
        try:
            # Prepare features
            X = self.prepare_features(alerts_data)
            y = np.array(risk_scores)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = self.model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model and preprocessors
            self.save_model()
            
            metrics = {
                'mse': mse,
                'r2_score': r2,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            logger.info(f"Risk scoring model trained successfully. R²: {r2:.3f}, MSE: {mse:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training risk scoring model: {str(e)}")
            raise
    
    def predict(self, alerts_data: List[Dict]) -> List[float]:
        """
        Predict risk scores for alerts.
        
        Args:
            alerts_data: List of alert dictionaries
            
        Returns:
            List of predicted risk scores
        """
        try:
            if self.model is None:
                self.load_model()
            
            if self.model is None:
                # Return default scores if model not available
                return [5.0] * len(alerts_data)
            
            # Prepare features
            X = self.prepare_features(alerts_data)
            X_scaled = self.scaler.transform(X)
            
            # Make predictions
            predictions = self.model.predict(X_scaled)
            
            # Ensure scores are between 0 and 10
            predictions = np.clip(predictions, 0, 10)
            
            return predictions.tolist()
            
        except Exception as e:
            logger.error(f"Error predicting risk scores: {str(e)}")
            # Return default scores on error
            return [5.0] * len(alerts_data)
    
    def save_model(self):
        """Save the trained model and preprocessors."""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.label_encoders, self.encoders_path)
            logger.info("Risk scoring model saved successfully")
        except Exception as e:
            logger.error(f"Error saving risk scoring model: {str(e)}")
    
    def load_model(self):
        """Load the trained model and preprocessors."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
            if os.path.exists(self.encoders_path):
                self.label_encoders = joblib.load(self.encoders_path)
            logger.info("Risk scoring model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading risk scoring model: {str(e)}")


class ThreatClassificationModel:
    """
    Machine Learning model for classifying threat types and severity.
    """
    
    def __init__(self):
        self.model = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.label_encoder = LabelEncoder()
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'threat_classification_model.pkl')
        self.vectorizer_path = os.path.join(settings.BASE_DIR, 'ml_models', 'threat_vectorizer.pkl')
        self.encoder_path = os.path.join(settings.BASE_DIR, 'ml_models', 'threat_encoder.pkl')
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def prepare_features(self, threat_data: List[Dict]) -> np.ndarray:
        """
        Prepare features for threat classification.
        
        Args:
            threat_data: List of threat indicator dictionaries
            
        Returns:
            numpy array of features
        """
        df = pd.DataFrame(threat_data)
        
        # Combine text features
        text_features = []
        for _, row in df.iterrows():
            text_parts = []
            if 'description' in row and pd.notna(row['description']):
                text_parts.append(str(row['description']))
            if 'threat_type' in row and pd.notna(row['threat_type']):
                text_parts.append(str(row['threat_type']))
            if 'malware_family' in row and pd.notna(row['malware_family']):
                text_parts.append(str(row['malware_family']))
            if 'actor' in row and pd.notna(row['actor']):
                text_parts.append(str(row['actor']))
            
            text_features.append(' '.join(text_parts))
        
        # Vectorize text
        X_text = self.vectorizer.fit_transform(text_features)
        
        # Add numeric features
        numeric_features = []
        if 'confidence' in df.columns:
            confidence_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            numeric_features.append(df['confidence'].map(confidence_mapping).fillna(0).values)
        
        if 'severity_score' in df.columns:
            numeric_features.append(df['severity_score'].fillna(0).values)
        
        # Combine features
        if numeric_features:
            X_numeric = np.column_stack(numeric_features)
            X = np.hstack([X_text.toarray(), X_numeric])
        else:
            X = X_text.toarray()
        
        return X
    
    def train(self, threat_data: List[Dict], threat_types: List[str]) -> Dict[str, float]:
        """
        Train the threat classification model.
        
        Args:
            threat_data: List of threat indicator dictionaries
            threat_types: List of corresponding threat types
            
        Returns:
            Dictionary with training metrics
        """
        try:
            # Prepare features
            X = self.prepare_features(threat_data)
            y = self.label_encoder.fit_transform(threat_types)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model and preprocessors
            self.save_model()
            
            metrics = {
                'accuracy': accuracy,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            logger.info(f"Threat classification model trained successfully. Accuracy: {accuracy:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training threat classification model: {str(e)}")
            raise
    
    def predict(self, threat_data: List[Dict]) -> List[str]:
        """
        Predict threat types for indicators.
        
        Args:
            threat_data: List of threat indicator dictionaries
            
        Returns:
            List of predicted threat types
        """
        try:
            if self.model is None:
                self.load_model()
            
            if self.model is None:
                # Return default predictions if model not available
                return ['unknown'] * len(threat_data)
            
            # Prepare features
            X = self.prepare_features(threat_data)
            
            # Make predictions
            predictions = self.model.predict(X)
            
            # Convert back to labels
            threat_types = self.label_encoder.inverse_transform(predictions)
            
            return threat_types.tolist()
            
        except Exception as e:
            logger.error(f"Error predicting threat types: {str(e)}")
            # Return default predictions on error
            return ['unknown'] * len(threat_data)
    
    def save_model(self):
        """Save the trained model and preprocessors."""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)
            joblib.dump(self.label_encoder, self.encoder_path)
            logger.info("Threat classification model saved successfully")
        except Exception as e:
            logger.error(f"Error saving threat classification model: {str(e)}")
    
    def load_model(self):
        """Load the trained model and preprocessors."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            if os.path.exists(self.vectorizer_path):
                self.vectorizer = joblib.load(self.vectorizer_path)
            if os.path.exists(self.encoder_path):
                self.label_encoder = joblib.load(self.encoder_path)
            logger.info("Threat classification model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading threat classification model: {str(e)}")


class AnomalyDetectionModel:
    """
    Machine Learning model for detecting anomalous behavior in security events.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'anomaly_detection_model.pkl')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'anomaly_scaler.pkl')
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def prepare_features(self, events_data: List[Dict]) -> np.ndarray:
        """
        Prepare features for anomaly detection.
        
        Args:
            events_data: List of event dictionaries
            
        Returns:
            numpy array of features
        """
        df = pd.DataFrame(events_data)
        
        # Define feature columns
        feature_columns = [
            'event_frequency', 'unique_ips', 'unique_ports', 'data_volume',
            'time_variance', 'geographic_spread', 'protocol_diversity'
        ]
        
        # Calculate features
        df['event_frequency'] = df.groupby('client_id')['client_id'].transform('count')
        df['unique_ips'] = df.groupby('client_id')['source_ip'].transform('nunique')
        df['unique_ports'] = df.groupby('client_id')['destination_port'].transform('nunique')
        df['data_volume'] = df['raw_data'].apply(lambda x: len(str(x)) if x else 0)
        
        # Time-based features
        if 'detected_at' in df.columns:
            df['detected_at'] = pd.to_datetime(df['detected_at'])
            df['time_variance'] = df.groupby('client_id')['detected_at'].transform('std').dt.total_seconds()
        else:
            df['time_variance'] = 0
        
        # Geographic spread (simplified)
        df['geographic_spread'] = df.groupby('client_id')['source_ip'].transform('nunique')
        
        # Protocol diversity
        df['protocol_diversity'] = df.groupby('client_id')['protocol'].transform('nunique')
        
        # Select and fill missing values
        features = df[feature_columns].fillna(0)
        
        return features.values
    
    def train(self, events_data: List[Dict]) -> Dict[str, float]:
        """
        Train the anomaly detection model.
        
        Args:
            events_data: List of event dictionaries
            
        Returns:
            Dictionary with training metrics
        """
        try:
            # Prepare features
            X = self.prepare_features(events_data)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model (using Isolation Forest for anomaly detection)
            from sklearn.ensemble import IsolationForest
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            self.model.fit(X_scaled)
            
            # Calculate anomaly scores
            scores = self.model.decision_function(X_scaled)
            anomalies = self.model.predict(X_scaled)
            
            # Save model and preprocessors
            self.save_model()
            
            metrics = {
                'anomaly_rate': (anomalies == -1).mean(),
                'avg_anomaly_score': scores.mean(),
                'training_samples': len(X_scaled)
            }
            
            logger.info(f"Anomaly detection model trained successfully. Anomaly rate: {metrics['anomaly_rate']:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training anomaly detection model: {str(e)}")
            raise
    
    def predict(self, events_data: List[Dict]) -> List[Dict]:
        """
        Predict anomalies in events.
        
        Args:
            events_data: List of event dictionaries
            
        Returns:
            List of anomaly predictions with scores
        """
        try:
            if self.model is None:
                self.load_model()
            
            if self.model is None:
                # Return default predictions if model not available
                return [{'is_anomaly': False, 'anomaly_score': 0.0}] * len(events_data)
            
            # Prepare features
            X = self.prepare_features(events_data)
            X_scaled = self.scaler.transform(X)
            
            # Make predictions
            predictions = self.model.predict(X_scaled)
            scores = self.model.decision_function(X_scaled)
            
            # Format results
            results = []
            for pred, score in zip(predictions, scores):
                results.append({
                    'is_anomaly': pred == -1,
                    'anomaly_score': float(score)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error predicting anomalies: {str(e)}")
            # Return default predictions on error
            return [{'is_anomaly': False, 'anomaly_score': 0.0}] * len(events_data)
    
    def save_model(self):
        """Save the trained model and preprocessors."""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Anomaly detection model saved successfully")
        except Exception as e:
            logger.error(f"Error saving anomaly detection model: {str(e)}")
    
    def load_model(self):
        """Load the trained model and preprocessors."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
            logger.info("Anomaly detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading anomaly detection model: {str(e)}")


# Global model instances
risk_scoring_model = RiskScoringModel()
threat_classification_model = ThreatClassificationModel()
anomaly_detection_model = AnomalyDetectionModel()
