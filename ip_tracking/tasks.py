from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import RequestLog, SuspiciousIP


@shared_task
def detect_suspicious_ips():
    one_hour_ago = now() - timedelta(hours=1)

    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    ip_counts = {}
    for log in logs:
        ip = log.ip_address
        ip_counts[ip] = ip_counts.get(ip, 0) + 1

        if log.path in ["/admin", "/login"]:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip, reason="Accessed sensitive path."
            )

    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip, reason="High request volume (100+/hr)."
            )
