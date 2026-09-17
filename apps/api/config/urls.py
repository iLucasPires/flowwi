from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # -------------------------------------------------------------------------
    # Admin
    # -------------------------------------------------------------------------
    path("admin/", admin.site.urls),
    # -------------------------------------------------------------------------
    # Allauth
    # -------------------------------------------------------------------------
    path("allauth/", include("allauth.urls")),
    # -------------------------------------------------------------------------
    # Doc
    # -------------------------------------------------------------------------
    path("schema", SpectacularAPIView.as_view(), name="schema"),
    path("docs", SpectacularSwaggerView.as_view(), name="docs"),
    path("redoc", SpectacularRedocView.as_view(), name="redoc"),
    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------
    path(
        route="api/",
        view=include(
            [
                # -------------------------------------------------------------
                # Allauth
                # -------------------------------------------------------------
                path("", include("allauth.headless.urls"), name="allauth"),
                # -------------------------------------------------------------
                # App Domains
                # -------------------------------------------------------------
                path("", include("apps.domains.media.urls"), name="media"),
                path("", include("apps.domains.document.urls"), name="document"),
                path("", include("apps.domains.form.urls"), name="form"),
                path("", include("apps.domains.inbox.urls"), name="inbox"),
                path("", include("apps.domains.task.urls"), name="task"),
                path("", include("apps.domains.sticky.urls"), name="sticky"),
                path("", include("apps.domains.quicklink.urls"), name="quicklink"),
                path("", include("apps.domains.workplace.urls"), name="workplace"),
                path("", include("apps.domains.user.urls"), name="profile"),
                # -------------------------------------------------------------
                # Apps Integrations
                # -------------------------------------------------------------
                path("", include("apps.integrations.google.urls"), name="google"),
                path("", include("apps.integrations.unsplash.urls"), name="unsplash"),
                # -------------------------------------------------------------
                # Apps Streaming
                # -------------------------------------------------------------
                path("", include("apps.common.streaming.urls"), name="streaming"),
            ]
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
    ]

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
