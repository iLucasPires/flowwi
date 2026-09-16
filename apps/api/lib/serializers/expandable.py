class ExpandableSerializerModel:
    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._expansion_applied = False

    def to_representation(self, instance):
        self._apply_expansion()
        return super().to_representation(instance)

    def _apply_expansion(self):
        """
        Resolves `expand` lazily, at serialization time rather than at __init__.

        A nested expandable serializer (e.g. `assignees` on Task, itself expandable
        via `profile`) is constructed before it's bound to its real parent, so at
        __init__ time `self.context` can't see the request yet. By the time
        to_representation runs, the whole serializer tree is bound and `self.context`
        resolves correctly all the way up, so nested expansions work too.
        """
        if self._expansion_applied:
            return
        self._expansion_applied = True

        request = self.context.get("request")
        if not request:
            return

        expand = request.query_params.get("expand", "")
        expand_fields = {field.strip() for field in expand.split(",") if field.strip()}

        for field in expand_fields:
            definition = self.expandable_fields.get(field)
            if not definition:
                continue

            self.fields[field] = definition() if callable(definition) else definition
