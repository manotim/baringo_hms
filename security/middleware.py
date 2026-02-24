from django.utils import timezone
from .models import AuditLog

class AuditMiddleware:
    """
    Middleware to log all requests
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Code to be executed for each request before the view is called
        response = self.get_response(request)
        
        # Log after response if user is authenticated and it's a modifying action
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.log_action(request)
        
        return response
    
    def log_action(self, request):
        # Don't log for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return
        
        # Determine action based on method and path
        if 'delete' in request.path.lower():
            action = 'DELETE'
        elif 'create' in request.path.lower() or 'add' in request.path.lower():
            action = 'CREATE'
        elif 'update' in request.path.lower() or 'edit' in request.path.lower():
            action = 'UPDATE'
        else:
            action = 'UPDATE'  # Default for POST requests
        
        AuditLog.objects.create(
            user=request.user,
            action=action,
            model_name=request.resolver_match.app_name if request.resolver_match else 'Unknown',
            details=f"{request.method} {request.path}",
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip