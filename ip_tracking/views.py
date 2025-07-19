from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit


@ratelimit(key="ip", rate="10/m", method="GET", block=True)
@ratelimit(key="ip", rate="5/m", method="GET", block=True)
def login_view(request):
    return JsonResponse({"message": "This is a login view"})
