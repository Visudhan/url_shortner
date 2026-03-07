"""
API views for the Analytics app.
"""

from django.db.models import Count
from django.db.models.functions import TruncDate

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from shortener.models import URL
from analytics.models import Click
from analytics.serializers import AnalyticsStatSerializer


class AnalyticsStatView(APIView):
    """
    GET /api/urls/<short_code>/stats/

    Returns click analytics for a specific URL.

    We use Django Database Aggregations here to let PostgreSQL do the heavy lifting
    (counting groups) rather than loading all clicks into memory.
    """

    def get(self, request, short_code):
        # ─── Step 1: Find the URL ───
        url_obj = URL.objects.filter(short_code=short_code).first()
        if not url_obj:
            url_obj = URL.objects.filter(custom_alias=short_code).first()

        if not url_obj:
            raise NotFound("URL not found.")

        # ─── Step 2: Aggregate Data in PostgreSQL ───

        # Total clicks (fast count query)
        total_clicks = Click.objects.filter(url=url_obj).count()

        # Group by Date (PostgreSQL TruncDate)
        # Returns: [{'date': '2025-01-01', 'ct': 5}, {'date': '2025-01-02', 'ct': 12}]
        clicks_by_date_qs = (
            Click.objects.filter(url=url_obj)
            .annotate(date=TruncDate('clicked_at'))
            .values('date')
            .annotate(ct=Count('id'))
            .order_by('-date')
        )
        
        # Format for serializer: {'2025-01-01': 5, etc.}
        clicks_by_date = {
            str(item['date']): item['ct'] 
            for item in clicks_by_date_qs if item['date']
        }

        # Group by Country
        clicks_by_country_qs = (
            Click.objects.filter(url=url_obj)
            .values('country')
            .annotate(ct=Count('id'))
            .order_by('-ct')
        )
        clicks_by_country = {
            item['country'] or 'Unknown': item['ct'] 
            for item in clicks_by_country_qs
        }

        # Group by Referer
        clicks_by_referer_qs = (
            Click.objects.filter(url=url_obj)
            .values('referer')
            .annotate(ct=Count('id'))
            .order_by('-ct')
        )
        clicks_by_referer = {
            item['referer'] or 'Direct': item['ct'] 
            for item in clicks_by_referer_qs
        }

        # ─── Step 3: Serialize and Return ───
        
        data = {
            "total_clicks": total_clicks,
            "clicks_by_date": clicks_by_date,
            "clicks_by_country": clicks_by_country,
            "clicks_by_referer": clicks_by_referer,
        }

        serializer = AnalyticsStatSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
