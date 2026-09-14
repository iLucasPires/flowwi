from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from ..serializers import (
    UnsplashDownloadSerializer,
    UnsplashPhotoSerializer,
    UnsplashSearchQuerySerializer,
)
from ..services import (
    UnsplashNotConfiguredError,
    UnsplashService,
    UnsplashUnavailableError,
)


@extend_schema(tags=["Unsplash"])
@extend_schema_view(
    photos=extend_schema(
        parameters=[UnsplashSearchQuerySerializer],
        responses=UnsplashPhotoSerializer(many=True),
    ),
    download=extend_schema(request=UnsplashDownloadSerializer, responses=None),
)
class UnsplashViewSet(viewsets.GenericViewSet):
    """
    Server-side proxy for the Unsplash API used by the cover pickers.

    The access key never reaches the browser, and every listing is served from the
    Redis cache so the shared hourly quota is not burned by the UI typing.
    """

    serializer_class = UnsplashPhotoSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "unsplash"

    @property
    def service(self) -> UnsplashService:
        """Built per request so settings overrides (and key rotation) are picked up."""
        return UnsplashService()

    @action(detail=False, methods=["get"])
    def photos(self, request, *args, **kwargs):
        """Search results when `query` is given, otherwise the popular feed."""
        query_serializer = UnsplashSearchQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        query = (params.get("query") or "").strip()

        try:
            if query:
                payload = self.service.search_photos(
                    query=query,
                    page=params["page"],
                    per_page=params["per_page"],
                    orientation=params["orientation"],
                )
                results = payload.get("results", [])
                total_pages = payload.get("total_pages", 1)

            else:
                results = self.service.list_photos(
                    page=params["page"],
                    per_page=params["per_page"],
                )
                total_pages = None

        except UnsplashNotConfiguredError:
            return Response(
                {"detail": "Unsplash não está configurado nesta instância."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except UnsplashUnavailableError:
            return Response(
                {"detail": "Não foi possível consultar o Unsplash agora."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "results": UnsplashPhotoSerializer(results, many=True).data,
                "page": params["page"],
                "total_pages": total_pages,
            }
        )

    @action(detail=False, methods=["post"])
    def download(self, request, *args, **kwargs):
        """
        Register a download with Unsplash — required by their API guidelines every
        time a user actually picks a photo.
        """
        serializer = UnsplashDownloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.service.track_download(serializer.validated_data["download_location"])

        except UnsplashNotConfiguredError:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except ValueError:
            return Response(
                {"download_location": ["Deve ser uma URL da API do Unsplash."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
