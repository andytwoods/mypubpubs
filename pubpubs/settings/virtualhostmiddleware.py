

class VirtualHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # let's configure the root urlconf
        host = request.get_host()
        if 'pub' not in host:
            request.urlconf = 'graffiti.urls'

        # order matters!
        response = self.get_response(request)
        return response