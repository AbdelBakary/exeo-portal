from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render

# Create your views here.
class ThreatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing threat intelligence
    """
    pass
