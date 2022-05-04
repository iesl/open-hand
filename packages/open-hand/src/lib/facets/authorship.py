from typing import Dict, List, Optional, Tuple, Set

from itertools import groupby
import click
from email_validator import validate_email, EmailNotValidError

from lib.predef.alignment import Alignment, Left, OneOrBoth, Right, Both, separateOOBs
from lib.predef.typedefs import ClusterID, SignatureID, TildeID
from lib.predef.colors import dim, yellowB
from lib.predef.utils import nextnums

from lib.open_exchange.utils import is_tildeid

from lib.shadowdb.queries import add_all_referenced_signatures
from lib.shadowdb.profiles import ProfileStore

from lib.shadowdb.data import (
    MentionClustering,
    MentionRecords,
    PaperRec,
    PaperWithPrimaryAuthor,
    SignatureRec,
    SignatureWithFocus,
)


def get_mention_clustering(init: MentionRecords) -> MentionClustering:
    def by_cluster(s: SignatureRec):
        return s.cluster_id if s.cluster_id is not None else "<unclustered>"

    paperlist = [p for _, p in init.papers.items()]
    print(f"get_mention_clustering count={len(paperlist)}")
    render_papers(paperlist)

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


def valid_email(s: str) -> bool:
    try:
        validate_email(s).email
        return True
    except EmailNotValidError:
        return False


def get_tildeid(profile_store: ProfileStore, openId: str) -> Optional[TildeID]:
    if is_tildeid(openId):
        return openId

    if not valid_email(openId):
        return

    maybeProfileId = profile_store.add_profile(openId)
    if maybeProfileId is None:
        return

    return maybeProfileId


def get_primary_tildeids(profile_store: ProfileStore, papersWithSignatures: List[PaperWithPrimaryAuthor]) -> Set[str]:
    results: List[str] = []
    for pws in papersWithSignatures:
        for s in pws.signatures:
            openId = s.signature.author_info.openId
            if s.has_focus:
                maybeTildeId = get_tildeid(profile_store, openId)
                print(f"CheckID: {openId} -> {maybeTildeId}")
                if maybeTildeId is not None:
                    equivs = profile_store.get_equivalent_ids(maybeTildeId)
                    print(f"    equivs: {equivs}")
                    results.append(maybeTildeId)

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


def get_canonical_tilde_ids(profile_store: ProfileStore, cluster: List[PaperWithPrimaryAuthor]) -> Set[TildeID]:
    tildeids = get_primary_tildeids(profile_store, cluster)
    return profile_store.canonicalize_ids(list(tildeids))


def align_cluster(
    profile_store: ProfileStore, cluster: List[PaperWithPrimaryAuthor]
) -> Dict[TildeID, Alignment[SignatureID]]:
    canonical_ids = get_canonical_tilde_ids(profile_store, cluster)
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


def format_sig(sig: SignatureWithFocus) -> str:
    ts = "~" if is_tildeid(sig.signature.author_info.openId) else ""
    if sig.has_focus:
        return yellowB(f"{ts}{sig.signature.author_info.fullname}")
    return dim(f"{ts}{sig.signature.author_info.fullname}")


def render_paper(paper: PaperRec):
    title = click.style(paper.title, fg="blue")
    author_names = [f"{p.author_name}" for p in paper.authors]
    auths = ", ".join(author_names)
    id = paper.paper_id
    click.echo(f"{title} ({id})")
    click.echo(f"      {auths}")


def render_papers(papers: List[PaperRec]):
    for p in papers:
        render_paper(p)


def render_pwpa(pwpa: PaperWithPrimaryAuthor, n: int):
    title = click.style(pwpa.paper.title, fg="blue")
    sid = pwpa.primary_signature().signature_id
    fmtsigs = [format_sig(sig) for sig in pwpa.signatures]
    auths = ", ".join(fmtsigs)
    click.echo(f"{n}.   {title} ({sid})")
    click.echo(f"      {auths}")


def displayMentionsInClusters(mentions: MentionRecords):
    clustering = get_mention_clustering(mentions)

    profile_store = ProfileStore()

    for cluster_id in clustering.cluster_ids():
        cluster = clustering.cluster(cluster_id)

        canonical_ids = get_canonical_tilde_ids(profile_store, cluster)

        primary_ids = get_primary_tildeids(profile_store, cluster)
        idstr = ", ".join(canonical_ids)
        other_ids = primary_ids.difference(canonical_ids)
        other_idstr = ", ".join(other_ids)

        names = list(get_primary_name_variants(cluster))

        name1 = names[0]
        namestr = ", ".join(names[1:])

        click.echo(f"Cluster for {name1}")
        if len(names) > 1:
            click.echo(f"  aka {namestr}")

        if len(canonical_ids) == 0:
            click.echo(f"  No Valid User ID")
        elif len(canonical_ids) == 1:
            if len(other_ids) == 0:
                click.echo(f"  id: {idstr}")
            else:
                click.echo(f"  id: {idstr} alts: {other_idstr}")

        alignments = align_cluster(profile_store, cluster)
        displayed_sigs: Set[SignatureID] = set()
        ubermentions = profile_store.allMentions

        pnum = nextnums()
        for _, aligned in alignments.items():
            ls, rs, bs = separateOOBs(aligned.values)

            print("Papers Only In Cluster")
            for sig_id in ls.value:
                sig = ubermentions.signatures[sig_id]
                displayed_sigs.add(sig_id)
                pwpa = PaperWithPrimaryAuthor.from_signature(ubermentions, sig)
                render_pwpa(pwpa, next(pnum))

            print("Papers in Both Profile and Cluster")
            for sig_id in bs.value:
                sig = ubermentions.signatures[sig_id]
                displayed_sigs.add(sig_id)
                pwpa = PaperWithPrimaryAuthor.from_signature(ubermentions, sig)
                render_pwpa(pwpa, next(pnum))

            print("Papers Only In Profile")
            for sig_id in rs.value:
                sig = ubermentions.signatures[sig_id]
                displayed_sigs.add(sig_id)
                pwpa = PaperWithPrimaryAuthor.from_signature(ubermentions, sig)
                render_pwpa(pwpa, next(pnum))

        print("Unaligned Papers")
        for pws in cluster:
            if pws.primary_signature().signature_id not in displayed_sigs:
                render_pwpa(pws, next(pnum))

        click.echo("\n")


def displayMentionsSorted(mentions: MentionRecords):
    print("Mention Display")

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

        pnum = nextnums(0)

        for _, aligned in alignments.items():
            ls, rs, bs = separateOOBs(aligned.values)
            allValues = ls.value + rs.value + bs.value
            sortedValues = sorted(allValues)
            for sig_id in sortedValues:
                sig = ubermentions.signatures[sig_id]
                displayed_sigs.add(sig_id)
                pwpa = PaperWithPrimaryAuthor.from_signature(ubermentions, sig)
                render_pwpa(pwpa, next(pnum))

        print("Unaligned Papers")
        for pws in cluster:
            if pws.primary_signature().signature_id not in displayed_sigs:
                render_pwpa(pws, next(pnum))

        click.echo("\n")
