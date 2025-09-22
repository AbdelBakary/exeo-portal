"""
Signals for the tickets application.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ClientTicket, TicketTimeline


@receiver(post_save, sender=ClientTicket)
def ticket_created_handler(sender, instance, created, **kwargs):
    """Handle ticket creation - create timeline event."""
    if created:
        TicketTimeline.objects.create(
            ticket=instance,
            event_type='created',
            description=f"Ticket créé par {instance.created_by.get_full_name()}",
            user=instance.created_by,
            metadata={
                'ticket_id': instance.ticket_id,
                'category': instance.category,
                'priority': instance.priority
            }
        )


@receiver(pre_save, sender=ClientTicket)
def ticket_pre_save_handler(sender, instance, **kwargs):
    """Store old values before saving."""
    if instance.pk:
        try:
            old_instance = ClientTicket.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_priority = old_instance.priority
        except ClientTicket.DoesNotExist:
            pass


@receiver(post_save, sender=ClientTicket)
def ticket_updated_handler(sender, instance, created, **kwargs):
    """Handle ticket updates - create timeline events."""
    if not created and hasattr(instance, '_old_status'):
        # Check for status changes
        if instance._old_status != instance.status:
            TicketTimeline.objects.create(
                ticket=instance,
                event_type='status_changed',
                description=f"Statut changé de {instance._old_status} à {instance.status}",
                user=instance.assigned_to,
                metadata={
                    'old_status': instance._old_status,
                    'new_status': instance.status
                }
            )
        
        # Check for priority changes
        if hasattr(instance, '_old_priority') and instance._old_priority != instance.priority:
            TicketTimeline.objects.create(
                ticket=instance,
                event_type='priority_changed',
                description=f"Priorité changée de {instance._old_priority} à {instance.priority}",
                user=instance.assigned_to,
                metadata={
                    'old_priority': instance._old_priority,
                    'new_priority': instance.priority
                }
            )
        
        # Check for assignment changes
        if hasattr(instance, '_old_assigned_to') and instance._old_assigned_to != instance.assigned_to:
            if instance.assigned_to:
                TicketTimeline.objects.create(
                    ticket=instance,
                    event_type='assigned',
                    description=f"Ticket assigné à {instance.assigned_to.get_full_name()}",
                    user=instance.assigned_by,
                    metadata={
                        'assigned_to': instance.assigned_to.id,
                        'assigned_by': instance.assigned_by.id if instance.assigned_by else None
                    }
                )

