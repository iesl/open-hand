from pprint import pprint
from marshmallow import fields, post_load
from dataclasses import dataclass

from typing import Any, List, Optional, Union
from lib.orx.schemas import PartialSchema

from lib.predefs.data import BoolField, OptIntField, OptStringField, StrField, IntField
StartField = fields.Raw(allow_none=True)
EndField = fields.Raw(allow_none=True)

@dataclass
class StartEnd:
    start: Optional[Union[int, str]]
    end: Optional[Union[int, str]]


@dataclass
class ExpertiseTimeline(StartEnd):
    keywords: List[str]


class ExpertiseTimelineSchema(PartialSchema):
    start = StartField
    end = EndField
    keywords = fields.List(StrField)

    # @post_load
    # def make(self, data: Any, **_) -> ExpertiseTimeline:
    #     return ExpertiseTimeline(**data)


@dataclass
class InstitutionRec:
    domain: str
    name: str


class InstitutionRecSchema(PartialSchema):
    domain = StrField
    name = StrField


@dataclass
class InstitutionTimeline:
    start = StartField
    end = EndField
    start = fields.Raw()
    end = fields.Raw()
    institution: List[InstitutionRec]
    position: str


class InstitutionTimelineSchema(PartialSchema):
    start = StartField
    end = EndField
    institution = fields.Nested(InstitutionRecSchema)
    position = StrField


@dataclass
class NameEntry:
    first: Optional[str]
    last: str
    middle: Optional[str]
    preferred: bool
    username: str


class NameEntrySchema(PartialSchema):
    first = OptStringField
    last = StrField
    middle = OptStringField
    preferred = BoolField
    username = StrField


@dataclass
class PersonalRelation:
    start = StartField
    end = EndField
    email: Optional[str]
    name: str
    relation: str


class PersonalRelationSchema(PartialSchema):
    start = StartField
    end = EndField
    email = OptStringField
    name = StrField
    relation = StrField


@dataclass
class ProfileContent:
    dblp: str
    emails: List[str]
    emailsConfirmed: List[str]
    expertise: List[ExpertiseTimeline]
    gender: str
    gscholar: str
    history: List[InstitutionTimeline]
    homepage: str
    linkedin: str
    names: List[NameEntry]
    preferredEmail: str
    # relations: List[PersonalRelation]
    wikipedia: str


class ProfileContentSchema(PartialSchema):
    dblp = StrField
    emails = fields.List(StrField)
    emailsConfirmed = fields.List(StrField)
    expertise = fields.List(fields.Nested(ExpertiseTimelineSchema))
    gender = StrField
    gscholar = StrField
    history = fields.List(fields.Nested(InstitutionTimelineSchema))
    homepage = StrField
    linkedin = StrField
    names = fields.List(fields.Nested(NameEntrySchema))
    preferredEmail = StrField
    relations = fields.List(fields.Nested(PersonalRelationSchema))
    wikipedia = StrField


@dataclass
class Profile:
    content: ProfileContent
    id: str
    # active: bool
    # ddate: None
    # tauthor: OpenReview.net
    # tcdate: 1486666808284
    # tddate: None
    # tmdate: 1521264752605
    # invitation: str
    # nonreaders: []
    # password: True
    # readers: [OpenReview.net ~Martin_Zinkevich1]
    # signatures: [~Martin_Zinkevich1]
    # writers: [OpenReview.net]}


class ProfileSchema(PartialSchema):
    id = StrField
    content = fields.Nested(ProfileContentSchema)


def load_profile(data: Any) -> Profile:
    try:
        p: Profile = ProfileSchema().load(data)
        return p
    except:
        print("Error loading data")
        pprint(data)
        raise
