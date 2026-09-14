from rest_framework.routers import SimpleRouter

from .views import WorkplaceMemberViewSet, WorkplaceViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"workplaces", WorkplaceViewSet)
router.register(r"workplace-members", WorkplaceMemberViewSet)

urlpatterns = router.urls
