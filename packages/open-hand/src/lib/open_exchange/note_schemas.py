# Schemas for data fetched from OpenReview via REST Endpoints
# Fetched data is generally loaded and then immediately transformed
#    into formats for local storage and use in the inference engine

from dataclasses import dataclass


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
