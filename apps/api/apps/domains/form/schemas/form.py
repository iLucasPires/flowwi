from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

# =============================================================================
# Enums
# =============================================================================


class BlockType(StrEnum):
    TEXT = "text"
    EMAIL = "email"
    NUMBER = "number"
    TIME = "time"
    DATE = "date"
    FILE = "file"
    CHOICE = "choice"
    SELECT = "select"
    CONTENT = "content"
    PHONE = "phone"
    URL = "url"
    YES_NO = "yes_no"
    RATING = "rating"
    SCALE = "scale"
    SLIDER = "slider"
    RANKING = "ranking"
    COUNTRY = "country"
    SIGNATURE = "signature"


class ConditionOperator(StrEnum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


# =============================================================================
# Condition (single + nested groups)
# =============================================================================


class ConditionSchema(BaseModel):
    """Visibility condition referencing another block's value."""

    field_id: str = Field(description="client_id of the block this condition references")
    operator: ConditionOperator
    value: str | int | float | bool | None = None

    model_config = {"extra": "forbid"}


class ConditionGroupSchema(BaseModel):
    """Group of rules combined with AND/OR. Can be nested arbitrarily."""

    op: Literal["and", "or"]
    rules: list["ConditionSchema | ConditionGroupSchema"]

    model_config = {"extra": "forbid"}


ConditionGroupSchema.model_rebuild()

# Accepted condition payloads: legacy single rule, or a group
ConditionPayload = ConditionSchema | ConditionGroupSchema


# =============================================================================
# Layout
# =============================================================================


class BlockLayout(BaseModel):
    col_span: int = 0
    col_start: int = 0

    model_config = {"extra": "forbid"}


# =============================================================================
# Field Configs (Discriminated Union)
# =============================================================================


class BaseFieldConfig(BaseModel):
    """Common properties app by all field configs."""

    placeholder: str | None = None
    help_text: str | None = None
    hidden: bool = False
    disabled: bool = False

    model_config = {"extra": "forbid"}


class TextFieldConfig(BaseFieldConfig):
    type: Literal["text", "email", "phone", "url"] = "text"
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    long: bool | None = None


class NumberFieldConfig(BaseFieldConfig):
    type: Literal["number", "slider"] = "number"
    min: float | None = None
    max: float | None = None
    step: float | None = None


class DateFieldConfig(BaseFieldConfig):
    type: Literal["date"] = "date"
    min_date: str | None = None
    max_date: str | None = None


class TimeFieldConfig(BaseFieldConfig):
    type: Literal["time"] = "time"


class SelectOption(BaseModel):
    label: str
    value: str | int | float | bool

    model_config = {"extra": "forbid"}


class SelectFieldConfig(BaseFieldConfig):
    type: Literal["select", "choice", "ranking"] = "select"
    options: list[SelectOption] = Field(default_factory=list)
    multiple: bool | None = None

    @field_validator("options")
    @classmethod
    def at_least_one_option(cls, v: list[SelectOption]) -> list[SelectOption]:
        if not v:
            raise ValueError("At least one option is required.")
        return v


class FileFieldConfig(BaseFieldConfig):
    type: Literal["file"] = "file"
    accept: list[str] | None = None
    max_size: int | None = None
    multiple: bool | None = None


class ContentFieldConfig(BaseModel):
    """Free-form text block (heading/paragraph) with no associated answer.

    `node` stores the raw ProseMirror/Tiptap JSON node so the editor can
    round-trip it (marks, links, heading level) without lossy conversion.
    """

    type: Literal["content"] = "content"
    node: dict = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class YesNoFieldConfig(BaseFieldConfig):
    type: Literal["yes_no"] = "yes_no"
    yes_label: str = "Yes"
    no_label: str = "No"


class RatingFieldConfig(BaseFieldConfig):
    type: Literal["rating"] = "rating"
    max_stars: int = 5
    icon: str = "star"  # star | heart | thumb
    allow_half: bool = False


class ScaleFieldConfig(BaseFieldConfig):
    type: Literal["scale"] = "scale"
    min_label: str = ""
    max_label: str = ""
    min_value: int = 0
    max_value: int = 10
    show_labels: bool = True


class CountryFieldConfig(BaseFieldConfig):
    type: Literal["country"] = "country"
    preferred: list[str] | None = None  # ISO country codes pinned to top


class SignatureFieldConfig(BaseFieldConfig):
    type: Literal["signature"] = "signature"
    typed_allowed: bool = True  # allow typed as fallback to drawn


FieldConfig = Annotated[
    TextFieldConfig
    | NumberFieldConfig
    | DateFieldConfig
    | TimeFieldConfig
    | SelectFieldConfig
    | FileFieldConfig
    | ContentFieldConfig
    | YesNoFieldConfig
    | RatingFieldConfig
    | ScaleFieldConfig
    | CountryFieldConfig
    | SignatureFieldConfig,
    Field(discriminator="type"),
]


# =============================================================================
# Mapping (backward compat for validators that resolve by block type string)
# =============================================================================

BLOCK_CONFIG_SCHEMAS: dict[str, type[BaseModel]] = {
    BlockType.TEXT: TextFieldConfig,
    BlockType.EMAIL: TextFieldConfig,
    BlockType.PHONE: TextFieldConfig,
    BlockType.URL: TextFieldConfig,
    BlockType.NUMBER: NumberFieldConfig,
    BlockType.SLIDER: NumberFieldConfig,
    BlockType.TIME: TimeFieldConfig,
    BlockType.DATE: DateFieldConfig,
    BlockType.SELECT: SelectFieldConfig,
    BlockType.CHOICE: SelectFieldConfig,
    BlockType.RANKING: SelectFieldConfig,
    BlockType.FILE: FileFieldConfig,
    BlockType.CONTENT: ContentFieldConfig,
    BlockType.YES_NO: YesNoFieldConfig,
    BlockType.RATING: RatingFieldConfig,
    BlockType.SCALE: ScaleFieldConfig,
    BlockType.COUNTRY: CountryFieldConfig,
    BlockType.SIGNATURE: SignatureFieldConfig,
}
