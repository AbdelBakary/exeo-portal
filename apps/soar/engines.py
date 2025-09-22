"""
SOAR engines for executing playbooks and automations.
"""
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Playbook, PlaybookExecution, Action, Integration, SOARLog
from apps.alerts.models import Alert
from apps.incidents.models import Incident
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class PlaybookEngine:
    """Engine for executing SOAR playbooks."""
    
    def __init__(self):
        self.action_engines = {
            'email_notification': EmailNotificationEngine(),
            'slack_notification': SlackNotificationEngine(),
            'create_ticket': CreateTicketEngine(),
            'assign_alert': AssignAlertEngine(),
            'block_ip': BlockIPEngine(),
            'quarantine_file': QuarantineFileEngine(),
            'update_status': UpdateStatusEngine(),
            'add_comment': AddCommentEngine(),
            'escalate': EscalateEngine(),
            'webhook': WebhookEngine(),
            'script': ScriptEngine(),
        }
    
    def execute_playbook(self, playbook: Playbook, trigger_data: Dict) -> PlaybookExecution:
        """
        Execute a playbook with given trigger data.
        
        Args:
            playbook: The playbook to execute
            trigger_data: Data that triggered the playbook
            
        Returns:
            PlaybookExecution instance
        """
        execution = PlaybookExecution.objects.create(
            playbook=playbook,
            trigger_type=trigger_data.get('type', 'manual'),
            trigger_data=trigger_data,
            status='running',
            executed_by=trigger_data.get('user')
        )
        
        try:
            # Log execution start
            self._log_execution(execution, 'info', 'playbook', 'Playbook execution started')
            
            # Execute each step
            steps = playbook.steps or []
            total_steps = len(steps)
            execution.total_steps = total_steps
            
            success_count = 0
            failure_count = 0
            
            for i, step in enumerate(steps):
                try:
                    # Execute step
                    step_result = self._execute_step(execution, step, trigger_data)
                    
                    if step_result.get('success', False):
                        success_count += 1
                        self._log_execution(
                            execution, 'info', 'step',
                            f"Step {i+1} executed successfully: {step.get('name', 'Unknown')}"
                        )
                    else:
                        failure_count += 1
                        self._log_execution(
                            execution, 'error', 'step',
                            f"Step {i+1} failed: {step_result.get('error', 'Unknown error')}"
                        )
                    
                    execution.steps_completed = i + 1
                    execution.save()
                    
                except Exception as e:
                    failure_count += 1
                    self._log_execution(
                        execution, 'error', 'step',
                        f"Step {i+1} failed with exception: {str(e)}"
                    )
                    continue
            
            # Update execution results
            execution.success_count = success_count
            execution.failure_count = failure_count
            execution.status = 'completed' if failure_count == 0 else 'failed'
            execution.completed_at = timezone.now()
            execution.execution_time = (execution.completed_at - execution.started_at).total_seconds()
            
            # Log completion
            self._log_execution(
                execution, 'info', 'playbook',
                f"Playbook execution completed. Success: {success_count}, Failures: {failure_count}"
            )
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            self._log_execution(execution, 'error', 'playbook', f"Playbook execution failed: {str(e)}")
        
        execution.save()
        return execution
    
    def _execute_step(self, execution: PlaybookExecution, step: Dict, trigger_data: Dict) -> Dict:
        """
        Execute a single playbook step.
        
        Args:
            execution: The playbook execution
            step: Step configuration
            trigger_data: Trigger data
            
        Returns:
            Step execution result
        """
        action_type = step.get('action_type')
        parameters = step.get('parameters', {})
        
        # Resolve variables in parameters
        resolved_parameters = self._resolve_variables(parameters, trigger_data, execution)
        
        # Get action engine
        engine = self.action_engines.get(action_type)
        if not engine:
            return {'success': False, 'error': f'Unknown action type: {action_type}'}
        
        # Execute action
        try:
            result = engine.execute(resolved_parameters, execution, trigger_data)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resolve_variables(self, parameters: Dict, trigger_data: Dict, execution: PlaybookExecution) -> Dict:
        """
        Resolve variables in step parameters.
        
        Args:
            parameters: Step parameters
            trigger_data: Trigger data
            execution: Playbook execution
            
        Returns:
            Resolved parameters
        """
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str):
                # Replace variables in string values
                resolved_value = value
                for var_key, var_value in trigger_data.items():
                    placeholder = f"${{{var_key}}}"
                    if placeholder in resolved_value:
                        resolved_value = resolved_value.replace(placeholder, str(var_value))
                
                # Replace execution variables
                execution_vars = {
                    'execution_id': execution.id,
                    'playbook_name': execution.playbook.name,
                    'timestamp': timezone.now().isoformat()
                }
                
                for var_key, var_value in execution_vars.items():
                    placeholder = f"${{{var_key}}}"
                    if placeholder in resolved_value:
                        resolved_value = resolved_value.replace(placeholder, str(var_value))
                
                resolved[key] = resolved_value
            else:
                resolved[key] = value
        
        return resolved
    
    def _log_execution(self, execution: PlaybookExecution, level: str, component: str, message: str):
        """Log execution event."""
        SOARLog.objects.create(
            level=level,
            message=message,
            component=component,
            execution=execution,
            client=execution.playbook.client,
            user=execution.executed_by
        )


class BaseActionEngine:
    """Base class for action engines."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Execute the action with given parameters."""
        raise NotImplementedError


class EmailNotificationEngine(BaseActionEngine):
    """Engine for sending email notifications."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Send email notification."""
        try:
            recipients = parameters.get('recipients', [])
            subject = parameters.get('subject', 'SOAR Notification')
            template = parameters.get('template', 'soar/email_notification.html')
            context = parameters.get('context', {})
            
            # Add execution context
            context.update({
                'execution': execution,
                'trigger_data': trigger_data,
                'timestamp': timezone.now()
            })
            
            # Render email content
            html_content = render_to_string(template, context)
            
            # Send email
            send_mail(
                subject=subject,
                message='',  # Plain text version
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=html_content,
                fail_silently=False
            )
            
            return {'sent': True, 'recipients': len(recipients)}
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            raise


class SlackNotificationEngine(BaseActionEngine):
    """Engine for sending Slack notifications."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Send Slack notification."""
        try:
            webhook_url = parameters.get('webhook_url')
            channel = parameters.get('channel', '#security')
            message = parameters.get('message', 'SOAR Notification')
            
            if not webhook_url:
                raise ValueError("Slack webhook URL is required")
            
            # Prepare Slack message
            slack_data = {
                'channel': channel,
                'text': message,
                'username': 'SOAR Bot',
                'icon_emoji': ':robot_face:'
            }
            
            # Add execution details
            if execution:
                slack_data['attachments'] = [{
                    'color': 'good' if execution.status == 'completed' else 'danger',
                    'fields': [
                        {'title': 'Playbook', 'value': execution.playbook.name, 'short': True},
                        {'title': 'Status', 'value': execution.status, 'short': True},
                        {'title': 'Execution ID', 'value': str(execution.id), 'short': True}
                    ]
                }]
            
            # Send to Slack
            response = requests.post(webhook_url, json=slack_data, timeout=30)
            response.raise_for_status()
            
            return {'sent': True, 'response': response.status_code}
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            raise


class CreateTicketEngine(BaseActionEngine):
    """Engine for creating tickets in external systems."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Create ticket in external system."""
        try:
            integration_id = parameters.get('integration_id')
            title = parameters.get('title', 'SOAR Generated Ticket')
            description = parameters.get('description', '')
            priority = parameters.get('priority', 'medium')
            
            if not integration_id:
                raise ValueError("Integration ID is required")
            
            integration = Integration.objects.get(id=integration_id)
            
            # Prepare ticket data
            ticket_data = {
                'title': title,
                'description': description,
                'priority': priority,
                'source': 'SOAR',
                'execution_id': execution.id
            }
            
            # Send to external system
            if integration.integration_type == 'api':
                response = self._create_api_ticket(integration, ticket_data)
            elif integration.integration_type == 'webhook':
                response = self._create_webhook_ticket(integration, ticket_data)
            else:
                raise ValueError(f"Unsupported integration type: {integration.integration_type}")
            
            return {'created': True, 'ticket_id': response.get('id'), 'response': response}
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            raise
    
    def _create_api_ticket(self, integration: Integration, ticket_data: Dict) -> Dict:
        """Create ticket via API integration."""
        url = f"{integration.base_url}/tickets"
        headers = {
            'Authorization': f"Bearer {integration.api_key}",
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=ticket_data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def _create_webhook_ticket(self, integration: Integration, ticket_data: Dict) -> Dict:
        """Create ticket via webhook integration."""
        response = requests.post(integration.base_url, json=ticket_data, timeout=30)
        response.raise_for_status()
        return response.json()


class AssignAlertEngine(BaseActionEngine):
    """Engine for assigning alerts to users."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Assign alert to user."""
        try:
            alert_id = parameters.get('alert_id')
            user_id = parameters.get('user_id')
            
            if not alert_id or not user_id:
                raise ValueError("Alert ID and User ID are required")
            
            alert = Alert.objects.get(id=alert_id)
            user = User.objects.get(id=user_id)
            
            alert.assigned_to = user
            alert.save()
            
            return {'assigned': True, 'alert_id': alert_id, 'user_id': user_id}
            
        except Exception as e:
            logger.error(f"Error assigning alert: {str(e)}")
            raise


class BlockIPEngine(BaseActionEngine):
    """Engine for blocking IP addresses."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Block IP address via firewall."""
        try:
            ip_address = parameters.get('ip_address')
            integration_id = parameters.get('integration_id')
            duration = parameters.get('duration', 3600)  # 1 hour default
            
            if not ip_address or not integration_id:
                raise ValueError("IP address and integration ID are required")
            
            integration = Integration.objects.get(id=integration_id)
            
            # Prepare block request
            block_data = {
                'ip_address': ip_address,
                'action': 'block',
                'duration': duration,
                'reason': 'SOAR automated response',
                'execution_id': execution.id
            }
            
            # Send to firewall
            if integration.integration_type == 'firewall':
                response = self._block_firewall_ip(integration, block_data)
            else:
                raise ValueError(f"Unsupported integration type for IP blocking: {integration.integration_type}")
            
            return {'blocked': True, 'ip_address': ip_address, 'response': response}
            
        except Exception as e:
            logger.error(f"Error blocking IP: {str(e)}")
            raise
    
    def _block_firewall_ip(self, integration: Integration, block_data: Dict) -> Dict:
        """Block IP via firewall integration."""
        url = f"{integration.base_url}/block"
        headers = {
            'Authorization': f"Bearer {integration.api_key}",
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=block_data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()


class QuarantineFileEngine(BaseActionEngine):
    """Engine for quarantining files."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Quarantine file."""
        try:
            file_path = parameters.get('file_path')
            file_hash = parameters.get('file_hash')
            integration_id = parameters.get('integration_id')
            
            if not file_path and not file_hash:
                raise ValueError("File path or hash is required")
            
            integration = Integration.objects.get(id=integration_id)
            
            # Prepare quarantine request
            quarantine_data = {
                'file_path': file_path,
                'file_hash': file_hash,
                'action': 'quarantine',
                'reason': 'SOAR automated response',
                'execution_id': execution.id
            }
            
            # Send to endpoint protection
            response = self._quarantine_file(integration, quarantine_data)
            
            return {'quarantined': True, 'file_path': file_path, 'response': response}
            
        except Exception as e:
            logger.error(f"Error quarantining file: {str(e)}")
            raise
    
    def _quarantine_file(self, integration: Integration, quarantine_data: Dict) -> Dict:
        """Quarantine file via integration."""
        url = f"{integration.base_url}/quarantine"
        headers = {
            'Authorization': f"Bearer {integration.api_key}",
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=quarantine_data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()


class UpdateStatusEngine(BaseActionEngine):
    """Engine for updating status of alerts or incidents."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Update status of resource."""
        try:
            resource_type = parameters.get('resource_type')  # 'alert' or 'incident'
            resource_id = parameters.get('resource_id')
            new_status = parameters.get('new_status')
            
            if not all([resource_type, resource_id, new_status]):
                raise ValueError("Resource type, ID, and new status are required")
            
            if resource_type == 'alert':
                resource = Alert.objects.get(id=resource_id)
            elif resource_type == 'incident':
                resource = Incident.objects.get(id=resource_id)
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
            
            resource.status = new_status
            resource.save()
            
            return {'updated': True, 'resource_type': resource_type, 'resource_id': resource_id, 'new_status': new_status}
            
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            raise


class AddCommentEngine(BaseActionEngine):
    """Engine for adding comments to alerts or incidents."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Add comment to resource."""
        try:
            resource_type = parameters.get('resource_type')  # 'alert' or 'incident'
            resource_id = parameters.get('resource_id')
            comment = parameters.get('comment')
            is_internal = parameters.get('is_internal', True)
            
            if not all([resource_type, resource_id, comment]):
                raise ValueError("Resource type, ID, and comment are required")
            
            if resource_type == 'alert':
                from apps.alerts.models import AlertComment
                comment_obj = AlertComment.objects.create(
                    alert_id=resource_id,
                    author=execution.executed_by,
                    content=comment,
                    is_internal=is_internal
                )
            elif resource_type == 'incident':
                from apps.incidents.models import IncidentComment
                comment_obj = IncidentComment.objects.create(
                    incident_id=resource_id,
                    author=execution.executed_by,
                    content=comment,
                    is_internal=is_internal
                )
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
            
            return {'added': True, 'comment_id': comment_obj.id}
            
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            raise


class EscalateEngine(BaseActionEngine):
    """Engine for escalating alerts or incidents."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Escalate resource."""
        try:
            resource_type = parameters.get('resource_type')  # 'alert' or 'incident'
            resource_id = parameters.get('resource_id')
            escalate_to_id = parameters.get('escalate_to_id')
            reason = parameters.get('reason', 'SOAR automated escalation')
            
            if not all([resource_type, resource_id, escalate_to_id]):
                raise ValueError("Resource type, ID, and escalate to user are required")
            
            escalate_to = User.objects.get(id=escalate_to_id)
            
            if resource_type == 'alert':
                resource = Alert.objects.get(id=resource_id)
                resource.assigned_to = escalate_to
                resource.status = 'in_progress'
            elif resource_type == 'incident':
                resource = Incident.objects.get(id=resource_id)
                resource.assigned_to = escalate_to
                resource.status = 'assigned'
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
            
            resource.save()
            
            # Add escalation comment
            comment = f"Escalated to {escalate_to.get_full_name()}: {reason}"
            if resource_type == 'alert':
                from apps.alerts.models import AlertComment
                AlertComment.objects.create(
                    alert=resource,
                    author=execution.executed_by,
                    content=comment,
                    is_internal=True
                )
            elif resource_type == 'incident':
                from apps.incidents.models import IncidentComment
                IncidentComment.objects.create(
                    incident=resource,
                    author=execution.executed_by,
                    content=comment,
                    is_internal=True
                )
            
            return {'escalated': True, 'resource_type': resource_type, 'resource_id': resource_id, 'escalate_to': escalate_to_id}
            
        except Exception as e:
            logger.error(f"Error escalating resource: {str(e)}")
            raise


class WebhookEngine(BaseActionEngine):
    """Engine for sending webhook notifications."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Send webhook notification."""
        try:
            url = parameters.get('url')
            method = parameters.get('method', 'POST')
            headers = parameters.get('headers', {})
            data = parameters.get('data', {})
            
            if not url:
                raise ValueError("Webhook URL is required")
            
            # Add execution context to data
            data.update({
                'execution_id': execution.id,
                'playbook_name': execution.playbook.name,
                'timestamp': timezone.now().isoformat()
            })
            
            # Send webhook
            if method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            return {'sent': True, 'status_code': response.status_code, 'response': response.text}
            
        except Exception as e:
            logger.error(f"Error sending webhook: {str(e)}")
            raise


class ScriptEngine(BaseActionEngine):
    """Engine for executing custom scripts."""
    
    def execute(self, parameters: Dict, execution: PlaybookExecution, trigger_data: Dict) -> Dict:
        """Execute custom script."""
        try:
            script_path = parameters.get('script_path')
            script_content = parameters.get('script_content')
            script_type = parameters.get('script_type', 'python')
            args = parameters.get('args', [])
            
            if not script_path and not script_content:
                raise ValueError("Script path or content is required")
            
            # This is a simplified implementation
            # In production, you would need proper sandboxing and security measures
            import subprocess
            import tempfile
            import os
            
            if script_content:
                # Create temporary script file
                with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{script_type}', delete=False) as f:
                    f.write(script_content)
                    script_path = f.name
            
            # Execute script
            result = subprocess.run(
                [script_type, script_path] + args,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Clean up temporary file
            if script_content:
                os.unlink(script_path)
            
            return {
                'executed': True,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            raise


# Global playbook engine instance
playbook_engine = PlaybookEngine()
