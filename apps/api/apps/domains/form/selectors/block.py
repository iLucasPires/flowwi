from ..models import Form, FormPage


class FormBlockSelector:
    @staticmethod
    def get_page_ids(form: Form, ids: set[int]) -> set[int]:
        """Return existing page IDs for the given form."""
        return set(
            FormPage.objects.filter(
                form=form,
                id__in=ids,
            ).values_list("id", flat=True)
        )
