"""
Celery tasks for SOAR operations.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .engines import playbook_engine
from .models import Playbook, PlaybookExecution, AutomationRule, SOARLog
from apps.alerts.models import Alert
from apps.incidents.models import Incident

logger = logging.getLogger(__name__)


@shared_task
def execute_playbook(playbook_id: int, trigger_data: dict):
    """
    Execute a playbook with given trigger data.
    
    Args:
        playbook_id: ID of the playbook to execute
        trigger_data: Data that triggered the playbook
    """
    try:
        playbook = Playbook.objects.get(id=playbook_id)
        
        # Check if playbook is enabled
        if not playbook.is_enabled:
            logger.info(f"Playbook {playbook.name} is disabled, skipping execution")
            return
        
        # Execute playbook
        execution = playbook_engine.execute_playbook(playbook, trigger_data)
        
        logger.info(f"Playbook {playbook.name} executed with status: {execution.status}")
        return f"Playbook {playbook.name} executed with status: {execution.status}"
        
    except Playbook.DoesNotExist:
        logger.error(f"Playbook with ID {playbook_id} not found")
        return f"Playbook with ID {playbook_id} not found"
    except Exception as e:
        logger.error(f"Error executing playbook {playbook_id}: {str(e)}")
        raise


@shared_task
def process_automation_rules():
    """
    Process all active automation rules and trigger playbooks as needed.
    """
    try:
        logger.info("Starting automation rules processing")
        
        processed_rules = 0
        triggered_playbooks = 0
        
        for rule in AutomationRule.objects.filter(is_enabled=True):
            try:
                # Check if rule should trigger
                if _should_trigger_rule(rule):
                    # Prepare trigger data
                    trigger_data = {
                        'type': 'automation_rule',
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'timestamp': timezone.now().isoformat()
                    }
                    
                    # Execute playbook with delay if configured
                    if rule.execution_delay > 0:
                        execute_playbook.apply_async(
                            args=[rule.playbook.id, trigger_data],
                            countdown=rule.execution_delay
                        )
                    else:
                        execute_playbook.delay(rule.playbook.id, trigger_data)
                    
                    # Update rule statistics
                    rule.trigger_count += 1
                    rule.last_triggered = timezone.now()
                    rule.save()
                    
                    triggered_playbooks += 1
                
                processed_rules += 1
                
            except Exception as e:
                logger.error(f"Error processing rule {rule.name}: {str(e)}")
                rule.failure_count += 1
                rule.save()
                continue
        
        logger.info(f"Processed {processed_rules} rules, triggered {triggered_playbooks} playbooks")
        return f"Processed {processed_rules} rules, triggered {triggered_playbooks} playbooks"
        
    except Exception as e:
        logger.error(f"Error processing automation rules: {str(e)}")
        raise


@shared_task
def cleanup_old_executions():
    """
    Clean up old playbook executions and logs.
    """
    try:
        logger.info("Starting cleanup of old SOAR executions")
        
        # Remove executions older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_executions = PlaybookExecution.objects.filter(
            started_at__lt=cutoff_date
        )
        
        execution_count = old_executions.count()
        old_executions.delete()
        
        # Remove logs older than 90 days
        log_cutoff_date = timezone.now() - timedelta(days=90)
        
        old_logs = SOARLog.objects.filter(
            created_at__lt=log_cutoff_date
        )
        
        log_count = old_logs.count()
        old_logs.delete()
        
        logger.info(f"Cleaned up {execution_count} executions and {log_count} logs")
        return f"Cleaned up {execution_count} executions and {log_count} logs"
        
    except Exception as e:
        logger.error(f"Error cleaning up old executions: {str(e)}")
        raise


@shared_task
def monitor_playbook_health():
    """
    Monitor playbook execution health and alert on issues.
    """
    try:
        logger.info("Starting playbook health monitoring")
        
        # Check for stuck executions (running for more than 1 hour)
        stuck_cutoff = timezone.now() - timedelta(hours=1)
        
        stuck_executions = PlaybookExecution.objects.filter(
            status='running',
            started_at__lt=stuck_cutoff
        )
        
        for execution in stuck_executions:
            # Mark as timeout
            execution.status = 'timeout'
            execution.completed_at = timezone.now()
            execution.error_message = 'Execution timed out'
            execution.save()
            
            # Log the timeout
            SOARLog.objects.create(
                level='warning',
                message=f'Playbook execution {execution.id} timed out',
                component='monitor',
                execution=execution,
                client=execution.playbook.client
            )
        
        # Check for high failure rates
        recent_time = timezone.now() - timedelta(hours=24)
        
        for playbook in Playbook.objects.filter(is_enabled=True):
            recent_executions = PlaybookExecution.objects.filter(
                playbook=playbook,
                started_at__gte=recent_time
            )
            
            if recent_executions.count() >= 5:  # Only check if there are enough executions
                failed_count = recent_executions.filter(status='failed').count()
                failure_rate = failed_count / recent_executions.count()
                
                if failure_rate > 0.5:  # More than 50% failure rate
                    SOARLog.objects.create(
                        level='error',
                        message=f'High failure rate detected for playbook {playbook.name}: {failure_rate:.2%}',
                        component='monitor',
                        client=playbook.client
                    )
        
        logger.info("Playbook health monitoring completed")
        return "Health monitoring completed"
        
    except Exception as e:
        logger.error(f"Error monitoring playbook health: {str(e)}")
        raise


@shared_task
def generate_soar_report():
    """
    Generate SOAR performance and usage report.
    """
    try:
        logger.info("Starting SOAR report generation")
        
        from apps.reports.models import Report
        from apps.accounts.models import User
        
        # Get report data
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Execution statistics
        total_executions = PlaybookExecution.objects.count()
        executions_24h = PlaybookExecution.objects.filter(started_at__gte=last_24h).count()
        executions_7d = PlaybookExecution.objects.filter(started_at__gte=last_7d).count()
        
        successful_executions = PlaybookExecution.objects.filter(status='completed').count()
        failed_executions = PlaybookExecution.objects.filter(status='failed').count()
        
        # Playbook statistics
        active_playbooks = Playbook.objects.filter(is_enabled=True).count()
        total_playbooks = Playbook.objects.count()
        
        # Automation rule statistics
        active_rules = AutomationRule.objects.filter(is_enabled=True).count()
        total_rules = AutomationRule.objects.count()
        
        # Generate report content
        report_content = f"""
# Rapport SOAR - {now.strftime('%Y-%m-%d')}

## Résumé des exécutions
- Total des exécutions: {total_executions}
- Exécutions dernières 24h: {executions_24h}
- Exécutions dernières 7 jours: {executions_7d}
- Exécutions réussies: {successful_executions}
- Exécutions échouées: {failed_executions}
- Taux de succès: {(successful_executions / total_executions * 100):.1f}% (si total > 0)

## Playbooks
- Playbooks actifs: {active_playbooks}
- Total des playbooks: {total_playbooks}

## Règles d'automatisation
- Règles actives: {active_rules}
- Total des règles: {total_rules}

## Top 5 des playbooks les plus exécutés (7 derniers jours)
"""
        
        # Add top playbooks
        from django.db.models import Count
        top_playbooks = PlaybookExecution.objects.filter(
            started_at__gte=last_7d
        ).values('playbook__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        for playbook in top_playbooks:
            report_content += f"- {playbook['playbook__name']}: {playbook['count']} exécutions\n"
        
        # Create report
        system_user = User.objects.filter(role='admin').first()
        if not system_user:
            system_user = User.objects.first()
        
        report = Report.objects.create(
            title=f"Rapport SOAR - {now.strftime('%Y-%m-%d')}",
            description="Rapport automatique des performances SOAR",
            report_type='technical',
            content=report_content,
            summary=f"Rapport SOAR: {total_executions} exécutions, {successful_executions} réussies",
            period_start=last_7d,
            period_end=now,
            created_by=system_user
        )
        
        logger.info(f"Generated SOAR report: {report.id}")
        return f"Generated SOAR report: {report.id}"
        
    except Exception as e:
        logger.error(f"Error generating SOAR report: {str(e)}")
        raise


def _should_trigger_rule(rule: AutomationRule) -> bool:
    """
    Check if an automation rule should trigger.
    
    Args:
        rule: AutomationRule instance
        
    Returns:
        True if rule should trigger
    """
    try:
        conditions = rule.conditions
        
        # Check priority levels
        if 'priority_levels' in conditions:
            # This would need to be implemented based on the specific condition logic
            pass
        
        # Check categories
        if 'categories' in conditions:
            # This would need to be implemented based on the specific condition logic
            pass
        
        # Check impact score threshold
        if 'min_impact_score' in conditions:
            # This would need to be implemented based on the specific condition logic
            pass
        
        # Check time threshold
        if 'time_threshold_hours' in conditions:
            # This would need to be implemented based on the specific condition logic
            pass
        
        # For now, return True to trigger all rules
        # In production, implement proper condition checking
        return True
        
    except Exception as e:
        logger.error(f"Error checking rule conditions: {str(e)}")
        return False
