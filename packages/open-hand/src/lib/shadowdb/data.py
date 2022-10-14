from typing import Any, Dict, List
from typing import Any, Optional, List
from dataclasses import dataclass, asdict
from lib.open_exchange.note_schemas import Note
from lib.predef.typedefs import ClusterID, SignatureID

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from pprint import pprint
import re

from lib.open_exchange import utils as ld
from lib.predef.zipper import Zipper

from .shadowdb_schemas import AuthorRec, PaperRec, AuthorInfoBlock, SignatureRec


## TODO this should probably go in the shadow db section, as it represents the stored tuples,
## not the hydrated versions of the data
@dataclass
class MentionRecords:
    """ Record of all clusterable mentions
    Mentions in this case are Signatures, which
    represent a particular author for a given paper
    """
    papers: Dict[str, PaperRec]
    signatures: Dict[str, SignatureRec]

    def get_papers(self) -> List[PaperRec]:
        return [p for _, p in self.papers.items()]

    def get_signatures(self) -> List[SignatureRec]:
        return [s for _, s in self.signatures.items()]

    def paper_dict(self) -> Dict[str, Any]:
        return dict([(id, asdict(v)) for id, v in self.papers.items()])

    def signature_dict(self) -> Dict[str, Any]:
        return dict([(id, asdict(v)) for id, v in self.signatures.items()])

    def merge(self, m2: "MentionRecords") -> "MentionRecords":
        p12 = {**self.papers, **m2.papers}
        s12 = {**self.signatures, **m2.signatures}
        return MentionRecords(papers=p12, signatures=s12)


@dataclass
class ClusteringRecord:
    mentions: MentionRecords
    cluster_id: str
    canopy: str


@dataclass
class SignedPaper:
    """A paper with a primary author of interest
    """

    paper: PaperRec
    signatures: Zipper[SignatureRec]

    def primary_signature(self) -> SignatureRec:
        return self.signatures.focus

    def signatureId(self) -> SignatureID:
        return self.primary_signature().signature_id

    @staticmethod
    def from_signature(mentions: MentionRecords, signature: SignatureRec) -> "SignedPaper":
        paper = mentions.papers[signature.paper_id]
        num_authors = len(paper.authors)
        focal_signature = signature.author_info.position
        signature_ids = [f"{paper.paper_id}_{i}" for i in range(num_authors)]
        signatures = [mentions.signatures[id] for id in signature_ids]
        sigzips = Zipper.fromList(signatures)
        if sigzips is None:
            raise Exception("")
        zip_to_focus = sigzips.forward(focal_signature)
        if zip_to_focus is None:
            raise Exception("")

        return SignedPaper(paper=paper, signatures=zip_to_focus)


@dataclass
class MentionClustering:
    mentions: MentionRecords
    clustering: Dict[ClusterID, List[SignedPaper]]

    def cluster_ids(self) -> List[ClusterID]:
        return list(self.clustering)

    def cluster(self, id: ClusterID) -> List[SignedPaper]:
        return self.clustering[id]

@dataclass
class DisplayableClustering:
    predicted_clustering: MentionClustering
    ground_clustering: MentionClustering

    # def get_cluster_ids(self) -> List[ClusterID]:
    #     return self.clustering.cluster_ids()

    # def get_canonical_author_id(self, cluster_id: ClusterID):
    #     pass

    # def get_author_id_variants(self, author_id: TildeID):
    #     pass

    # def get_name_variants(self, author_id: TildeID):
    #     pass



def papers2dict(ps: List[PaperRec]) -> Dict[str, PaperRec]:
    return dict([(p.paper_id, p) for p in ps])


def signatures2dict(ps: List[SignatureRec]) -> Dict[str, SignatureRec]:
    return dict([(p.signature_id, p) for p in ps])


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
        note_number = note.number

        for idx, (id, name) in enumerate(zip(author_ids, authors)):
            authorRecs.append(AuthorRec(author_name=name, id=id, position=idx))

        prec = PaperRec(
            paper_id=paper_id,
            note_number=note_number,
            title=title,
            abstract=abstract,
            authors=authorRecs,
            journal_name=None,
            year=year,
            venue=venue,
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

        recs.papers[prec.paper_id] = prec

        authorRecs = prec.authors

        paper_id = prec.paper_id

        for position, authorRec in enumerate(authorRecs):
            ws = re.compile("[ ]+")
            nameParts = ws.split(authorRec.author_name)
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
                fullname=authorRec.author_name,
            )
            ## TODO double check author_id
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
        recs = recs.merge(mrs)

    return recs
