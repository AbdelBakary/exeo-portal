"""
Celery tasks for analytics and ML operations.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .ml_models import risk_scoring_model, threat_classification_model, anomaly_detection_model
from .models import RiskScore, Metric
from apps.alerts.models import Alert
from apps.threat_intelligence.models import ThreatIndicator

logger = logging.getLogger(__name__)


@shared_task
def calculate_risk_scores():
    """
    Calculate risk scores for all unprocessed alerts.
    """
    try:
        # Get alerts without risk scores or with old scores
        alerts = Alert.objects.filter(
            risk_score=0.0
        ).select_related('client')[:100]  # Process in batches
        
        if not alerts:
            logger.info("No alerts to process for risk scoring")
            return
        
        # Prepare data for ML model
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'severity': alert.severity,
                'alert_type': alert.alert_type,
                'source_ip': alert.source_ip,
                'destination_ip': alert.destination_ip,
                'source_port': alert.source_port,
                'destination_port': alert.destination_port,
                'description': alert.description,
                'tags': alert.tags,
                'raw_data': alert.raw_data,
                'detected_at': alert.detected_at,
                'client_id': alert.client_id
            })
        
        # Get predictions
        risk_scores = risk_scoring_model.predict(alerts_data)
        
        # Update alerts with new risk scores
        for alert, score in zip(alerts, risk_scores):
            alert.risk_score = score
            alert.risk_factors = {
                'ml_model': 'gradient_boosting_v1',
                'calculated_at': timezone.now().isoformat(),
                'confidence': 0.8  # Default confidence
            }
            alert.save()
            
            # Create risk score record
            RiskScore.objects.create(
                client=alert.client,
                score_type='alert',
                entity_id=str(alert.id),
                entity_type='Alert',
                score=score,
                confidence=0.8,
                factors=alert.risk_factors,
                methodology='ml_model_v1'
            )
        
        logger.info(f"Calculated risk scores for {len(alerts)} alerts")
        return f"Processed {len(alerts)} alerts"
        
    except Exception as e:
        logger.error(f"Error calculating risk scores: {str(e)}")
        raise


@shared_task
def classify_threat_indicators():
    """
    Classify threat indicators using ML model.
    """
    try:
        # Get unclassified threat indicators
        indicators = ThreatIndicator.objects.filter(
            threat_type__isnull=True
        ).select_related('source')[:100]  # Process in batches
        
        if not indicators:
            logger.info("No threat indicators to classify")
            return
        
        # Prepare data for ML model
        indicators_data = []
        for indicator in indicators:
            indicators_data.append({
                'description': indicator.description,
                'threat_type': indicator.threat_type,
                'malware_family': indicator.malware_family,
                'actor': indicator.actor,
                'confidence': indicator.confidence,
                'severity_score': indicator.severity_score
            })
        
        # Get predictions
        threat_types = threat_classification_model.predict(indicators_data)
        
        # Update indicators with classifications
        for indicator, threat_type in zip(indicators, threat_types):
            indicator.threat_type = threat_type
            indicator.save()
        
        logger.info(f"Classified {len(indicators)} threat indicators")
        return f"Classified {len(indicators)} indicators"
        
    except Exception as e:
        logger.error(f"Error classifying threat indicators: {str(e)}")
        raise


@shared_task
def detect_anomalies():
    """
    Detect anomalous behavior in security events.
    """
    try:
        # Get recent alerts for anomaly detection
        recent_time = timezone.now() - timedelta(hours=24)
        alerts = Alert.objects.filter(
            detected_at__gte=recent_time
        ).select_related('client')[:1000]  # Process recent alerts
        
        if not alerts:
            logger.info("No recent alerts for anomaly detection")
            return
        
        # Prepare data for ML model
        events_data = []
        for alert in alerts:
            events_data.append({
                'client_id': alert.client_id,
                'source_ip': alert.source_ip,
                'destination_port': alert.destination_port,
                'protocol': alert.protocol,
                'raw_data': alert.raw_data,
                'detected_at': alert.detected_at
            })
        
        # Get anomaly predictions
        anomalies = anomaly_detection_model.predict(events_data)
        
        # Process results
        anomaly_count = 0
        for alert, anomaly_result in zip(alerts, anomalies):
            if anomaly_result['is_anomaly']:
                anomaly_count += 1
                # Update alert with anomaly information
                if not alert.tags:
                    alert.tags = []
                if 'anomaly' not in alert.tags:
                    alert.tags.append('anomaly')
                alert.risk_score = max(alert.risk_score, 7.0)  # Boost risk score for anomalies
                alert.save()
        
        logger.info(f"Detected {anomaly_count} anomalies in {len(alerts)} alerts")
        return f"Detected {anomaly_count} anomalies"
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise


@shared_task
def calculate_metrics():
    """
    Calculate various metrics for dashboards and reporting.
    """
    try:
        from apps.accounts.models import Client
        
        # Calculate metrics for each client
        for client in Client.objects.filter(is_active=True):
            # Alert metrics
            total_alerts = Alert.objects.filter(client=client).count()
            open_alerts = Alert.objects.filter(client=client, status='open').count()
            high_severity_alerts = Alert.objects.filter(
                client=client, severity__in=['high', 'critical']
            ).count()
            
            # Risk score metrics
            avg_risk_score = Alert.objects.filter(client=client).aggregate(
                avg_score=models.Avg('risk_score')
            )['avg_score'] or 0
            
            # Time-based metrics
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            
            alerts_24h = Alert.objects.filter(
                client=client, detected_at__gte=last_24h
            ).count()
            
            alerts_7d = Alert.objects.filter(
                client=client, detected_at__gte=last_7d
            ).count()
            
            # Create or update metrics
            metrics_data = [
                ('total_alerts', total_alerts, 'count'),
                ('open_alerts', open_alerts, 'count'),
                ('high_severity_alerts', high_severity_alerts, 'count'),
                ('avg_risk_score', avg_risk_score, 'average'),
                ('alerts_24h', alerts_24h, 'count'),
                ('alerts_7d', alerts_7d, 'count'),
            ]
            
            for name, value, metric_type in metrics_data:
                Metric.objects.update_or_create(
                    client=client,
                    name=name,
                    period_start=now.replace(hour=0, minute=0, second=0, microsecond=0),
                    period_end=now,
                    defaults={
                        'metric_type': metric_type,
                        'value': value,
                        'unit': 'count' if metric_type == 'count' else 'score',
                        'calculation_method': 'direct'
                    }
                )
        
        logger.info("Calculated metrics for all clients")
        return "Metrics calculated successfully"
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise


@shared_task
def train_ml_models():
    """
    Train all ML models with recent data.
    """
    try:
        # Get training data
        recent_time = timezone.now() - timedelta(days=30)
        
        # Prepare risk scoring training data
        alerts = Alert.objects.filter(
            detected_at__gte=recent_time,
            risk_score__gt=0
        ).select_related('client')
        
        if alerts.count() > 100:  # Need minimum data for training
            alerts_data = []
            risk_scores = []
            
            for alert in alerts:
                alerts_data.append({
                    'severity': alert.severity,
                    'alert_type': alert.alert_type,
                    'source_ip': alert.source_ip,
                    'destination_ip': alert.destination_ip,
                    'source_port': alert.source_port,
                    'destination_port': alert.destination_port,
                    'description': alert.description,
                    'tags': alert.tags,
                    'raw_data': alert.raw_data,
                    'detected_at': alert.detected_at,
                    'client_id': alert.client_id
                })
                risk_scores.append(alert.risk_score)
            
            # Train risk scoring model
            risk_metrics = risk_scoring_model.train(alerts_data, risk_scores)
            logger.info(f"Risk scoring model trained: {risk_metrics}")
        
        # Prepare threat classification training data
        indicators = ThreatIndicator.objects.filter(
            first_seen__gte=recent_time,
            threat_type__isnull=False
        ).select_related('source')
        
        if indicators.count() > 50:  # Need minimum data for training
            indicators_data = []
            threat_types = []
            
            for indicator in indicators:
                indicators_data.append({
                    'description': indicator.description,
                    'threat_type': indicator.threat_type,
                    'malware_family': indicator.malware_family,
                    'actor': indicator.actor,
                    'confidence': indicator.confidence,
                    'severity_score': indicator.severity_score
                })
                threat_types.append(indicator.threat_type)
            
            # Train threat classification model
            threat_metrics = threat_classification_model.train(indicators_data, threat_types)
            logger.info(f"Threat classification model trained: {threat_metrics}")
        
        # Prepare anomaly detection training data
        events_data = []
        for alert in alerts:
            events_data.append({
                'client_id': alert.client_id,
                'source_ip': alert.source_ip,
                'destination_port': alert.destination_port,
                'protocol': alert.protocol,
                'raw_data': alert.raw_data,
                'detected_at': alert.detected_at
            })
        
        if len(events_data) > 100:  # Need minimum data for training
            # Train anomaly detection model
            anomaly_metrics = anomaly_detection_model.train(events_data)
            logger.info(f"Anomaly detection model trained: {anomaly_metrics}")
        
        logger.info("All ML models training completed")
        return "ML models trained successfully"
        
    except Exception as e:
        logger.error(f"Error training ML models: {str(e)}")
        raise
