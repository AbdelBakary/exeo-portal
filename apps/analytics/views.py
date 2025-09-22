"""
API views for analytics and risk scoring.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Max, Min
from django.db import models

from .models import RiskScore, Metric, DashboardWidget
from .services import RiskScoringService, ThreatIntelligenceService
from .serializers import RiskScoreSerializer, MetricSerializer, DashboardWidgetSerializer
from apps.alerts.models import Alert
from apps.accounts.permissions import CanAccessClientData


class RiskScoreListView(generics.ListAPIView):
    """List risk scores for the authenticated user's client."""
    
    serializer_class = RiskScoreSerializer
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_queryset(self):
        queryset = RiskScore.objects.all()
        
        # Filter by client if user is a client
        if self.request.user.role == 'client' and self.request.user.client:
            queryset = queryset.filter(client=self.request.user.client)
        
        return queryset.order_by('-calculated_at')


class MetricListView(generics.ListAPIView):
    """List metrics for the authenticated user's client."""
    
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_queryset(self):
        queryset = Metric.objects.all()
        
        # Filter by client if user is a client
        if self.request.user.role == 'client' and self.request.user.client:
            queryset = queryset.filter(client=self.request.user.client)
        
        return queryset.order_by('-calculated_at')


class DashboardWidgetListView(generics.ListAPIView):
    """List dashboard widgets for the authenticated user's client."""
    
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_queryset(self):
        queryset = DashboardWidget.objects.filter(is_visible=True)
        
        # Filter by client if user is a client
        if self.request.user.role == 'client' and self.request.user.client:
            queryset = queryset.filter(client=self.request.user.client)
        
        return queryset.order_by('position_y', 'position_x')


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def calculate_risk_scores(request):
    """
    Manually trigger risk score calculation for alerts.
    """
    try:
        scoring_service = RiskScoringService()
        
        # Get alerts without scores or with old scores
        alerts = Alert.objects.filter(risk_score=0.0)
        
        # Filter by client if user is a client
        if request.user.role == 'client' and request.user.client:
            alerts = alerts.filter(client=request.user.client)
        
        # Limit to 100 alerts per request
        alerts = alerts[:100]
        
        if not alerts:
            return Response({
                'message': 'No alerts found for risk score calculation',
                'processed': 0
            })
        
        processed_count = 0
        errors = []
        
        for alert in alerts:
            try:
                score, factors = scoring_service.calculate_alert_risk_score(alert)
                
                # Update alert
                alert.risk_score = score
                alert.risk_factors = factors
                alert.save(update_fields=['risk_score', 'risk_factors'])
                
                # Create risk score record
                RiskScore.objects.create(
                    client=alert.client,
                    score_type='alert',
                    entity_id=str(alert.id),
                    entity_type='Alert',
                    score=score,
                    confidence=factors.get('confidence', 0.8),
                    factors=factors,
                    methodology=factors.get('methodology', 'professional_hybrid_v1'),
                    calculated_by=request.user
                )
                
                processed_count += 1
                
            except Exception as e:
                errors.append(f"Alert {alert.id}: {str(e)}")
                continue
        
        return Response({
            'message': f'Risk scores calculated for {processed_count} alerts',
            'processed': processed_count,
            'errors': errors[:10]  # Limit error messages
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def risk_score_statistics(request):
    """
    Get risk score statistics for dashboard.
    """
    try:
        # Base queryset
        queryset = Alert.objects.all()
        
        # Filter by client if user is a client
        if request.user.role == 'client' and request.user.client:
            queryset = queryset.filter(client=request.user.client)
        
        # Time filters
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Risk score statistics
        risk_stats = queryset.aggregate(
            avg_risk_score=Avg('risk_score'),
            max_risk_score=Max('risk_score'),
            min_risk_score=Min('risk_score'),
            total_alerts=Count('id')
        )
        
        # Risk level distribution
        risk_levels = {
            'critical': queryset.filter(risk_score__gte=8.0).count(),
            'high': queryset.filter(risk_score__gte=6.0, risk_score__lt=8.0).count(),
            'medium': queryset.filter(risk_score__gte=4.0, risk_score__lt=6.0).count(),
            'low': queryset.filter(risk_score__gte=2.0, risk_score__lt=4.0).count(),
            'minimal': queryset.filter(risk_score__lt=2.0).count()
        }
        
        # Time-based risk statistics
        risk_24h = queryset.filter(detected_at__gte=last_24h).aggregate(
            avg_score=Avg('risk_score'),
            max_score=Max('risk_score'),
            count=Count('id')
        )
        
        risk_7d = queryset.filter(detected_at__gte=last_7d).aggregate(
            avg_score=Avg('risk_score'),
            max_score=Max('risk_score'),
            count=Count('id')
        )
        
        # Top risk factors
        high_risk_alerts = queryset.filter(risk_score__gte=7.0)
        risk_factors = {}
        
        for alert in high_risk_alerts[:50]:  # Sample for performance
            if alert.risk_factors and 'components' in alert.risk_factors:
                for component, data in alert.risk_factors['components'].items():
                    if component not in risk_factors:
                        risk_factors[component] = 0
                    risk_factors[component] += 1
        
        # Sort risk factors by frequency
        top_risk_factors = sorted(risk_factors.items(), key=lambda x: x[1], reverse=True)[:10]
        
        statistics = {
            'overall': {
                'avg_risk_score': round(risk_stats['avg_risk_score'] or 0, 2),
                'max_risk_score': round(risk_stats['max_risk_score'] or 0, 2),
                'min_risk_score': round(risk_stats['min_risk_score'] or 0, 2),
                'total_alerts': risk_stats['total_alerts']
            },
            'risk_levels': risk_levels,
            'time_based': {
                'last_24h': {
                    'avg_score': round(risk_24h['avg_score'] or 0, 2),
                    'max_score': round(risk_24h['max_score'] or 0, 2),
                    'count': risk_24h['count']
                },
                'last_7d': {
                    'avg_score': round(risk_7d['avg_score'] or 0, 2),
                    'max_score': round(risk_7d['max_score'] or 0, 2),
                    'count': risk_7d['count']
                }
            },
            'top_risk_factors': top_risk_factors
        }
        
        return Response(statistics)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def risk_score_distribution(request):
    """
    Get risk score distribution for charts.
    """
    try:
        # Base queryset
        queryset = Alert.objects.all()
        
        # Filter by client if user is a client
        if request.user.role == 'client' and request.user.client:
            queryset = queryset.filter(client=request.user.client)
        
        # Get distribution by score ranges
        distribution = {
            '0-2': queryset.filter(risk_score__gte=0, risk_score__lt=2).count(),
            '2-4': queryset.filter(risk_score__gte=2, risk_score__lt=4).count(),
            '4-6': queryset.filter(risk_score__gte=4, risk_score__lt=6).count(),
            '6-8': queryset.filter(risk_score__gte=6, risk_score__lt=8).count(),
            '8-10': queryset.filter(risk_score__gte=8, risk_score__lte=10).count()
        }
        
        # Get distribution by severity
        severity_distribution = {}
        for severity in ['low', 'medium', 'high', 'critical']:
            severity_distribution[severity] = queryset.filter(severity=severity).aggregate(
                avg_score=Avg('risk_score'),
                count=Count('id')
            )
        
        # Get distribution by alert type
        type_distribution = {}
        alert_types = queryset.values('alert_type').annotate(
            count=Count('id'),
            avg_score=Avg('risk_score')
        ).order_by('-count')[:10]
        
        for alert_type in alert_types:
            type_distribution[alert_type['alert_type']] = {
                'count': alert_type['count'],
                'avg_score': round(alert_type['avg_score'] or 0, 2)
            }
        
        return Response({
            'score_ranges': distribution,
            'severity_distribution': severity_distribution,
            'type_distribution': type_distribution
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def train_ml_models(request):
    """
    Train ML models with recent data.
    """
    try:
        from .tasks import train_ml_models as train_task
        
        # Trigger training (synchronous for now)
        result = train_task()
        
        return Response({
            'message': 'ML models training completed',
            'result': result
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def threat_intelligence_enrichment(request, alert_id):
    """
    Enrich alert with threat intelligence data.
    """
    try:
        # Get alert
        alert = Alert.objects.get(id=alert_id)
        
        # Check permissions
        if request.user.role == 'client' and request.user.client != alert.client:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Enrich with threat intelligence
        ti_service = ThreatIntelligenceService()
        ti_data = ti_service.enrich_alert_with_ti(alert)
        
        return Response(ti_data)
        
    except Alert.DoesNotExist:
        return Response({
            'error': 'Alert not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)