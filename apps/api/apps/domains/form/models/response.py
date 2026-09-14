from django.db import models
from django.utils.translation import gettext_lazy as _

from lib.models import TimeStampedModel, UUIDModel
from lib.utils.upload import upload_to_path

from .block import FormBlock


class FormResponse(UUIDModel, TimeStampedModel):
    form = models.ForeignKey(
        to="Form",
        related_name="responses",
        on_delete=models.CASCADE,
        verbose_name=_("form"),
        help_text=_("The form that was submitted."),
    )
    respondent_email = models.EmailField(
        blank=True,
        default="",
        verbose_name=_("respondent email"),
        help_text=_("The email address of the person who submitted the form."),
    )
    respondent_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name=_("respondent phone"),
        help_text=_("The phone number of the person who submitted the form."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Form Response")
        verbose_name_plural = _("Form Responses")

    def __str__(self):
        return f"{self.form.title} - {self.created_at}"


class FormAnswer(UUIDModel, TimeStampedModel):
    response = models.ForeignKey(
        to=FormResponse,
        related_name="answers",
        on_delete=models.CASCADE,
        verbose_name=_("response"),
        help_text=_("The form response this answer belongs to."),
    )

    block = models.ForeignKey(
        to=FormBlock,
        related_name="answers",
        on_delete=models.CASCADE,
        verbose_name=_("block"),
        help_text=_("The form block (field) this answer is for."),
    )

    value = models.JSONField(
        verbose_name=_("value"),
        help_text=_("The actual data submitted for this field."),
    )

    class Meta:
        verbose_name = _("Form Answer")
        verbose_name_plural = _("Form Answers")

    def __str__(self):
        return f"{self.block.title}: {self.value}"


class FormAnswerFile(UUIDModel, TimeStampedModel):
    answer = models.ForeignKey(
        to=FormAnswer,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name=_("answer"),
        help_text=_("The form answer this file belongs to."),
    )

    file = models.FileField(
        upload_to=upload_to_path(
            "forms",
            "answers",
            "answer.response.form.pk",
        ),
        verbose_name=_("file"),
        help_text=_("The uploaded file."),
    )

    class Meta:
        verbose_name = _("Form Answer File")
        verbose_name_plural = _("Form Answer Files")
