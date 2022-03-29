import pprint

from typing import List, Tuple

from .mongoconn import dbconn

pp = pprint.PrettyPrinter(indent=2)

from lib.data import ClusteringRecord, MentionRecords, PaperRec, PaperRecSchema, SignatureRec, SignatureRecSchema


def get_canopy_strs() -> List[str]:
    distinct_canopies = dbconn.command({"distinct": "signatures", "key": "author_info.block"})
    canopies = distinct_canopies["values"]
    return canopies


def get_cluster(clusterstr: str) -> ClusteringRecord:
    clusterings_coll = dbconn.clusterings

    final_cluster = [
        p
        for p in clusterings_coll.aggregate(
            [
                {"$match": {"clid": {"$eq": clusterstr}}},
                {"$project": {"_id": 0}},
                {
                    "$lookup": {
                        "from": "signatures",
                        "localField": "sigid",
                        "foreignField": "signature_id",
                        "as": "signatures",
                    }
                },
                {
                    "$lookup": {
                        "from": "paper",
                        "localField": "signatures.paper_id",
                        "foreignField": "paper_id",
                        "as": "papers",
                    }
                },
            ]
        )
    ]

    # paper_canopy_dict = dict(paper_canopy)

    # pprint.pprint(final_cluster)
    papers = [PaperRecSchema().load(rec["papers"][0]) for rec in final_cluster]
    signatures = [SignatureRecSchema().load(rec["signatures"][0]) for rec in final_cluster]
    paperdict = dict([(p.paper_id, p) for p in papers])
    sigdict = dict([(s.signature_id, s) for s in signatures])
    mentions = MentionRecords(papers=paperdict, signatures=sigdict)

    c0 = final_cluster[0]
    cluster_id = c0["clid"]
    clustering_id = c0["id"]
    canopystr = c0["canopy"]

    return ClusteringRecord(mentions=mentions, clustering_id=clustering_id, cluster_id=cluster_id, canopy=canopystr)


def add_all_referenced_signatures(mentions: MentionRecords) -> MentionRecords:
    signature_coll = dbconn.signatures
    paperids = [paper_id for (paper_id, _) in mentions.papers.items()]
    all_sigs: List[SignatureRec] = [
        SignatureRecSchema().load(sig) for sig in signature_coll.find({"paper_id": {"$in": paperids}})
    ]
    sigdict = dict([(sig.signature_id, sig) for sig in all_sigs])
    combined_sigdict = mentions.signatures | sigdict
    return MentionRecords(papers=mentions.papers, signatures=combined_sigdict)


def get_canopy(canopystr: str) -> MentionRecords:
    signature_coll = dbconn.signatures

    sig_canopy: List[Tuple[str, SignatureRec]] = [
        (sig["signature_id"], SignatureRecSchema().load(sig))
        for sig in signature_coll.find({"author_info.block": {"$eq": canopystr}})
    ]

    sig_canopy_dict = dict(sig_canopy)
    # pprint.pprint(f"get_canopy({canopystr})")

    paper_canopy: List[Tuple[str, PaperRec]] = [
        (p["paper_id"], PaperRecSchema().load(p))
        for p in signature_coll.aggregate(
            [
                {"$match": {"author_info.block": {"$eq": canopystr}}},
                {"$project": {"_id": 0, "paper_id": 1}},
                {
                    "$lookup": {
                        "from": "paper",
                        "localField": "paper_id",
                        "foreignField": "paper_id",
                        "as": "fromItems",
                    }
                },
                {
                    "$replaceRoot": {
                        "newRoot": {
                            "$mergeObjects": [
                                {"$arrayElemAt": ["$fromItems", 0]},
                                "$$ROOT",
                            ]
                        }
                    }
                },
                {"$project": {"fromItems": 0}},
                {"$project": {"_id": 0, "__v": 0}},
            ]
        )
    ]

    paper_canopy_dict = dict(paper_canopy)

    return MentionRecords(papers=paper_canopy_dict, signatures=sig_canopy_dict)


def list_canopies(offset: int):
    cstrs = get_canopy_strs()
    slice = cstrs[offset : offset + 15]
    print(f"Total Canopies = {len(cstrs)}")
    for i, s in enumerate(slice):
        print(f"  {i+offset}. {s}")


def list_canopies_counted(offset: int):
    cstrs = get_canopy_strs()
    canopies = [(i, cstr, get_canopy(cstr)) for i, cstr in enumerate(cstrs)]
    counted_canopies = [(i, len(mentions.papers), cstr) for i, cstr, mentions in canopies]
    counted_canopies.sort(reverse=True, key=lambda r: r[1])
    slice = counted_canopies[offset : offset + 15]
    print(f"Total Canopies = {len(cstrs)}")
    for i, n, s in slice:
        print(f" {i+offset}. n={n} '{s}'")


def show_canopy(offset: int):
    all_canopies = get_canopy_strs()
    canopystr = all_canopies[offset]
    # sig_canopy, paper_canopy = get_canopy(canopystr)
    mentions = get_canopy(canopystr)
    papers, signatures = mentions.papers, mentions.signatures

    pp.pprint(f"Using Canopy {canopystr}")
    pp.pprint(f"Signatures for {canopystr}")
    pp.pprint(signatures)
    pp.pprint(f"Papers for {canopystr}")
    pp.pprint(papers)
