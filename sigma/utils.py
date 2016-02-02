from rest_framework import fields

class CurrentUserCreateOnlyDefault:
    is_update = None
    user = None
    def set_context(self, serializer_field):
        self.is_update = serializer_field.parent.instance is not None
        self.user = serializer_field.context['request'].user

    def __call__(self):
        if self.is_update:
            raise fields.SkipField()
        return self.user
