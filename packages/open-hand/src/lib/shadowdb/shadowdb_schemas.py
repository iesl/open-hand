from marshmallow import Schema, fields, EXCLUDE, post_load
from dataclasses import dataclass

from typing import Any, List, Optional, Set

from lib.predef.schemas import OptBoolField, OptStringField, PartialSchema, StrField, OptIntField, IntField


@dataclass
class AuthorRec:
    author_name: str  # this field name is tied to the name used in the s2and package
    id: Optional[str]
    position: int


class AuthorRecSchema(Schema):
    author_name = StrField
    id = OptStringField
    position = IntField

    @post_load
    def make(self, data: Any, **_) -> AuthorRec:
        return AuthorRec(**data)


@dataclass
class PaperRec:
    # this field name is tied to the name used in the s2and package
    # TODO possibly use @property def paper_id() to just use 'id'
    paper_id: str
    abstract: Optional[str]
    authors: List[AuthorRec]
    journal_name: Optional[str]
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
    openId: Optional[str]
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
    openId = OptStringField
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

    @property
    def foo(self):
        pass


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


@dataclass
class Cluster:
    cluster_id: str
    signature_id: str
    canopy: str


class ClusterSchema(Schema):
    cluster_id = StrField
    signature_id = StrField
    canopy = StrField

    @post_load
    def make(self, data: Any, **_) -> Cluster:
        return Cluster(**data)


@dataclass
class NameEntry:
    first: Optional[str]
    last: str
    middle: Optional[str]
    preferred: Optional[bool]
    username: Optional[str]


class NameEntrySchema(Schema):
    first = OptStringField
    last = StrField
    middle = OptStringField
    preferred = OptBoolField
    username = OptStringField

    @post_load
    def make(self, data: Any, **kwargs) -> NameEntry:
        return NameEntry(**data)


@dataclass
class ProfileContent:
    names: List[NameEntry]


class ProfileContentSchema(Schema):
    names = fields.List(fields.Nested(NameEntrySchema))

    @post_load
    def make(self, data: Any, **kwargs) -> ProfileContent:
        return ProfileContent(**data)


@dataclass
class Profile:
    id: str
    content: ProfileContent


class ProfileSchema(Schema):
    id = StrField
    content = fields.Nested(ProfileContentSchema)

    @post_load
    def make(self, data: Any, **kwargs) -> Profile:
        return Profile(**data)


@dataclass
class Equivalence:
    ids: List[str]

    @classmethod
    def of(cls, ids: List[str]) -> "Equivalence":
        return cls(ids)


class EquivalenceSchema(PartialSchema):
    ids = fields.List(StrField)

    @post_load
    def make(self, data: Any, **kwargs) -> Equivalence:
        return Equivalence(**data)


import lib.open_exchange.profile_schemas as oschemas


def convert_profile(oprof: oschemas.Profile) -> Profile:
    content_names: List[NameEntry] = [
        NameEntry(
            first=name.first, middle=name.middle, last=name.last, username=name.username, preferred=name.preferred
        )
        for name in oprof.content.names
    ]
    return Profile(oprof.id, content=ProfileContent(names=content_names))
