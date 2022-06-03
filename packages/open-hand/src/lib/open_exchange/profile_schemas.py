# pyright: reportUnusedImport=false
# pyright: reportUnusedExpression=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false

from pprint import pprint
from marshmallow import fields
from dataclasses import dataclass

from typing import Any, List, Optional, cast, Dict

from marshmallow.decorators import post_load, pre_load
from lib.predef.schemas import PartialSchema

from lib.predef.schemas import OptBoolField, OptStringField, StrField
from . import logger as log

StartField = fields.Int(allow_none=True)
EndField = fields.Int(allow_none=True)


def clean_start_end(data: Any):
    if "start" not in data:
        data["start"] = None

    if "end" not in data:
        data["end"] = None

    start = data["start"]
    end = data["end"]

    if start is not None and not isinstance(start, int):
        log.warn(f"expected int: start={start}; data={data}")
        data["start"] = None

    if end is not None and not isinstance(end, int):
        log.warn(f"expected int: end={end}; data={data}")
        data["end"] = None
    return data


def clean_position(data: Any):
    if "position" in data:
        position = data["position"]
        if not isinstance(position, str):
            log.warn(f"expected str: position={position}; data={data}")
            data["position"] = str(position)

    return data


def clean_strings(data: Any, *keys: str):
    for key in keys:
        if key in data:
            value = data[key]
            if isinstance(value, str):
                if len(value.strip()) == 0:
                    log.warn(f"whitespace str: {key}='{value}'; data={data}")
                    data[key] = None
            else:
                log.warn(f"expected str: {key}='{value}'; data={data}")

    return data


# print(f"Cleaning {key} required={value_required}")

def clean_string_data(data: Dict[str, Any], **keys: bool):

    def validate(key: str, val: Any) -> str:
        if isinstance(val, str):
            return val
        log.warn(f"wrong type {key}='{val}'; setting to 'nil'; data={data}")
        return 'nil'

    for key in keys:
        have_value = key in data
        value = data[key] if have_value else None
        value_required = keys[key]
        # missing_required_key = not have_value and value_required
        # if missing_required_key:
        #     log.warn(f"missing required key '{key}'; setting to 'nil'; data={data}")
        #     data[key] = "nil"
        #     continue

        if value_required:
            data[key] = validate(key, value)
            continue

        have_wrong_type = have_value and not isinstance(data[key], str)
        if have_value and isinstance(data[key], str):
            value = data[key]

            if len(value.strip()) == 0:
                log.warn(f"whitespace-only str: {key}='{value}'; setting to None; data={data}")
                data[key] = None
            # else:
            #     log.warn(f"expected str: {key}='{value}'; data={data}")

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
    def clean(self, data: Any, **kwargs):
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

    @pre_load
    def clean(self, data: Any, many: Any, **kwargs):
        clean_strings(data, "name", "domain")
        return data

    @post_load
    def make(self, data: Any, **kwarg) -> InstitutionRec:
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
        clean_position(data)
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
    def clean(self, data: Any, **kwargs):
        if "preferred" not in data:
            data["preferred"] = False
        if "username" not in data:
            data["username"] = None
        else:
            username = data["username"]
            is_str = isinstance(username, str)
            is_emptystr = is_str and len(username.strip()) == 0

            if not is_str:
                log.warn(f"username is not a str('{username}');  data={data}")

            if is_emptystr:
                log.warn(f"username is an empty str; data={data}")

            if is_emptystr:
                data["username"] = None

        return data

    @post_load
    def make(self, data: Any, **kwargs) -> NameEntry:
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
    def make(self, data: Any, **kwargs) -> PersonalRelation:
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
    def make(self, data: Any, **kwargs) -> ProfileContent:
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
    def make(self, data: Any, **kwargs) -> Profile:
        return Profile(**data)


def load_profile(data: Any) -> Profile:
    try:
        p: Profile = cast(Profile, ProfileSchema().load(data))
        return p
    except Exception as inst:
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        pprint(data)
        raise
