from rest_framework.routers import SimpleRouter

from .views import ProfileViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"profiles", ProfileViewSet, basename="profile")

urlpatterns = router.urls
