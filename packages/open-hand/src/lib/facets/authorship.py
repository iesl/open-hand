from dataclasses import dataclass

from typing import Dict, List, Optional, Tuple, Set

from itertools import groupby
from lib.open_exchange.open_fetch import fetch_notes_for_author, fetch_profile

from lib.predef.alignment import Alignment, Left, OneOrBoth, Right, Both
from lib.predef.listops import ListOps
from lib.predef.typedefs import AuthorID, CatalogID, CatalogType, ClusterID, SignatureID, TildeID
from lib.predef.utils import is_valid_email

from lib.open_exchange.utils import is_tildeid

from lib.shadowdb.shadowdb import getShadowDB
from lib.shadowdb.profiles import ProfileStore

from lib.shadowdb.data import (
    MentionClustering,
    MentionRecords,
    SignedPaper,
    SignatureRec,
    mention_records_from_note,
)


@dataclass
class CatalogEntry:
    signed_paper: SignedPaper
    secondary_catalog: Optional[CatalogID]


@dataclass
class AggregateAuthorship:
    primary_catalog: CatalogID
    entries: List[CatalogEntry]


@dataclass
class AuthorCatalog:
    """Authorship info, including names, papers, emails
    When built from OpenReview API, it reflects information contained
    in the user's profile, plus all known papers by the author.
    """

    signed_papers: List[SignedPaper]
    usernames: List[AuthorID]
    id: CatalogID
    type: CatalogType


class CatalogGroup:
    catalogs: Dict[CatalogID, AuthorCatalog]

    def __init__(self, catalogs: List[AuthorCatalog]):
        self.catalogs = dict([(c.id, c) for c in catalogs])

    def get_catalogs(self, type: CatalogType) -> List[AuthorCatalog]:
        return [cat for cat in self.catalogs.values() if cat.type == type]

    def get_aggregate_authorship(self, catalog: AuthorCatalog) -> AggregateAuthorship:
        entries: Dict[SignatureID, CatalogEntry] = {}
        primary_catalog = catalog.id
        for signed_paper in catalog.signed_papers:
            other_catalog: Optional[CatalogID] = None
            for catid, cat in self.catalogs.items():
                if catid != catalog.id and signed_paper in cat.signed_papers:
                    other_catalog = catid

            entry = CatalogEntry(signed_paper, other_catalog)
            entries[signed_paper.signatureId()] = entry

        # Include papers from catalogs with author ids that match the initial catalog
        for other_cat_id, other_cat in self.catalogs.items():
            if other_cat_id != catalog.id and ListOps.has_intersection(catalog.usernames, other_cat.usernames):
                for signed_paper in other_cat.signed_papers:
                    if signed_paper.signatureId() not in entries:
                        entry = CatalogEntry(signed_paper, other_cat_id)
                        entries[signed_paper.signatureId()] = entry

        return AggregateAuthorship(primary_catalog, list(entries.values()))


def get_predicted_clustering(init: MentionRecords) -> MentionClustering:
    def sortkey_by_cluster(s: SignatureRec):
        return s.cluster_id if s.cluster_id is not None else "<unclustered>"

    paperlist = init.get_papers()
    print(f"get_predicted_clustering count={len(paperlist)}")

    grouped = groupby(init.get_signatures(), sortkey_by_cluster)

    cluster_groups: Dict[str, List[SignatureRec]] = dict([(id, list(grp)) for id, grp in grouped])

    cluster_ids = list(cluster_groups)

    mentions = getShadowDB().add_all_referenced_signatures(init)
    clusters: List[Tuple[ClusterID, List[SignedPaper]]] = []

    for id in cluster_ids:
        signedPapers = [SignedPaper.from_signature(mentions, sig) for sig in cluster_groups[id]]
        clusters.append((ClusterID(id), signedPapers))

    clustering = dict(clusters)

    return MentionClustering(mentions, clustering=clustering)


def get_tildeid(profile_store: ProfileStore, openId: str) -> Optional[TildeID]:
    if is_tildeid(openId):
        return openId

    if not is_valid_email(openId):
        return

    maybeProfileId = profile_store.add_profile(openId)
    if maybeProfileId is None:
        return

    return maybeProfileId


def get_signatory_authorids(signedPapers: List[SignedPaper]) -> Set[AuthorID]:
    results: Set[AuthorID] = set()
    for pws in signedPapers:
        prime_sig = pws.primary_signature()
        openId = prime_sig.author_info.openId
        if openId is not None:
            results.add(openId)

    return results


def get_focused_openids(profile_store: ProfileStore, signedPapers: List[SignedPaper]) -> Set[TildeID]:
    results: List[str] = []
    for pws in signedPapers:
        prime_sig = pws.primary_signature()
        openId = prime_sig.author_info.openId
        if openId is not None:
            maybeTildeId = get_tildeid(profile_store, openId)
            if maybeTildeId is not None:
                results.append(maybeTildeId)

    return set(results)


def get_primary_name_variants(signedPapers: List[SignedPaper]) -> Set[str]:
    results: List[str] = []
    for pws in signedPapers:
        prime_sig = pws.primary_signature()
        fullname = prime_sig.author_info.fullname
        results.append(fullname)

    uniq = set(results)
    return uniq


def get_canonical_tilde_ids(profile_store: ProfileStore, cluster: List[SignedPaper]) -> Set[TildeID]:
    openids = get_focused_openids(profile_store, cluster)
    return profile_store.canonicalize_ids(list(openids))


def align_cluster(profile_store: ProfileStore, cluster: List[SignedPaper]) -> Dict[TildeID, Alignment[SignatureID]]:
    canonical_ids = get_canonical_tilde_ids(profile_store, cluster)
    alignments: Dict[TildeID, Alignment[SignatureID]] = dict()
    for tid in canonical_ids:
        a = align_cluster_to_user(profile_store, cluster, tid)
        alignments[tid] = a
    return alignments


def align_cluster_to_user(
    profile_store: ProfileStore, cluster: List[SignedPaper], user_id: TildeID
) -> Alignment[SignatureID]:
    papersWithPrimaryAuthor = profile_store.fetch_signatures_as_signed_papers(user_id)
    signed_papers = papersWithPrimaryAuthor

    print(f"Aligning {user_id} w/{len(signed_papers)} papers to cluster w/{len(cluster)} papers")
    aligned: List[OneOrBoth[SignatureID]] = []
    primary_sigs: List[SignatureRec] = [p.primary_signature() for p in signed_papers]
    primary_sigs_ids: List[SignatureID] = [s.signature_id for s in primary_sigs]
    sig_set: Set[SignatureID] = set(primary_sigs_ids)

    cluster_dict: Dict[SignatureID, SignedPaper] = dict([(c.primary_signature().signature_id, c) for c in cluster])

    for sig_id in cluster_dict:
        if sig_id in sig_set:
            aligned.append(Both.of(sig_id))
        else:
            aligned.append(Left.of(sig_id))

    for sig_id in sig_set:
        if sig_id not in cluster_dict:
            aligned.append(Right.of(sig_id))

    return Alignment(values=aligned)


def fetch_openreview_author_catalog(authorId: AuthorID) -> Optional[AuthorCatalog]:
    open_profile = fetch_profile(authorId)
    if open_profile is None:
        return
    usernames = [name.username for name in open_profile.content.names if name.username is not None]
    usernames.append(open_profile.id)
    usernames = ListOps.uniq(usernames)
    notes = list(fetch_notes_for_author(open_profile.id))
    author_mentions = MentionRecords(papers=dict(), signatures=dict())
    for note in notes:
        note_mention = mention_records_from_note(note)
        author_mentions = author_mentions.merge(note_mention)

    signed_papers: List[SignedPaper] = []
    for signature in author_mentions.get_signatures():
        if signature.author_id in usernames:
            sig = SignedPaper.from_signature(author_mentions, signature)
            signed_papers.append(sig)

    return AuthorCatalog(usernames=usernames, signed_papers=signed_papers, type="OpenReviewProfile", id=authorId)


def get_predicted_author_catalogs(canopystr: str) -> List[AuthorCatalog]:
    canopyMentions = getShadowDB().get_canopy(canopystr)
    clustering: MentionClustering = get_predicted_clustering(canopyMentions)
    catalogs: List[AuthorCatalog] = []
    for index, signed_papers in enumerate(clustering.clustering.values()):
        catalog_id = f"pred#{index}"
        uniq_author_ids = get_signatory_authorids(signed_papers)
        catalog = AuthorCatalog(signed_papers, usernames=list(uniq_author_ids), id=catalog_id, type="Predicted")
        catalogs.append(catalog)

    return catalogs


def fetch_catalogs_for_authors(author_ids: List[AuthorID]) -> List[AuthorCatalog]:
    remaining_ids = [*author_ids]
    fetched_catalogs: List[AuthorCatalog] = []
    while remaining_ids:
        id = remaining_ids.pop()
        cat = fetch_openreview_author_catalog(id)
        if cat:
            catalog_id = f"true#{len(fetched_catalogs)}"
            cat.id = catalog_id
            fetched_catalogs.append(cat)
            for userid in cat.usernames:
                if userid in remaining_ids:
                    remaining_ids.remove(userid)
    return fetched_catalogs


def createCatalogGroupForCanopy(canopystr: str) -> CatalogGroup:
    predicted_catalogs = get_predicted_author_catalogs(canopystr)
    predicted_author_ids: List[AuthorID] = ListOps.uniq(ListOps.flatten([c.usernames for c in predicted_catalogs]))
    true_catalogs: List[AuthorCatalog] = fetch_catalogs_for_authors(predicted_author_ids)

    return CatalogGroup([*predicted_catalogs, *true_catalogs])
