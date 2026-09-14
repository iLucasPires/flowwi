from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from lib.bases import ServiceBase

from ..models import Form, FormBlock, FormPage
from ..schemas import BlockInput, PageInput
from ..selectors import FormBlockSelector


class FormBlockService(ServiceBase):
    def __init__(self):
        super().__init__(model=FormBlock)

    @transaction.atomic
    def bulk_sync(self, form: Form, raw_pages: list, raw_blocks: list) -> list[FormBlock]:
        """Delete everything and recreate from scratch."""
        pages_in = [PageInput(**p) for p in raw_pages]
        blocks_in = self._parse_and_sort(raw_blocks)
        self._validate_grid_overflow(blocks_in, form.grid_columns or 1)

        self.filter(form=form).delete()
        FormPage.objects.filter(form=form).delete()

        pages = self._create_pages(form, pages_in)
        return self._create_blocks(form, blocks_in, pages)

    @transaction.atomic
    def bulk_upsert(self, form: Form, raw_blocks: list) -> list[FormBlock]:
        """Update existing blocks, create new ones, remove the rest.

        Matching prefers the numeric `id`, but falls back to `client_id`:
        client-created blocks never carry a numeric id (the frontend keeps
        using its own generated `client_id` as the stable key across saves),
        so matching by id alone would treat every block as new on every
        autosave and delete+recreate the whole set — cascading into deleted
        `FormAnswer` rows for existing responses.
        """
        blocks_in = self._parse_and_sort(raw_blocks)
        self._validate_pages_belong_to_form(form, blocks_in)
        self._validate_grid_overflow(blocks_in, form.grid_columns or 1)

        # Delete blocks not in the new list first to avoid unique constraint conflicts
        incoming_ids = {b.id for b in blocks_in if b.id}
        incoming_client_ids = {b.client_id for b in blocks_in if b.client_id}
        self.filter(form=form).exclude(
            Q(id__in=incoming_ids) | Q(client_id__in=incoming_client_ids),
        ).delete()

        # Clear all orders to avoid conflicts during reassignment
        self.filter(form=form).update(order=-1)
        existing_by_id = self.filter(form=form).in_bulk()
        existing_by_client_id = {b.client_id: b for b in existing_by_id.values() if b.client_id}

        saved_ids = []
        for order, block in enumerate(blocks_in):
            saved_id = self._save_block(form, block, order, existing_by_id, existing_by_client_id)
            saved_ids.append(saved_id)

        return list(self.filter(id__in=saved_ids).order_by("page__order", "order"))

    # -------------------------------------------------------------------------
    # Parsing
    # -------------------------------------------------------------------------

    def _parse_and_sort(self, raw: list) -> list[BlockInput]:
        blocks = [BlockInput.from_raw(dict(b)) for b in raw]
        blocks.sort(key=lambda b: (b.page_order or b.page or 0, b.order))
        return blocks

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    def _create_pages(self, form: Form, pages: list[PageInput]) -> list[FormPage]:
        if not pages:
            return [FormPage.objects.create(form=form, order=0)]

        return FormPage.objects.bulk_create(
            [FormPage(form=form, order=i, title=p.title, description=p.description) for i, p in enumerate(pages)]
        )

    def _create_blocks(
        self,
        form: Form,
        blocks: list[BlockInput],
        pages: list[FormPage],
    ) -> list[FormBlock]:
        objects = []
        for order, block in enumerate(blocks):
            page = self._get_page_for_block(block, pages)
            fields = block.to_db_fields()
            fields.pop("page_id", None)
            objects.append(FormBlock(form=form, page=page, order=order, **fields))

        return self.bulk_create(objects)

    def _save_block(
        self,
        form: Form,
        block: BlockInput,
        order: int,
        existing_by_id: dict,
        existing_by_client_id: dict,
    ) -> int:
        """Create or update a single block. Returns the saved ID."""
        fields = block.to_db_fields()
        fields["order"] = order

        instance = existing_by_id.get(block.id) if block.id else None
        if not instance and block.client_id:
            instance = existing_by_client_id.get(block.client_id)

        if instance:
            for key, value in fields.items():
                setattr(instance, key, value)
            instance.save()
            return instance.id

        return self.create({"form": form, **fields}).id

    def _get_page_for_block(self, block: BlockInput, pages: list[FormPage]) -> FormPage:
        if block.page_order is not None and 0 <= block.page_order < len(pages):
            return pages[block.page_order]
        return pages[0]

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    def _validate_pages_belong_to_form(self, form: Form, blocks: list[BlockInput]):
        page_ids = {b.page for b in blocks if b.page is not None}
        if not page_ids:
            return

        existing = FormBlockSelector.get_page_ids(form, page_ids)
        missing = page_ids - existing
        if missing:
            raise ValidationError(f"Pages inválidas: {sorted(missing)}")

    def _validate_grid_overflow(self, blocks: list[BlockInput], grid: int):
        if grid <= 1:
            return

        row_used = 0
        current_page = None

        for block in blocks:
            page_key = block.page_order or block.page
            if page_key != current_page:
                current_page = page_key
                row_used = 0

            span = block.layout.col_span or 1

            if span > grid:
                raise ValidationError(f'Bloco "{block.title}" excede as {grid} colunas.')

            if row_used + span > grid:
                row_used = 0

            row_used += span
