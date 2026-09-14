from rest_framework.routers import SimpleRouter

from .views import InboxViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"inbox", InboxViewSet, basename="inbox")

urlpatterns = router.urls
