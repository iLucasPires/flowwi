from urllib.parse import urlencode

from django.conf import settings
from rest_framework import serializers

# Unsplash requires every attribution link back to the photographer and to Unsplash
# itself to carry these UTM parameters.
UTM_PARAMS = {
    "utm_source": settings.UNSPLASH_APP_NAME,
    "utm_medium": "referral",
}


def with_utm(url: str | None) -> str:
    if not url:
        return ""

    separator = "&" if "?" in url else "?"

    return f"{url}{separator}{urlencode(UTM_PARAMS)}"


class UnsplashPhotoSerializer(serializers.Serializer):
    """
    Trimmed-down view of an Unsplash photo — only what the cover picker renders,
    plus the attribution the API guidelines require us to display and store.
    """

    id = serializers.CharField()
    color = serializers.CharField(allow_null=True, required=False)
    blur_hash = serializers.CharField(allow_null=True, required=False)
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)

    description = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    download_location = serializers.SerializerMethodField()
    credit = serializers.SerializerMethodField()

    def get_description(self, photo: dict) -> str:
        return photo.get("alt_description") or photo.get("description") or ""

    def get_thumb_url(self, photo: dict) -> str:
        urls = photo.get("urls") or {}

        return urls.get("thumb") or urls.get("small") or ""

    def get_preview_url(self, photo: dict) -> str:
        urls = photo.get("urls") or {}

        return urls.get("small") or urls.get("regular") or ""

    def get_cover_url(self, photo: dict) -> str:
        """The URL stored as the cover — `regular` is 1080px wide, plenty for a banner."""
        urls = photo.get("urls") or {}

        return urls.get("regular") or urls.get("full") or ""

    def get_download_location(self, photo: dict) -> str:
        return (photo.get("links") or {}).get("download_location") or ""

    def get_credit(self, photo: dict) -> dict:
        user = photo.get("user") or {}
        user_links = user.get("links") or {}

        return {
            "source": "unsplash",
            "photo_id": photo.get("id") or "",
            "photo_url": with_utm((photo.get("links") or {}).get("html")),
            "author_name": user.get("name") or "",
            "author_username": user.get("username") or "",
            "author_url": with_utm(user_links.get("html")),
        }


class UnsplashSearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True, max_length=120)
    page = serializers.IntegerField(required=False, min_value=1, max_value=50, default=1)
    per_page = serializers.IntegerField(required=False, min_value=1, max_value=30, default=24)
    orientation = serializers.ChoiceField(
        required=False,
        choices=["landscape", "portrait", "squarish"],
        default="landscape",
    )


class UnsplashDownloadSerializer(serializers.Serializer):
    download_location = serializers.URLField(max_length=500)
