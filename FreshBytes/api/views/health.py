"""
Health check endpoints for monitoring system status.
"""
import logging
import psutil
import os
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Comprehensive health check endpoint that monitors:
    - Database connectivity
    - Cache functionality
    - System resources (CPU, Memory, Disk)
    - Application status
    """
    logger.info("Health check requested")
    
    status_info = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'environment': 'development' if settings.DEBUG else 'production',
        'checks': {}
    }
    
    # Database connectivity check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status_info['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
            logger.debug("Database health check passed")
    except Exception as e:
        status_info['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        status_info['status'] = 'unhealthy'
        logger.error(f"Database health check failed: {str(e)}")
    
    # Cache functionality check
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status_info['checks']['cache'] = {
                'status': 'healthy',
                'message': 'Cache functionality working'
            }
            logger.debug("Cache health check passed")
        else:
            status_info['checks']['cache'] = {
                'status': 'unhealthy',
                'message': 'Cache read/write failed'
            }
            status_info['status'] = 'unhealthy'
            logger.error("Cache health check failed - read/write mismatch")
    except Exception as e:
        status_info['checks']['cache'] = {
            'status': 'unhealthy',
            'message': f'Cache connection failed: {str(e)}'
        }
        status_info['status'] = 'unhealthy'
        logger.error(f"Cache health check failed: {str(e)}")
    
    # System resources check
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status_info['checks']['system'] = {
            'status': 'healthy',
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'disk_percent': disk.percent,
            'disk_free_gb': round(disk.free / (1024**3), 2)
        }
        
        # Check if system resources are within acceptable limits
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            status_info['checks']['system']['status'] = 'warning'
            status_info['checks']['system']['message'] = 'System resources are high'
            logger.warning(f"High system resource usage - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
        else:
            status_info['checks']['system']['message'] = 'System resources are normal'
            logger.debug(f"System resources normal - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
            
    except Exception as e:
        status_info['checks']['system'] = {
            'status': 'unhealthy',
            'message': f'System resource check failed: {str(e)}'
        }
        status_info['status'] = 'unhealthy'
        logger.error(f"System resource check failed: {str(e)}")
    
    # Application status check
    try:
        # Check if critical settings are configured
        critical_settings = [
            'SECRET_KEY',
            'DATABASES',
            'REST_FRAMEWORK'
        ]
        
        missing_settings = []
        for setting in critical_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            status_info['checks']['application'] = {
                'status': 'unhealthy',
                'message': f'Missing critical settings: {", ".join(missing_settings)}'
            }
            status_info['status'] = 'unhealthy'
            logger.error(f"Missing critical settings: {missing_settings}")
        else:
            status_info['checks']['application'] = {
                'status': 'healthy',
                'message': 'Application configuration is valid'
            }
            logger.debug("Application configuration check passed")
            
    except Exception as e:
        status_info['checks']['application'] = {
            'status': 'unhealthy',
            'message': f'Application check failed: {str(e)}'
        }
        status_info['status'] = 'unhealthy'
        logger.error(f"Application check failed: {str(e)}")
    
    # Log overall health status
    if status_info['status'] == 'healthy':
        logger.info("Health check completed - all systems healthy")
    else:
        logger.warning(f"Health check completed - system unhealthy: {status_info['status']}")
    
    return Response(status_info, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([])
def health_check(request):
    """
    Simple health check for load balancers and basic monitoring.
    Returns minimal information for quick status checks.
    """
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'ok',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Simple health check failed: {str(e)}")
        return Response({
            'status': 'error',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE) 