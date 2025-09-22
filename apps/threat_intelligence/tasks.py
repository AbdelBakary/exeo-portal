"""
Celery tasks for threat intelligence operations.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services import threat_intelligence_aggregator
from .models import ThreatSource, ThreatIndicator, ThreatCorrelation
from apps.accounts.models import Client

logger = logging.getLogger(__name__)


@shared_task
def aggregate_threat_intelligence():
    """
    Aggregate threat intelligence from all configured sources.
    """
    try:
        logger.info("Starting threat intelligence aggregation")
        
        # Aggregate indicators from all sources
        results = threat_intelligence_aggregator.aggregate_indicators(days=7)
        
        logger.info(f"Threat intelligence aggregation completed: {results}")
        
        # Update source last sync times
        for source in ThreatSource.objects.filter(is_active=True):
            source.last_sync = timezone.now()
            source.save()
        
        return results
        
    except Exception as e:
        logger.error(f"Error in threat intelligence aggregation: {str(e)}")
        raise


@shared_task
def correlate_threat_indicators():
    """
    Correlate threat indicators with existing alerts.
    """
    try:
        logger.info("Starting threat indicator correlation")
        
        # Correlate for all active clients
        total_correlations = {
            'ip_matches': 0,
            'domain_matches': 0,
            'url_matches': 0,
            'hash_matches': 0,
            'total': 0
        }
        
        for client in Client.objects.filter(is_active=True):
            correlations = threat_intelligence_aggregator.correlate_with_alerts(client)
            
            for key, value in correlations.items():
                total_correlations[key] += value
        
        logger.info(f"Threat indicator correlation completed: {total_correlations}")
        return total_correlations
        
    except Exception as e:
        logger.error(f"Error in threat indicator correlation: {str(e)}")
        raise


@shared_task
def cleanup_old_indicators():
    """
    Clean up old and inactive threat indicators.
    """
    try:
        logger.info("Starting cleanup of old threat indicators")
        
        # Remove indicators older than 90 days that are not active
        cutoff_date = timezone.now() - timedelta(days=90)
        
        old_indicators = ThreatIndicator.objects.filter(
            first_seen__lt=cutoff_date,
            is_active=False
        )
        
        count = old_indicators.count()
        old_indicators.delete()
        
        logger.info(f"Cleaned up {count} old threat indicators")
        return f"Cleaned up {count} indicators"
        
    except Exception as e:
        logger.error(f"Error cleaning up old indicators: {str(e)}")
        raise


@shared_task
def update_indicator_confidence():
    """
    Update confidence scores for threat indicators based on correlation data.
    """
    try:
        logger.info("Starting confidence score update")
        
        # Get indicators with correlations
        indicators = ThreatIndicator.objects.filter(
            correlations__isnull=False
        ).distinct()
        
        updated_count = 0
        
        for indicator in indicators:
            # Calculate new confidence based on correlations
            correlations = ThreatCorrelation.objects.filter(threat_indicator=indicator)
            
            if correlations.exists():
                # Increase confidence based on number of correlations
                correlation_count = correlations.count()
                verified_count = correlations.filter(is_verified=True).count()
                
                # Base confidence from source
                base_confidence = {
                    'low': 0.3,
                    'medium': 0.6,
                    'high': 0.8,
                    'critical': 0.9
                }.get(indicator.confidence, 0.5)
                
                # Boost confidence based on correlations
                correlation_boost = min(correlation_count * 0.1, 0.3)
                verification_boost = min(verified_count * 0.2, 0.4)
                
                new_confidence = min(base_confidence + correlation_boost + verification_boost, 1.0)
                
                # Update confidence
                if new_confidence > base_confidence:
                    indicator.confidence = 'high' if new_confidence > 0.7 else 'medium'
                    indicator.save()
                    updated_count += 1
        
        logger.info(f"Updated confidence for {updated_count} indicators")
        return f"Updated {updated_count} indicators"
        
    except Exception as e:
        logger.error(f"Error updating indicator confidence: {str(e)}")
        raise


@shared_task
def generate_threat_reports():
    """
    Generate automated threat intelligence reports.
    """
    try:
        logger.info("Starting threat report generation")
        
        from .models import ThreatIntelligenceReport
        
        # Get recent indicators and correlations
        recent_time = timezone.now() - timedelta(days=7)
        
        recent_indicators = ThreatIndicator.objects.filter(
            first_seen__gte=recent_time,
            is_active=True
        )
        
        recent_correlations = ThreatCorrelation.objects.filter(
            created_at__gte=recent_time
        )
        
        # Generate report content
        report_content = f"""
# Rapport de Threat Intelligence - {timezone.now().strftime('%Y-%m-%d')}

## Résumé
- {recent_indicators.count()} nouveaux indicateurs de menace
- {recent_correlations.count()} corrélations détectées
- {recent_indicators.filter(confidence='high').count()} indicateurs haute confiance

## Indicateurs par type
"""
        
        # Add indicators by type
        indicator_types = recent_indicators.values('indicator_type').annotate(
            count=models.Count('id')
        )
        
        for item in indicator_types:
            report_content += f"- {item['indicator_type']}: {item['count']}\n"
        
        report_content += f"""
## Corrélations par type
"""
        
        # Add correlations by type
        correlation_types = recent_correlations.values('correlation_type').annotate(
            count=models.Count('id')
        )
        
        for item in correlation_types:
            report_content += f"- {item['correlation_type']}: {item['count']}\n"
        
        # Create report
        report = ThreatIntelligenceReport.objects.create(
            title=f"Rapport Threat Intelligence - {timezone.now().strftime('%Y-%m-%d')}",
            report_type='weekly',
            content=report_content,
            summary=f"Rapport hebdomadaire: {recent_indicators.count()} indicateurs, {recent_correlations.count()} corrélations",
            severity_level='medium',
            created_by_id=1  # System user
        )
        
        # Add related data
        report.threat_indicators.set(recent_indicators[:100])  # Limit to 100
        
        logger.info(f"Generated threat intelligence report: {report.id}")
        return f"Generated report {report.id}"
        
    except Exception as e:
        logger.error(f"Error generating threat reports: {str(e)}")
        raise


@shared_task
def sync_threat_feeds():
    """
    Sync data from configured threat intelligence feeds.
    """
    try:
        logger.info("Starting threat feed synchronization")
        
        from .models import ThreatIntelligenceFeed
        
        synced_feeds = 0
        total_indicators = 0
        
        for feed in ThreatIntelligenceFeed.objects.filter(is_active=True):
            try:
                # This is a simplified implementation
                # In reality, you would implement specific feed parsers
                indicators = threat_intelligence_aggregator.osint_connector.get_indicators()
                
                # Process indicators
                count = threat_intelligence_aggregator._process_osint_indicators(indicators)
                total_indicators += count
                
                # Update feed statistics
                feed.total_indicators += count
                feed.last_success = timezone.now()
                feed.save()
                
                synced_feeds += 1
                
            except Exception as e:
                logger.error(f"Error syncing feed {feed.name}: {str(e)}")
                feed.last_error = str(e)
                feed.save()
                continue
        
        logger.info(f"Synced {synced_feeds} feeds, processed {total_indicators} indicators")
        return f"Synced {synced_feeds} feeds, {total_indicators} indicators"
        
    except Exception as e:
        logger.error(f"Error syncing threat feeds: {str(e)}")
        raise
