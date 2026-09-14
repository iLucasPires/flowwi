from pydantic import BaseModel, Field

from .form import BlockLayout, BlockType, ConditionSchema


class PageInput(BaseModel):
    title: str = ""
    description: str = ""

    model_config = {"extra": "ignore"}


class BlockInput(BaseModel):
    """Aggregator schema for a form block received from the API.

    Keeps backward compatibility with the existing flat payload structure
    while providing strong typing internally.
    """

    id: int | None = None
    title: str = ""
    type: BlockType = BlockType.TEXT
    required: bool = False
    order: int = 0
    config: dict = Field(default_factory=dict)
    layout: BlockLayout = Field(default_factory=BlockLayout)
    condition: ConditionSchema | None = None
    client_id: str = ""
    page: int | None = None
    page_order: int | None = None

    model_config = {"extra": "ignore"}

    def to_db_fields(self, *, exclude_id: bool = True) -> dict:
        """Return a dict ready for model create/update, flattening layout."""
        data = self.model_dump(
            exclude={"id", "page", "page_order", "layout"} if exclude_id else {"page", "page_order", "layout"},
        )
        data["col_span"] = self.layout.col_span
        data["col_start"] = self.layout.col_start
        data["page_id"] = self.page
        # Serialize condition to dict for JSONField storage
        data["condition"] = self.condition.model_dump() if self.condition else {}
        return data

    @classmethod
    def from_raw(cls, raw: dict) -> "BlockInput":
        """Parse raw API payload, mapping flat col_span/col_start into layout."""
        layout_data = {}
        if "col_span" in raw:
            layout_data["col_span"] = raw.pop("col_span")
        if "col_start" in raw:
            layout_data["col_start"] = raw.pop("col_start")
        if layout_data and "layout" not in raw:
            raw["layout"] = layout_data

        # Map legacy `condition` dict into ConditionSchema-compatible format
        condition = raw.get("condition")
        if isinstance(condition, dict) and condition:
            # Rename legacy `client_id` key to `field_id`
            if "client_id" in condition and "field_id" not in condition:
                condition["field_id"] = condition.pop("client_id")
            raw["condition"] = condition
        elif not condition:
            raw["condition"] = None

        return cls(**raw)
