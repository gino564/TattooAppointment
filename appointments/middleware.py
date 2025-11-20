import logging
from django.utils.deprecation import MiddlewareMixin

# Configure logger
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Log the request details
        logger.info(f"[REQUEST] {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
        print(f"🔍 [MIDDLEWARE LOG] {request.method} {request.path}")
        return None
    
    def process_response(self, request, response):
        # Log the response status
        logger.info(f"[RESPONSE] {request.path} - Status: {response.status_code}")
        print(f"✅ [MIDDLEWARE LOG] Response Status: {response.status_code}")
        return response