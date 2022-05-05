from marshmallow import Schema, EXCLUDE, fields


class PartialSchema(Schema):
    class Meta(Schema.Meta):
        unknown = EXCLUDE


OptStringField = fields.Str(load_default=None)
StrField = fields.Str(allow_none=False)
IntField = fields.Int(allow_none=False)
OptIntField = fields.Int(load_default=None)
BoolField = fields.Bool(allow_none=False)
OptBoolField = fields.Bool()
