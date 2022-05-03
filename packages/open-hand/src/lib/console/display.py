from typing import Dict, List, Tuple, Set
import typing as t


from lib.db.database import add_all_referenced_signatures
from lib.orx.profile_store import ProfileStore
from lib.orx.utils import is_tildeid
from lib.predefs.alignment import Alignment, Left, OneOrBoth, Right, Both, separateOOBs
from lib.predefs.typedefs import ClusterID, SignatureID, TildeID
from itertools import groupby
import click

from lib.cli_utils import dim, yellowB


from lib.predefs.data import (
    MentionClustering,
    MentionRecords,
    PaperRec,
    PaperWithPrimaryAuthor,
    SignatureRec,
    SignatureWithFocus,
    AuthorRec,
)


def format_authors(authors: List[AuthorRec], fn: t.Callable[[AuthorRec, int], str]) -> List[str]:
    return [fn(a, i) for i, a in enumerate(authors)]


def format_sig(sig: SignatureWithFocus) -> str:
    ts = "~" if is_tildeid(sig.signature.author_info.openId) else ""
    if sig.has_focus:
        return yellowB(f"{ts}{sig.signature.author_info.fullname}")
    return dim(f"{ts}{sig.signature.author_info.fullname}")


def get_mention_clustering(init: MentionRecords) -> MentionClustering:
    def by_cluster(s: SignatureRec):
        return s.cluster_id if s.cluster_id is not None else "<unclustered>"

    grouped = groupby(init.signatures.values(), by_cluster)

    cluster_groups: Dict[str, List[SignatureRec]] = dict([(id, list(grp)) for id, grp in grouped])

    cluster_ids = list(cluster_groups)

    mentions = add_all_referenced_signatures(init)
    cluster_tuples: List[Tuple[ClusterID, List[PaperWithPrimaryAuthor]]] = []

    for id in cluster_ids:
        sig_zip_papers = [PaperWithPrimaryAuthor.from_signature(mentions, sig) for sig in cluster_groups[id]]
        cluster_tuples.append((ClusterID(id), sig_zip_papers))

    cluster_dict = dict(cluster_tuples)

    return MentionClustering(mentions, clustering=cluster_dict)


def get_primary_tildeids(papersWithSignatures: List[PaperWithPrimaryAuthor]) -> Set[str]:
    results: List[str] = []
    for pws in papersWithSignatures:
        for s in pws.signatures:
            openId = s.signature.author_info.openId
            if s.has_focus and is_tildeid(openId):
                results.append(openId)

    return set(results)


def get_primary_name_variants(papersWithSignatures: List[PaperWithPrimaryAuthor]) -> Set[str]:
    results: List[str] = []
    for pws in papersWithSignatures:
        for s in pws.signatures:
            fullname = s.signature.author_info.fullname
            if s.has_focus:
                results.append(fullname)

    uniq = set(results)
    return uniq


def align_cluster(
    profile_store: ProfileStore, cluster: List[PaperWithPrimaryAuthor]
) -> Dict[TildeID, Alignment[SignatureID]]:
    tildeids = get_primary_tildeids(cluster)
    canonical_ids = profile_store.canonicalize_ids(list(tildeids))
    alignments: Dict[TildeID, Alignment[SignatureID]] = dict()
    for tid in canonical_ids:
        a = align_cluster_to_user(profile_store, cluster, tid)
        alignments[tid] = a
    return alignments


def align_cluster_to_user(
    profile_store: ProfileStore, cluster: List[PaperWithPrimaryAuthor], user_id: TildeID
) -> Alignment[SignatureID]:
    papersWithPrimaryAuthor = profile_store.fetch_signatures_as_pwpa(user_id)
    pwpas = papersWithPrimaryAuthor

    print(f"Aligning {user_id} w/{len(pwpas)} papers to cluster w/{len(cluster)} papers")
    aligned: List[OneOrBoth[SignatureID]] = []
    primary_sigs: List[SignatureRec] = [p.primary_signature() for p in pwpas]
    primary_sigs_ids: List[SignatureID] = [s.signature_id for s in primary_sigs]
    sig_set: Set[SignatureID] = set(primary_sigs_ids)

    cluster_dict: Dict[SignatureID, PaperWithPrimaryAuthor] = dict(
        [(c.primary_signature().signature_id, c) for c in cluster]
    )

    for sig_id in cluster_dict:
        if sig_id in sig_set:
            aligned.append(Both.of(sig_id))
        else:
            aligned.append(Left.of(sig_id))

    for sig_id in sig_set:
        if sig_id not in cluster_dict:
            aligned.append(Right.of(sig_id))

    return Alignment(values=aligned)


def populate_profile_store(mentions: MentionRecords) -> ProfileStore:
    ps = ProfileStore()

    for _, sig in mentions.signatures.items():
        openId = sig.author_info.openId
        if is_tildeid(openId):
            ps.add_profile(openId)

    ps.show_profile_sets()
    return ps


def render_paper(paper: PaperRec):
    title = click.style(paper.title, fg="blue")
    names = [a.author_name for a in paper.authors]
    namestr = ", ".join(names)
    click.echo(f"   {title}")
    click.echo(f"      {namestr}")


def render_pwpa(pwpa: PaperWithPrimaryAuthor):
    title = click.style(pwpa.paper.title, fg="blue")
    sid = pwpa.primary_signature().signature_id
    fmtsigs = [format_sig(sig) for sig in pwpa.signatures]
    auths = ", ".join(fmtsigs)
    click.echo(f"   {title} ({sid})")
    click.echo(f"      {auths}")


def displayMentionsInClusters(mentions: MentionRecords):
    print("Clustering Display")

    clustering = get_mention_clustering(mentions)

    profile_store = ProfileStore()

    for cluster_id in clustering.cluster_ids():
        cluster = clustering.cluster(cluster_id)

        names = get_primary_name_variants(cluster)
        namestr = ", ".join(names)

        click.echo(f"Cluster for {namestr}")

        alignments = align_cluster(profile_store, cluster)
        displayed_sigs: Set[SignatureID] = set()
        ubermentions = profile_store.allMentions

        for _, aligned in alignments.items():
            ls, rs, bs = separateOOBs(aligned.values)

            print("Papers Only In Cluster")
            for sig_id in ls.value:
                sig = ubermentions.signatures[sig_id]
                displayed_sigs.add(sig_id)
                pwpa = PaperWithPrimaryAuthor.from_signature(ubermentions, sig)
                render_pwpa(pwpa)

            print("Papers in Both Profile and Cluster")
            for sig_id in bs.value:
                sig = ubermentions.signatures[sig_id]
                displayed_sigs.add(sig_id)
                pwpa = PaperWithPrimaryAuthor.from_signature(ubermentions, sig)
                render_pwpa(pwpa)

            print("Papers Only In Profile")
            for sig_id in rs.value:
                sig = ubermentions.signatures[sig_id]
                displayed_sigs.add(sig_id)
                pwpa = PaperWithPrimaryAuthor.from_signature(ubermentions, sig)
                render_pwpa(pwpa)

        print("Unaligned Papers")
        for pws in cluster:
            if pws.primary_signature().signature_id not in displayed_sigs:
                render_pwpa(pws)


        click.echo("\n")
