from marshmallow import Schema, EXCLUDE

class PartialSchema(Schema):
    class Meta(Schema.Meta):
        unknown = EXCLUDE
