from pydantic import BaseModel, Field

from lib.bases import ServiceBase

from ..models import Form
from ..selectors import FormSelector

# -------------------------------------------------------------------------
# Insight schemas (output only)
# -------------------------------------------------------------------------


class BlockInsight(BaseModel):
    block_id: int
    title: str
    type: str
    order: int
    answered: int
    skipped: int
    options: list[dict] | None = None


class FormInsights(BaseModel):
    form_id: int
    title: str
    total_responses: int
    submissions_over_time: list[dict] = Field(default_factory=list)
    blocks: list[BlockInsight] = Field(default_factory=list)


# -------------------------------------------------------------------------
# Service
# -------------------------------------------------------------------------


class FormService(ServiceBase):
    def __init__(self):
        super().__init__(model=Form)

    def get_published(self, public_id: str) -> Form | None:
        return FormSelector.get_public(public_id)

    # keep backward compat alias
    get_public_form = get_published

    def get_insights(self, form: Form) -> dict:
        total = form.responses.count()
        blocks = form.blocks.order_by("page__order", "order")
        answered_map = FormSelector.count_answered(form)
        choice_block_ids = [b.id for b in blocks if b.type in ("choice", "select")]
        options_map = FormSelector.count_options(form, choice_block_ids)

        block_insights = [
            BlockInsight(
                block_id=block.id,
                title=block.title,
                type=block.type,
                order=block.order,
                answered=answered_map.get(block.id, 0),
                skipped=total - answered_map.get(block.id, 0),
                options=options_map.get(block.id),
            )
            for block in blocks
        ]

        return FormInsights(
            form_id=form.id,
            title=form.title,
            total_responses=total,
            submissions_over_time=FormSelector.count_submissions(form),
            blocks=block_insights,
        ).model_dump()
