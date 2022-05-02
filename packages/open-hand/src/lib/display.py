from dataclasses import asdict
from typing import Dict, List, Tuple, Set, cast
import typing as t

from pprint import pprint

from openreview.openreview import Note
from lib.db.database import add_all_referenced_signatures
from lib.orx.open_exchange import get_notes_for_author, mention_records_from_note, mention_records_from_notes
from lib.orx.profile_store import ProfileStore
from lib.orx.utils import is_tildeid
from lib.predefs.alignment import Alignment, Left, OneOrBoth, Right, Both
from lib.predefs.typedefs import ClusterID
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
    mergeMentions,
)


def format_authors(authors: List[AuthorRec], fn: t.Callable[[AuthorRec, int], str]) -> List[str]:
    return [fn(a, i) for i, a in enumerate(authors)]


def format_sig(sig: SignatureWithFocus) -> str:
    if sig.has_focus:
        return yellowB(f"{sig.signature.author_info.fullname}")
    return dim(f"{sig.signature.author_info.fullname}")


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


def diff_cluster_with_known_papers(cluster: List[PaperWithPrimaryAuthor]):
    tildeids = get_primary_tildeids(cluster)
    for id in tildeids:
        notes = get_notes_for_author(id)
        for note in notes:
            title = note.content.title
            noteId = note.id


def align_cluster(profile_store: ProfileStore, cluster: List[PaperWithPrimaryAuthor]) -> Dict[str, Alignment[str]]:
    tildeids = get_primary_tildeids(cluster)
    canonical_ids = profile_store.canonicalize_ids(list(tildeids))
    alignments: Dict[str, Alignment[str]] = dict()
    for id in canonical_ids:
        a = align_cluster_to_user(cluster, id)
        alignments[id] = a
    return alignments


def align_cluster_to_user(cluster: List[PaperWithPrimaryAuthor], user_id: str) -> Alignment[str]:
    author_notes = list(get_notes_for_author(user_id))
    print(f"Aligning {user_id} w/{len(author_notes)} papers to cluster w/{len(cluster)} papers")
    aligned: List[OneOrBoth[str]] = []
    note_dict: Dict[str, Note] = dict([(cast(str, n.id), n) for n in author_notes])
    cluster_dict = dict([(c.paper.paper_id, c) for c in cluster])
    for c in cluster:
        paper_id = c.paper.paper_id
        if paper_id in note_dict:
            aligned.append(Both.of(paper_id))
        else:
            aligned.append(Left.of(paper_id))

    for n in author_notes:
        paper_id: str = n.id
        if paper_id not in cluster_dict:
            aligned.append(Right.of(paper_id))

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


def displayMentionsInClusters(mentions: MentionRecords):
    clustering = get_mention_clustering(mentions)
    print("Clustering")

    profile_store = populate_profile_store(clustering.mentions)

    # Add all referenced mention in profile store to MentionRecords

    print(f"Profile Notes")
    profile_ids = profile_store.get_all_ids()
    ubermentions = clustering.mentions

    for profile_id in profile_ids:
        author_notes = get_notes_for_author(profile_id)
        notelist = list(author_notes)
        m2s = mention_records_from_notes(notelist)
        ubermentions = mergeMentions(ubermentions, m2s)

    print(f"End/ Profile Notes")

    for cluster_id in clustering.cluster_ids():
        cluster = clustering.cluster(cluster_id)
        tildeids = get_primary_tildeids(cluster)
        canonical_ids = profile_store.canonicalize_ids(list(tildeids))

        names = get_primary_name_variants(cluster)
        tildeidsstr = ", ".join(tildeids)
        namestr = ", ".join(names)
        click.echo(f"Cluster for {namestr}")
        click.echo(f"  Known ids: {tildeidsstr}")
        for pws in cluster:
            title = click.style(pws.paper.title, fg="blue")
            fmtsigs = [format_sig(sig) for sig in pws.signatures]
            auths = ", ".join(fmtsigs)
            click.echo(f"   {title}")
            click.echo(f"      {auths}")

        alignments = align_cluster(profile_store, cluster)
        click.echo("Alignments")
        for userid, aligned in alignments.items():
            pprint(userid)
            pprint(aligned)
            for align in aligned.values:
                if isinstance(align, Left):
                    paper_only_in_cluster = align.value
                    paper_rec = ubermentions.papers[paper_only_in_cluster]
                    print("Left: Only In Cluster")
                    render_paper(paper_rec)
                elif isinstance(align, Right):
                    paper_only_in_profile = align.value
                    paper_rec = ubermentions.papers[paper_only_in_profile]
                    print("Right: Only In Profile")
                    render_paper(paper_rec)
                elif isinstance(align, Both):
                    paper_in_both = align.value
                    paper_rec = ubermentions.papers[paper_in_both]
                    print("Both: In Profile and Cluster")
                    render_paper(paper_rec)

        click.echo("\n")
