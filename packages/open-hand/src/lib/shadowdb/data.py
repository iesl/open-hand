from typing import Any, Dict, List, Tuple
from typing import Any, Optional, List
from dataclasses import dataclass, asdict
from lib.open_exchange.note_schemas import Note
from lib.predef.typedefs import ClusterID

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from pprint import pprint
import re

from lib.open_exchange import loadutil as ld

from .shadowdb_schemas import AuthorRec, PaperRec, AuthorInfoBlock, SignatureRec


@dataclass
class MentionRecords:
    papers: Dict[str, PaperRec]
    signatures: Dict[str, SignatureRec]

    def paper_dict(self) -> Dict[str, Any]:
        return dict([(id, asdict(v)) for id, v in self.papers.items()])

    def signature_dict(self) -> Dict[str, Any]:
        return dict([(id, asdict(v)) for id, v in self.signatures.items()])


@dataclass
class ClusteringRecord:
    mentions: MentionRecords
    prediction_group: str
    cluster_id: str
    canopy: str


@dataclass
class SignatureWithFocus:
    signature: SignatureRec
    has_focus: bool


@dataclass
class PaperWithPrimaryAuthor:
    """A paper with a primary author of interest"""

    paper: PaperRec
    signatures: List[SignatureWithFocus]

    def primary_signature(self) -> SignatureRec:
        for s in self.signatures:
            if s.has_focus:
                return s.signature

        raise Exception(f"Invalid State: No focused signature in paper {self.paper.id}")

    @staticmethod
    def from_signature(mentions: MentionRecords, signature: SignatureRec):
        paper = mentions.papers[signature.paper_id]
        num_authors = len(paper.authors)
        signature_ids = [(f"{paper.id}_{i}", signature.author_info.position == i) for i in range(num_authors)]
        signatures = [SignatureWithFocus(mentions.signatures[id], has_focus) for (id, has_focus) in signature_ids]
        return PaperWithPrimaryAuthor(paper, signatures)


@dataclass
class MentionClustering:
    mentions: MentionRecords
    clustering: Dict[ClusterID, List[PaperWithPrimaryAuthor]]

    def cluster_ids(self) -> List[ClusterID]:
        return list(self.clustering)

    def cluster(self, id: ClusterID) -> List[PaperWithPrimaryAuthor]:
        return self.clustering[id]


def papers2dict(ps: List[PaperRec]) -> Dict[str, PaperRec]:
    return dict([(p.id, p) for p in ps])


def signatures2dict(ps: List[SignatureRec]) -> Dict[str, SignatureRec]:
    return dict([(p.signature_id, p) for p in ps])


def mergeMentions(m1: MentionRecords, m2: MentionRecords) -> MentionRecords:
    p12 = {**m1.papers, **m2.papers}
    s12 = {**m1.signatures, **m2.signatures}
    return MentionRecords(papers=p12, signatures=s12)


def zip_signature_paper_pairs(mentions: MentionRecords) -> List[Tuple[SignatureRec, PaperRec]]:
    ps = mentions.papers
    return [(sig, ps[sig.paper_id]) for _, sig in mentions.signatures.items()]


def paperrec_from_note(note: Note) -> PaperRec:
    try:
        paper_id: str = note.id
        content: Any = asdict(note.content)

        bibdb: Optional[BibDatabase] = None
        bibtex = ld.optstr_entry("_bibtex", content)
        if bibtex is not None:
            bibdb = bibtexparser.loads(bibtex)

        title = ld.str_entry("title", content, bibdb)
        venue = ld.optstr_entry("venue", content, bibdb)
        abstract = ld.optstr_entry("abstract", content, bibdb)
        year = ld.optint_entry("year", content, bibdb)

        authors = ld.list_entry("authors", content)
        author_ids = ld.list_entry("authorids", content)
        authorRecs: List[AuthorRec] = []

        for idx, (id, name) in enumerate(zip(author_ids, authors)):
            authorRecs.append(AuthorRec(name=name, id=id, position=idx))

        prec = PaperRec(
            id=paper_id,
            title=title,
            abstract=abstract,
            authors=authorRecs,
            journal_name=None,
            year=year,
            venue=venue,
            references=[],
        )
        return prec
    except Exception as inst:
        print("Error Converting note to PaperRec")
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        js = asdict(note)
        pprint(js)
        raise


def mention_records_from_note(note: Note) -> MentionRecords:
    recs = MentionRecords(papers=dict(), signatures=dict())
    try:
        prec = paperrec_from_note(note)

        recs.papers[prec.id] = prec

        authorRecs = prec.authors
        # author_ids = prec.authors

        paper_id = prec.id

        for position, authorRec in enumerate(authorRecs):
            ws = re.compile("[ ]+")
            nameParts = ws.split(authorRec.name)
            firstName = nameParts[0]
            lastName = nameParts[-1]
            firstInitial = firstName[0]
            block = f"{firstInitial} {lastName}".lower()
            middleName: Optional[str] = None
            if len(nameParts) > 2:
                middleParts = nameParts[1:-1]
                middleName = " ".join(middleParts)

            openId = authorRec.id
            signature_id = f"{paper_id}_{authorRec.position}"

            aib = AuthorInfoBlock(
                position=position,
                block=block,
                given_block=block,
                openId=openId,
                first=firstName,
                last=lastName,
                middle=middleName,
                suffix=None,
                affiliations=[],
                email=None,
                fullname=authorRec.name,
            )
            sigRec = SignatureRec(
                paper_id=paper_id, author_id=signature_id, signature_id=signature_id, author_info=aib, cluster_id=None
            )

            recs.signatures[signature_id] = sigRec
    except Exception as inst:
        print("Error Converting note to mentions")
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        js = asdict(note)
        pprint(js)

    return recs


def mention_records_from_notes(notes: List[Note]) -> MentionRecords:
    recs = MentionRecords(papers=dict(), signatures=dict())
    for note in notes:
        mrs = mention_records_from_note(note)
        recs = mergeMentions(recs, mrs)

    return recs
