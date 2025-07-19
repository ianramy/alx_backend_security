from .models import RequestLog, BlockedIP
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django_ip_geolocation import IpGeolocationAPI
from django.core.cache import cache

api_key = "your_api_key_here"
geo = IpGeolocationAPI(api_key)

class LogIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")
        path = request.path

        RequestLog.objects.create(ip_address=ip, path=path, timestamp=now())

        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access denied.")

        cached_geo = cache.get(ip)
        if not cached_geo:
            response = geo.get_geolocation_data(ip_address=ip)
            country = response.get("country_name")
            city = response.get("city")
            cache.set(ip, (country, city), 60 * 60 * 24)
        else:
            country, city = cached_geo

        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            country=country,
            city=city,
            timestamp=now(),
        )

        RequestLog.objects.create(ip_address=ip, path=request.path, timestamp=now())
        return self.get_response(request)
