class ExpandableSerializerModel:
    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if not request:
            return

        expand = request.query_params.get("expand", "")
        expand_fields = {field.strip() for field in expand.split(",") if field.strip()}

        for field in expand_fields:
            definition = self.expandable_fields.get(field)
            if not definition:
                continue

            if callable(definition):
                self.fields[field] = definition()
            else:
                self.fields[field] = definition
