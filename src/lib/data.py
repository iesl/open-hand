from marshmallow import Schema, fields, EXCLUDE, post_load
from dataclasses import dataclass, asdict

from typing import Any, Dict, List, Optional

from marshmallow.utils import _signature

# from s2and.data import Author as S2AuthorNorm, Signature as S2SignatureNorm

OptStringField = fields.Str(allow_none=True)
StrField = fields.Str(allow_none=False)
IntField = fields.Int(allow_none=False)


@dataclass
class AuthorRec:
    author_name: str
    position: int


class AuthorRecSchema(Schema):
    author_name = fields.Str()
    position = fields.Int()

    @post_load
    def make(self, data, **_) -> AuthorRec:
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
    year: int


class PaperRecSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    abstract = OptStringField
    authors = fields.List(fields.Nested(AuthorRecSchema))
    journal_name = OptStringField
    paper_id = StrField
    references = fields.List(StrField)
    title = StrField
    venue = OptStringField
    year = IntField

    @post_load
    def make(self, data, **_) -> PaperRec:
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
    class Meta:
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
    def make(self, data, **_) -> AuthorInfoBlock:
        return AuthorInfoBlock(**data)


@dataclass
class SignatureRec:
    author_id: str
    paper_id: str
    signature_id: str
    author_info: AuthorInfoBlock


class SignatureRecSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    author_id = StrField
    paper_id = StrField
    signature_id = StrField
    author_info = fields.Nested(AuthorInfoBlockSchema)

    @post_load
    def make(self, data, **_) -> SignatureRec:
        return SignatureRec(**data)


@dataclass
class MentionRecords:
    papers: Dict[str, PaperRec]
    signatures: Dict[str, SignatureRec]

    def paper_dict(self) -> Dict[str, Any]:
        return dict([(id, asdict(v)) for id, v in self.papers.items()])

    def signature_dict(self) -> Dict[str, Any]:
        return dict([(id, asdict(v)) for id, v in self.signatures.items()])


@dataclass
class SignatureWithFocus:
    signature: SignatureRec
    has_focus: bool

@dataclass
class PaperWithSignatures:
    paper: PaperRec
    signatures: List[SignatureWithFocus]

def get_paper_with_signatures(mentions: MentionRecords, signature: SignatureRec) -> PaperWithSignatures:
    paper = mentions.papers[signature.paper_id]
    num_authors = len(paper.authors)
    signature_ids = [(f"{paper.paper_id}_{i}", signature.author_info.position==i) for i in range(num_authors)]
    signatures = [SignatureWithFocus(mentions.signatures[id], has_focus) for (id, has_focus) in signature_ids]
    return PaperWithSignatures(paper, signatures)

@dataclass
class ClusteringRecord:
    mentions: MentionRecords
    clustering_id: str
    cluster_id: str
    canopy: str
