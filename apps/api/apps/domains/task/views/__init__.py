from .status import TaskStatusViewSet
from .subtask import SubTaskViewSet
from .tag import TaskTagViewSet
from .task import TaskViewSet
from .type import TaskTypeViewSet

__all__ = [
    "TaskViewSet",
    "SubTaskViewSet",
    "TaskTagViewSet",
    "TaskStatusViewSet",
    "TaskTypeViewSet",
]
