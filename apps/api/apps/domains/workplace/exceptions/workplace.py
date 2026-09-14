from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class WorkplaceAlreadyJoined(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Workplace already joined")


class WorkplaceNameAlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Workplace name already exists")


class WorkplaceInviteKeyError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Workplace invite key error")


class WorkplaceNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("Workplace not found")
