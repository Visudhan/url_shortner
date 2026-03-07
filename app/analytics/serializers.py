"""
Serializers for Analytics app.
"""

from rest_framework import serializers


class AnalyticsStatSerializer(serializers.Serializer):
    """
    Serializer for the aggregated analytics report.

    We aren't using a ModelSerializer because we are returning
    aggregation results (Counts over time/countries), not raw Click rows.
    """
    total_clicks = serializers.IntegerField()
    clicks_by_date = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Format: {'YYYY-MM-DD': count}"
    )
    clicks_by_country = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Format: {'US': count, 'UK': count}"
    )
    clicks_by_referer = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Format: {'https://google.com': count}"
    )
