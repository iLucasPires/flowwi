from rest_framework.routers import SimpleRouter

from .views.sticky import StickyViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"stickies", StickyViewSet)

urlpatterns = router.urls
