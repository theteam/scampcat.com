class NyanCatMiddleware(object):
    """Nyan Nyan Nyan"""

    def process_response(self, request, response):
        response['X-Cat'] = "Nyan nyan nyan nyan"
        return response
