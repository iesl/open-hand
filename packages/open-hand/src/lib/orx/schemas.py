from marshmallow import Schema, EXCLUDE
from dataclasses import dataclass


class PartialSchema(Schema):
    class Meta(Schema.Meta):
        unknown = EXCLUDE


@dataclass
class NoteContent:
    pass
    # 'abstract'?: string;
    # html?: string; // this is a URL
    # venueid: string;
    # title: string;
    # authors: string[];
    # authorids: string[];
    # venue: string;
    # _bibtex: string;


@dataclass
class Note:
    pass
    # id: string;
    # content: NoteContent;


@dataclass
class Notes:
    pass
    # notes: Note[];
    # count: number;
