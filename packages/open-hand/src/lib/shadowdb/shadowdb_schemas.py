
from marshmallow import Schema, fields, EXCLUDE, post_load
from dataclasses import dataclass, asdict

from typing import Any, Dict, List, Optional

# TODO move these defs:
OptStringField = fields.Str(load_default=None)
StrField = fields.Str(allow_none=False)
IntField = fields.Int(allow_none=False)
OptIntField = fields.Int(load_default=None)
BoolField = fields.Bool(allow_none=False)
OptBoolField = fields.Bool()

@dataclass
class AuthorRec:
    author_name: str
    position: int


class AuthorRecSchema(Schema):
    author_name = fields.Str()
    position = fields.Int()

    @post_load
    def make(self, data: Any, **_) -> AuthorRec:
        return AuthorRec(**data)


@dataclass
class PaperRec:
    abstract: Optional[str]
    authors: List[AuthorRec]
    journal_name: Optional[str]
    paper_id: str
    references: List[str]
    title: str
    venue: Optional[str]
    year: Optional[int]


class PaperRecSchema(Schema):
    class Meta(Schema.Meta):
        unknown = EXCLUDE

    abstract = OptStringField
    authors = fields.List(fields.Nested(AuthorRecSchema))
    journal_name = OptStringField
    paper_id = StrField
    references = fields.List(StrField)
    title = StrField
    venue = OptStringField
    year = OptIntField

    @post_load
    def make(self, data: Any, **_) -> PaperRec:
        return PaperRec(**data)


@dataclass
class AuthorInfoBlock:
    affiliations: List[str]
    block: str
    email: Optional[str]
    first: Optional[str]
    fullname: str
    given_block: str
    last: Optional[str]
    middle: Optional[str]
    openId: str
    position: int
    suffix: Optional[str]


class AuthorInfoBlockSchema(Schema):
    class Meta(Schema.Meta):
        unknown = EXCLUDE

    affiliations = fields.List(StrField)
    block = StrField
    email = OptStringField
    first = OptStringField
    fullname = StrField
    given_block = StrField
    last = OptStringField
    middle = OptStringField
    openId = StrField
    position = IntField
    suffix = OptStringField

    @post_load
    def make(self, data: Any, **_) -> AuthorInfoBlock:
        return AuthorInfoBlock(**data)


@dataclass
class SignatureRec:
    author_id: str
    paper_id: str
    signature_id: str
    author_info: AuthorInfoBlock
    cluster_id: Optional[str]


class SignatureRecSchema(Schema):
    class Meta(Schema.Meta):
        unknown = EXCLUDE

    author_id = StrField
    paper_id = StrField
    signature_id = StrField
    author_info = fields.Nested(AuthorInfoBlockSchema)
    cluster_id = OptStringField

    @post_load
    def make(self, data: Any, **_) -> SignatureRec:
        return SignatureRec(**data)


