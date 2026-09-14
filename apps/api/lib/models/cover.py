from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta


class CoverStyleModel(models.Model):
    """
    Cover that is not an uploaded file.

    Models combining this mixin keep their own `ImageField` for uploads; `cover_style`
    holds the alternative — a CSS color/gradient (Gallery picks) or an external image
    URL (Link and Unsplash tabs) — and is ignored while the uploaded cover is set.

    `cover_credit` carries the attribution Unsplash requires whenever one of their
    photos is displayed (photographer name and profile link).
    """

    cover_style = models.CharField(
        verbose_name=_("cover style"),
        max_length=500,
        blank=True,
        default="",
        help_text=_("CSS color/gradient or external image URL. Ignored when a cover file is set."),
    )

    cover_credit = models.JSONField(
        verbose_name=_("cover credit"),
        null=True,
        blank=True,
        help_text=_("Attribution for the cover style when its source requires it (Unsplash)."),
    )

    class Meta(TypedModelMeta):
        abstract = True
