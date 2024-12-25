from django.shortcuts import render

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 404:
            # Handle the 404 error here, e.g., return a custom response or redirect
            return render(request, 'handler/404.html')

        return response
