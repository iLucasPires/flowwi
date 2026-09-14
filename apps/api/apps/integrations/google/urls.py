from rest_framework.routers import SimpleRouter

from .views import GoogleAuthViewSet, GoogleDriveViewSet

router = SimpleRouter(trailing_slash=False)

router.register(r"google-drive", GoogleAuthViewSet, basename="google-auth")
router.register(r"google-drive", GoogleDriveViewSet, basename="google-drive")

urlpatterns = router.urls
