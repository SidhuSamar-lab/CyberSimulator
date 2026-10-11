"""
CyberSimulator - Top-Level API URL Dispatcher.
Routes versioned API namespaces.
"""
from django.urls import path, include
from .v1.views import api_root

urlpatterns = [
    path('', api_root, name='api_root'),
    path('v1/', include('api.v1.urls')),
]
