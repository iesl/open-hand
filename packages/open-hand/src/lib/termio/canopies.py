from typing import Set

import click

from lib.facets.authorship import (
    CatalogGroup,
    align_cluster,
    get_focused_openids,
    get_predicted_clustering,
    get_primary_name_variants
)
from lib.predef.alignment import separateOOBs
from lib.predef.typedefs import SignatureID
from lib.predef.utils import nextnums

from lib.shadowdb.data import MentionClustering, MentionRecords
from lib.shadowdb.profiles import ProfileStore
from lib.shadowdb.shadowdb import getShadowDB
from lib.termio.misc_renders import render_author_catalog, render_signature, render_signed_paper


def list_canopies(offset: int):
    cstrs = getShadowDB().get_canopy_strs()
    slice = cstrs[offset : offset + 15]
    print(f"Total Canopies = {len(cstrs)}")
    for i, s in enumerate(slice):
        print(f"  {i+offset}. {s}")


def list_canopies_counted(offset: int):
    queryAPI = getShadowDB()
    cstrs = queryAPI.get_canopy_strs()
    canopies = [(i, cstr, queryAPI.get_canopy(cstr)) for i, cstr in enumerate(cstrs)]
    counted_canopies = [(i, len(mentions.papers), cstr) for i, cstr, mentions in canopies]
    counted_canopies.sort(reverse=True, key=lambda r: r[1])
    slice = counted_canopies[offset : offset + 15]
    print(f"Total Canopies = {len(cstrs)}")
    for i, n, s in slice:
        print(f" {i+offset}. n={n} '{s}'")

def render_catalog_group(catalogs: CatalogGroup):
    for cat in catalogs.catalogs.values():
        if cat.type == "Predicted":
            click.echo(f"Predicted Author Catalog {cat.id}")
            render_author_catalog(cat);

    for cat in catalogs.catalogs.values():
        if cat.type == "OpenReviewProfile":
            click.echo(f"OpenReview User Catalog {cat.id}")
            render_author_catalog(cat);

def displayMentionsInClusters(mentions: MentionRecords):
    clustering: MentionClustering = get_predicted_clustering(mentions)

    profile_store = ProfileStore()

    for cluster_id in clustering.cluster_ids():
        cluster = clustering.cluster(cluster_id)

        primary_ids = get_focused_openids(profile_store, cluster)
        canonical_ids = profile_store.canonicalize_ids(list(primary_ids))
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

            print("Papers Only In Predicted Cluster")
            for sig_id in ls.value:
                render_signature(sig_id, next(pnum), ubermentions)
                displayed_sigs.add(sig_id)

            print("Papers in Both Profile and Cluster")
            for sig_id in bs.value:
                render_signature(sig_id, next(pnum), ubermentions)
                displayed_sigs.add(sig_id)

            print("Papers Only In Profile")
            for sig_id in rs.value:
                render_signature(sig_id, next(pnum), ubermentions)
                displayed_sigs.add(sig_id)

        print("Unaligned Papers")
        for pws in cluster:
            if pws.primary_signature().signature_id not in displayed_sigs:
                render_signed_paper(pws, next(pnum))

        click.echo("\n")


# def createDisplayableClustering(mentions: MentionRecords):
#     clustering: MentionClustering = get_predicted_clustering(mentions)

#     profile_store = ProfileStore()

#     for cluster_id in clustering.cluster_ids():
#         cluster = clustering.cluster(cluster_id)

#         primary_ids = get_focused_openids(profile_store, cluster)
#         canonical_ids = profile_store.canonicalize_ids(list(primary_ids))
#         idstr = ", ".join(canonical_ids)
#         other_ids = primary_ids.difference(canonical_ids)
#         other_idstr = ", ".join(other_ids)

#         names = list(get_primary_name_variants(cluster))

#         name1 = names[0]
#         namestr = ", ".join(names[1:])

#         click.echo(f"Cluster for {name1}")
#         if len(names) > 1:
#             click.echo(f"  aka {namestr}")

#         if len(canonical_ids) == 0:
#             click.echo(f"  No Valid User ID")
#         elif len(canonical_ids) == 1:
#             if len(other_ids) == 0:
#                 click.echo(f"  id: {idstr}")
#             else:
#                 click.echo(f"  id: {idstr} alts: {other_idstr}")

#         alignments = align_cluster(profile_store, cluster)
#         displayed_sigs: Set[SignatureID] = set()
#         ubermentions = profile_store.allMentions

#         pnum = nextnums()
#         for _, aligned in alignments.items():
#             ls, rs, bs = separateOOBs(aligned.values)

#             print("Papers Only In Predicted Cluster")
#             for sig_id in ls.value:
#                 render_signature(sig_id, next(pnum), ubermentions)
#                 displayed_sigs.add(sig_id)

#             print("Papers in Both Profile and Cluster")
#             for sig_id in bs.value:
#                 render_signature(sig_id, next(pnum), ubermentions)
#                 displayed_sigs.add(sig_id)

#             print("Papers Only In Profile")
#             for sig_id in rs.value:
#                 render_signature(sig_id, next(pnum), ubermentions)
#                 displayed_sigs.add(sig_id)

#         print("Unaligned Papers")
#         for pws in cluster:
#             if pws.primary_signature().signature_id not in displayed_sigs:
#                 render_signed_paper(pws, next(pnum))

#         click.echo("\n")
