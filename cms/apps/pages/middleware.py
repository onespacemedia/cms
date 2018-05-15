from django.utils.http import http_date
from django.utils.deprecation import MiddlewareMixin

class PageLastUpdatedMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, 'pages'):
            response['Last-Modified'] = http_date(request.pages.current.last_modified_date)

        return response
