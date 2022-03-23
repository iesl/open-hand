import pprint

from typing import Dict, List, NamedTuple

from .mongoconn import dbconn

pp = pprint.PrettyPrinter(indent=2)


class CanopyMentions(NamedTuple):
    papers: Dict[str, object]
    signatures: Dict[str, object]


def get_canopy_strs() -> List[str]:
    distinct_canopies = dbconn.command({"distinct": "signatures", "key": "author_info.block"})
    canopies = distinct_canopies["values"]
    return canopies


def get_canopy(canopystr: str) -> CanopyMentions:
    signature_coll = dbconn.signatures

    sig_canopy = [(sig["signature_id"], sig) for sig in signature_coll.find({"author_info.block": {"$eq": canopystr}})]

    sig_canopy_dict = dict(sig_canopy)

    paper_canopy = [
        (p["paper_id"], p)
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
            ]
        )
    ]

    paper_canopy_dict = dict(paper_canopy)

    return CanopyMentions(papers=paper_canopy_dict, signatures=sig_canopy_dict)


def list_canopies(offset: int):
    cstrs = get_canopy_strs()
    slice = cstrs[offset : offset + 15]
    print(f"Total Canopies = {len(cstrs)}")
    for i, s in enumerate(slice):
        print(f"  {i+offset}. {s}")


def show_canopy(offset: int):
    all_canopies = get_canopy_strs()
    canopystr = all_canopies[offset]
    sig_canopy, paper_canopy = get_canopy(canopystr)

    pp.pprint(f"Using Canopy {canopystr}")
    pp.pprint(f"Signatures for {canopystr}")
    pp.pprint(sig_canopy)
    pp.pprint(f"Papers for {canopystr}")
    pp.pprint(paper_canopy)
