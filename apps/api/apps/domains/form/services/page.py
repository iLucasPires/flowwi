from lib.bases import ServiceBase

from ..models import FormPage


class FormPageService(ServiceBase):
    def __init__(self):
        super().__init__(model=FormPage)

    def get_by_form(self, form_id: int):
        return self.filter(form_id=form_id)
