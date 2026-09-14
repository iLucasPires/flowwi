from rest_framework.routers import SimpleRouter

from .views import SubTaskViewSet, TaskStatusViewSet, TaskTagViewSet, TaskTypeViewSet, TaskViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"tasks", TaskViewSet)
router.register(r"subtasks", SubTaskViewSet)
router.register(r"tasktags", TaskTagViewSet)
router.register(r"task-statuses", TaskStatusViewSet)
router.register(r"task-types", TaskTypeViewSet)

urlpatterns = router.urls
