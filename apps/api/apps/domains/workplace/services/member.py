from lib.bases import ServiceBase

from ..models import WorkplaceMember


class WorkplaceMemberService(ServiceBase):
    """
    Workplace member service class.
    """

    def __init__(self):
        super().__init__(WorkplaceMember)
