from celery import shared_task
from django.utils import timezone
from shortener.models import URL
from analytics.models import Click


@shared_task
def log_click_task(short_code, ip_address, user_agent, referer):
    """
    Background task to log a click event for a shortened URL.

    This runs asynchronously so the user's redirect isn't blocked
    by a database write.

    Args:
        short_code (str): The short code of the URL clicked
        ip_address (str): The visitor's IP address
        user_agent (str): The visitor's User-Agent string
        referer (str): The HTTP Referer header
    """
    # Find the URL (must handle possibility of custom_alias too)
    url_obj = URL.objects.filter(short_code=short_code).first()
    if url_obj is None:
        url_obj = URL.objects.filter(custom_alias=short_code).first()

    # If URL no longer exists, just drop the click
    if url_obj is None:
        return

    # Create the click record
    Click.objects.create(
        url=url_obj,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        clicked_at=timezone.now()
    )

    # Note: country/city resolution would happen here next
    # (e.g., using GeoIP2) since we are already in a background worker
