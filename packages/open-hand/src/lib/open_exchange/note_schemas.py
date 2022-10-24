# pyright: reportUnusedImport=false
# pyright: reportUnusedExpression=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false

# Schemas for data fetched from OpenReview via REST Endpoints
# Fetched data is generally loaded and then immediately transformed
#    into formats for local storage and use in the inference engine


from array import array
from pprint import pprint
from typing import Any, List, Optional, cast
from dataclasses import dataclass

from marshmallow import fields
from marshmallow.decorators import post_load, pre_load

from lib.predef.schemas import IntField, OptIntField, OptStringField, PartialSchema, StrField
from . import logger as log


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
    paperhash: Optional[str]
    # This field does not exist in OpenReview, but is included as a flag that
    #   there was an error unserializing the record obtained from the OpenReview
    #   REST api
    errors: Optional[str]


class NoteContentSchema(PartialSchema):
    title = StrField
    authors = fields.List(StrField)
    authorids = fields.List(OptStringField)
    abstract = OptStringField
    html = OptStringField
    venue = OptStringField
    venueid = OptStringField
    _bibtex = OptStringField
    paperhash = OptStringField
    errors = OptStringField

    @pre_load
    def clean_input(self, data: Any, many: Any, **kwargs):
        """Filter out any notes that do not have the required fields
        May indicate an error in the OpenReview database, but in any case,
        notes are not useful unless they have certain fields
        """
        valid_title = "title" in data and type(data["title"]) is str
        if not valid_title:
            data["title"] = ""
        valid_authors = "authors" in data and isinstance(data["authors"], list)
        if not valid_authors:
            data["authors"] = []
        valid_authorids = "authorids" in data and isinstance(data["authorids"], list)
        if not valid_authorids:
            data["authorids"] = []
        is_valid = valid_title and valid_authors and valid_authorids

        data["errors"] = None if is_valid else "NoteContentSchema missing required fields"

        return data

    @post_load
    def make(self, data: Any, **kwargs) -> NoteContent:
        try:
            return NoteContent(**data)
        except Exception as ex:
            print("NoteContentSchema Error")
            print(data)
            raise ex


@dataclass
class Note:
    id: str
    content: NoteContent
    forum: str
    invitation: str
    number: Optional[int]
    signatures: List[str]
    ## The Following fields are contained in the Note record, but currently not used
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
    number = OptIntField
    signatures = fields.List(StrField)

    @post_load
    def make(self, data: Any, **kwargs) -> Note:
        try:
            return Note(**data)
        except Exception as ex:
            print("NoteSchema Error")
            print(data)
            raise ex


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
        filtered_notes = [note for note in notes.notes if not note.content.errors]
        notes.notes = filtered_notes

        return notes
    except Exception as inst:
        print(type(inst))  # the exception instance
        print("args", inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        raise
