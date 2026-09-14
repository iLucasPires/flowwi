from rest_framework.routers import SimpleRouter

from .views import UnsplashViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"unsplash", UnsplashViewSet, basename="unsplash")

urlpatterns = router.urls
