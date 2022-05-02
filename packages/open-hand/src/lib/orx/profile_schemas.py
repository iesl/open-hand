from pprint import pprint
from marshmallow import fields
from dataclasses import dataclass

from typing import Any, List, Optional

from marshmallow.decorators import post_load, pre_load
from lib.orx.schemas import PartialSchema

from lib.predefs.data import OptBoolField, OptStringField, StrField

StartField = fields.Int(allow_none=True)
EndField = fields.Int(allow_none=True)


def clean_start_end(data: Any):
    if "start" not in data:
        data["start"] = None

    if "end" not in data:
        data["end"] = None

    start = data["start"]
    end = data["end"]

    if not isinstance(start, int):
        data["start"] = None

    if not isinstance(end, int):
        data["end"] = None
    return data


@dataclass
class ExpertiseTimeline:
    start: Optional[int]
    end: Optional[int]
    keywords: List[str]


class ExpertiseTimelineSchema(PartialSchema):
    start = StartField
    end = EndField
    keywords = fields.List(StrField)

    @pre_load
    def clean(self, data: Any, many: Any, **kwargs):
        return clean_start_end(data)

    @post_load
    def make(self, data: Any, **_) -> ExpertiseTimeline:
        return ExpertiseTimeline(**data)


@dataclass
class InstitutionRec:
    domain: Optional[str]
    name: str


class InstitutionRecSchema(PartialSchema):
    domain = OptStringField
    name = StrField

    @post_load
    def make(self, data: Any, **_) -> InstitutionRec:
        return InstitutionRec(**data)


@dataclass
class InstitutionTimeline:
    start: Optional[int]
    end: Optional[int]
    institution: InstitutionRec
    position: Optional[str]


class InstitutionTimelineSchema(PartialSchema):
    start = StartField
    end = EndField
    institution = fields.Nested(InstitutionRecSchema)
    position = OptStringField

    @pre_load
    def clean(self, data: Any, many: Any, **kwargs):
        return clean_start_end(data)

    @post_load
    def make(self, data: Any, **_) -> InstitutionTimeline:
        return InstitutionTimeline(**data)


@dataclass
class NameEntry:
    first: Optional[str]
    last: str
    middle: Optional[str]
    preferred: Optional[bool]
    username: Optional[str]


class NameEntrySchema(PartialSchema):
    first = OptStringField
    last = StrField
    middle = OptStringField
    preferred = OptBoolField
    username = OptStringField

    @pre_load
    def clean(self, data: Any, many: Any, **kwargs):
        if "preferred" not in data:
            data["preferred"] = False
        if "username" not in data:
            data["username"] = None

        return data

    @post_load
    def make(self, data: Any, **_) -> NameEntry:
        return NameEntry(**data)


@dataclass
class PersonalRelation:
    start: Optional[int]
    end: Optional[int]
    email: Optional[str]
    name: Optional[str]
    relation: str


class PersonalRelationSchema(PartialSchema):
    start = StartField
    end = EndField
    email = OptStringField
    name = OptStringField
    relation = StrField

    @pre_load
    def clean(self, data: Any, many: Any, **kwargs):
        return clean_start_end(data)

    @post_load
    def make(self, data: Any, **_) -> PersonalRelation:
        return PersonalRelation(**data)


@dataclass
class ProfileContent:
    dblp: Optional[str]
    emails: List[str]
    emailsConfirmed: List[str]
    expertise: List[ExpertiseTimeline]
    gender: Optional[str]
    gscholar: Optional[str]
    history: List[InstitutionTimeline]
    homepage: str
    linkedin: Optional[str]
    names: List[NameEntry]
    preferredEmail: Optional[str]
    relations: List[PersonalRelation]
    wikipedia: Optional[str]


class ProfileContentSchema(PartialSchema):
    dblp = OptStringField
    emails = fields.List(StrField)
    emailsConfirmed = fields.List(StrField)
    expertise = fields.List(fields.Nested(ExpertiseTimelineSchema))
    gender = OptStringField
    gscholar = OptStringField
    history = fields.List(fields.Nested(InstitutionTimelineSchema))
    homepage = OptStringField
    linkedin = OptStringField
    names = fields.List(fields.Nested(NameEntrySchema))
    preferredEmail = OptStringField
    relations = fields.List(fields.Nested(PersonalRelationSchema))
    wikipedia = OptStringField

    @pre_load
    def clean_expertise(self, data: Any, many: Any, **kwargs):
        if "expertise" not in data:
            data["expertise"] = []
        if "history" not in data:
            data["history"] = []
        if "preferredEmail" not in data:
            data["preferredEmail"] = None

        return data

    @post_load
    def make(self, data: Any, **_) -> ProfileContent:
        return ProfileContent(**data)


@dataclass
class Profile:
    id: str
    content: ProfileContent
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

    @post_load
    def make(self, data: Any, **_) -> Profile:
        return Profile(**data)


def load_profile(data: Any) -> Profile:
    try:
        p: Profile = ProfileSchema().load(data)
        return p
    except Exception as inst:
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        pprint(data)
        raise
