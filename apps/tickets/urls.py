"""
URL configuration for the tickets application.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Port 3000 - Espace Client
    path('my-tickets/', views.MyTicketsView.as_view(), name='my_tickets'),
    path('create-ticket/', views.MyTicketsView.as_view(), name='create_ticket'),
    
    # Port 8000 - Espace SOC
    path('all-tickets/', views.AllTicketsView.as_view(), name='all_tickets'),
    path('assign-ticket/<str:ticket_id>/', views.AssignTicketView.as_view(), name='assign_ticket'),
    
    # Ticket details and management
    path('ticket/<str:ticket_id>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('ticket/<str:ticket_id>/comments/', views.TicketCommentViewSet.as_view(), name='ticket_comments'),
    path('ticket/<str:ticket_id>/attachments/', views.TicketAttachmentViewSet.as_view(), name='ticket_attachments'),
    path('ticket/<str:ticket_id>/timeline/', views.TicketTimelineView.as_view(), name='ticket_timeline'),
    
    # Statistics and dashboard
    path('statistics/', views.ticket_statistics, name='ticket_statistics'),
    path('dashboard/', views.ticket_dashboard, name='ticket_dashboard'),
    
    # Templates and SLA
    path('templates/', views.TicketTemplateViewSet.as_view(), name='ticket_templates'),
    path('sla/', views.TicketSLAViewSet.as_view(), name='ticket_sla'),
]
