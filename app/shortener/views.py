"""
API views for the Shortener app.

Views handle the actual business logic:
  - Receive the HTTP request
  - Validate data using serializers
  - Perform the action (create URL, generate short code)
  - Return the response
"""

from django.core.cache import cache
from django.http import HttpResponseRedirect, Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from shortener.models import URL
from shortener.serializers import URLSerializer
from shortener.utils import generate_short_code

# Redis cache key prefix — keeps URL cache entries organized
# Example key: "shorturl:aB3xZ9" → "https://google.com/..."
CACHE_KEY_PREFIX = "shorturl"

# Cache timeout: 24 hours (in seconds)
# After 24h, expired entries are evicted and re-fetched from DB on next hit
CACHE_TIMEOUT = 60 * 60 * 24


class URLCreateView(APIView):
    """
    POST /api/urls/

    Create a new shortened URL.

    Request body:
      {
        "original_url": "https://example.com/long/path",   ← required
        "custom_alias": "my-brand",                         ← optional
        "expires_at": "2025-12-31T23:59:59Z"               ← optional
      }

    Response (201 Created):
      {
        "id": "uuid-...",
        "original_url": "https://example.com/long/path",
        "short_code": "aB3xZ9",
        "custom_alias": "my-brand",
        "short_url": "http://localhost:8000/my-brand",
        "created_at": "...",
        "expires_at": "...",
        "is_active": true
      }

    Flow:
      1. Validate input via URLSerializer
      2. Generate a unique short code via generate_short_code()
      3. Save the URL to PostgreSQL
      4. Return the created URL with 201 status
    """

    def post(self, request):
        # Step 1: Validate input data
        # Passing request in context so serializer can build absolute URLs
        serializer = URLSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            # Return validation errors (e.g., missing original_url, alias taken)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 2: Generate unique short code
        short_code = generate_short_code()

        # Step 3: Save to database
        # serializer.save() calls URL.objects.create() with validated data
        # We pass short_code as an extra field (not from user input)
        serializer.save(short_code=short_code)

        # Step 4: Return response with 201 Created
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ─── New imports added for Celery task ───
from analytics.tasks import log_click_task


# ... skipping to RedirectView ...
class RedirectView(APIView):
    """
    GET /<short_code>

    Redirects to the original URL.

    This is the most performance-critical endpoint:
      - Called on EVERY link click (100x more reads than writes)
      - Must be as fast as possible — target: <50ms

    Flow:
      1. Check Redis cache for the short code
         → HIT: redirect immediately (fastest path, ~1ms)
      2. MISS: Query PostgreSQL for the URL
         → Not found or inactive/expired: return 404
         → Found: cache in Redis, then redirect
      3. (Later in Step 6: async log the click via Celery)

    Why Redis first?
      - Redis is an in-memory store — lookups take ~1ms
      - PostgreSQL is disk-based — lookups take ~5-50ms
      - At scale (millions of redirects/day), this 5-50x speedup matters enormously
    """

    def get_client_ip(self, request):
        """Extract the real IP address from the request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def get(self, request, short_code):
        # ─── Step 1: Check Redis cache ───
        cache_key = f"{CACHE_KEY_PREFIX}:{short_code}"
        original_url = cache.get(cache_key)

        if original_url:
            self._log_click_async(request, short_code)
            return HttpResponseRedirect(original_url)

        # ─── Step 2: Cache MISS — query PostgreSQL ───
        url_obj = URL.objects.filter(short_code=short_code, is_active=True).first()

        if url_obj is None:
            url_obj = URL.objects.filter(custom_alias=short_code, is_active=True).first()

        if url_obj is None:
            raise Http404("Short URL not found.")

        if url_obj.is_expired:
            raise Http404("This short URL has expired.")

        # ─── Step 3: Cache in Redis for next time ───
        cache.set(cache_key, url_obj.original_url, timeout=CACHE_TIMEOUT)

        # ─── Step 4: Async log the click via Celery ───
        self._log_click_async(request, short_code)

        # ─── Step 5: Redirect ───
        return HttpResponseRedirect(url_obj.original_url)

    def _log_click_async(self, request, short_code):
        """Helper to safely enqueue the analytics task without blocking the thread."""
        try:
            ip_addr = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referer = request.META.get('HTTP_REFERER', '')

            # .delay() sends the task to Redis to be picked up by Celery workers
            log_click_task.delay(
                short_code=short_code,
                ip_address=ip_addr,
                user_agent=user_agent,
                referer=referer
            )
        except Exception:
            # If Redis/Celery is down, silently skip analytics — don't break the redirect
            pass

