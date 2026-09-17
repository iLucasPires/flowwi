from rest_framework.routers import SimpleRouter

from .views import QuickLinkViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"quicklinks", QuickLinkViewSet)

urlpatterns = router.urls
