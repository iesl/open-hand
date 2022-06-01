# pyright: reportUnusedImport=false
# pyright: reportUnusedExpression=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false

# Schemas for data fetched from OpenReview via REST Endpoints
# Fetched data is generally loaded and then immediately transformed
#    into formats for local storage and use in the inference engine


from pprint import pprint
from typing import Any, List, Optional, cast
from dataclasses import dataclass

from marshmallow import fields
from marshmallow.decorators import post_load

from lib.predef.schemas import IntField, OptStringField, PartialSchema, StrField


@dataclass
class NoteContent:
    title: str
    authors: List[str]
    authorids: List[str]
    abstract: Optional[str]
    html: Optional[str]
    venue: Optional[str]
    venueid: Optional[str]
    _bibtex: Optional[str]
    paperhash: str


class NoteContentSchema(PartialSchema):
    title = StrField
    authors = fields.List(StrField)
    authorids = fields.List(OptStringField)
    abstract = OptStringField
    html = OptStringField
    venue = OptStringField
    venueid = OptStringField
    _bibtex = OptStringField
    paperhash = StrField

    @post_load
    def make(self, data: Any, **kwargs) -> NoteContent:
        return NoteContent(**data)


@dataclass
class Note:
    id: str
    content: NoteContent
    forum: str
    invitation: str
    number: int
    signatures: List[str]
    # nonreaders: []
    # original: None
    # readers: [everyone]
    # referent: None
    # replyto: None
    # mdate: None
    # ddate: None
    # cdate: 1451606400000
    # tcdate: 1616870329591
    # tmdate: 1617109693871
    # writers: ['dblp.org']}


class NoteSchema(PartialSchema):
    id = StrField
    content = fields.Nested(NoteContentSchema)
    forum = StrField
    invitation = StrField
    number = IntField
    signatures = fields.List(StrField)

    @post_load
    def make(self, data: Any, **kwargs) -> Note:
        return Note(**data)


@dataclass
class Notes:
    notes: List[Note]
    count: int


class NotesSchema(PartialSchema):
    notes = fields.List(fields.Nested(NoteSchema))
    count = IntField

    @post_load
    def make(self, data: Any, **kwargs) -> Notes:
        return Notes(**data)


def load_notes(data: Any) -> Notes:
    try:
        # pyright: ignore
        notes: Notes = cast(Notes, NotesSchema().load(data))
        return notes
    except Exception as inst:
        print(type(inst))  # the exception instance
        print("args", inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        print("data:")
        pprint(data)
        raise
