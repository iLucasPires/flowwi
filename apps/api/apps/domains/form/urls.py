from rest_framework.routers import SimpleRouter

from .views import (
    FormBlockViewSet,
    FormPageViewSet,
    FormResponseViewSet,
    FormViewSet,
)

router = SimpleRouter(trailing_slash=False)

router.register(r"forms", FormViewSet)
router.register(r"form-blocks", FormBlockViewSet)
router.register(r"form-pages", FormPageViewSet)
router.register(r"form-responses", FormResponseViewSet)

urlpatterns = router.urls
