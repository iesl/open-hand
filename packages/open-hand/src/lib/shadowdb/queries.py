import pprint
from typing import Any, Dict, List, Optional, Set, cast

from .data import ClusteringRecord, MentionRecords, papers2dict, signatures2dict

from .mongoconn import MongoDB

from .shadowdb_schemas import (
    PaperRec,
    PaperRecSchema,
    SignatureRec,
    SignatureRecSchema,
    Cluster,
    ClusterSchema,
    Profile,
    ProfileSchema,
    Equivalence,
    EquivalenceSchema,
)

signature_schema = SignatureRecSchema()
cluster_schema = ClusterSchema()
paper_schema = PaperRecSchema()
profile_schema = ProfileSchema()
equiv_schema = EquivalenceSchema()


def load_signature(enc: Any) -> SignatureRec:
    try:
        dec: SignatureRec = cast(SignatureRec, signature_schema.load(enc))
        return dec
    except Exception as inst:
        print(type(inst))  # the exception instance
        print("args", inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        print("data:")
        pprint.pprint(enc)
        raise


def load_paper(enc: Any) -> PaperRec:
    try:
        dec: PaperRec = cast(PaperRec, paper_schema.load(enc))
        return dec
    except Exception as inst:
        print(type(inst))  # the exception instance
        print("args", inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        print("data:")
        pprint.pprint(enc)
        raise


def load_cluster(enc: Any) -> Cluster:
    dec: Cluster = cast(Cluster, cluster_schema.load(enc))
    return dec


class QueryAPI:
    db: MongoDB

    def __init__(self):
        self.db = MongoDB()

    @property
    def papers(self):
        return self.db.papers

    @property
    def signatures(self):
        return self.db.signatures

    @property
    def clusters(self):
        return self.db.clusters

    @property
    def profiles(self):
        return self.db.profiles

    @property
    def equivalence(self):
        return self.db.equivalence

    def insert_papers(self, papers: List[PaperRec]):
        enc: List[Any] = [paper_schema.dump(p) for p in papers]
        self.papers.insert_many(enc)

    def insert_signatures(self, signatures: List[SignatureRec]):
        enc: List[Any] = [signature_schema.dump(s) for s in signatures]
        self.signatures.insert_many(enc)

    def insert_cluster(self, cluster: Cluster):
        enc: Any = cluster_schema.dump(cluster)
        self.clusters.insert_one(enc)

    def insert_profile(self, profile: Profile):
        enc: Any = profile_schema.dump(profile)
        self.profiles.insert_one(enc)

    def find_equivalence(self, strs: List[str]) -> List[str]:
        cursor = self.equivalence.find({"ids": {"$in": list(strs)}})
        id_sets: List[Equivalence] = [cast(Equivalence, equiv_schema.load(c)) for c in cursor]
        allids: Set[str] = set()
        for ids in id_sets:
            allids = allids.union(set(ids.ids))

        return list(allids)

    def create_equivalence(self, equivs: List[str]) -> List[str]:
        formerEquiv = self.find_equivalence(equivs)
        combined = equivs + formerEquiv
        uniq = list(set(combined))
        newEquiv = Equivalence.of(uniq)
        enc: Any = equiv_schema.dump(newEquiv)

        self.equivalence.delete_many({"ids": {"$in": uniq}})
        self.equivalence.insert_one(enc)
        return self.find_equivalence(newEquiv.ids)

    def get_clusters_for_canopy(self, canopy: str) -> List[ClusteringRecord]:
        cursor = self.clusters.find({"canopy": canopy})

        cluster_ids: List[str] = [c["cluster_id"] for c in cursor]
        cluster_ids: List[str] = list(set(cluster_ids))
        pprint.pp(cluster_ids)
        clusters = [self.get_cluster(c) for c in cluster_ids]

        return clusters

    def add_all_referenced_signatures(self, mentions: MentionRecords) -> MentionRecords:
        paperids = [paper_id for (paper_id, _) in mentions.papers.items()]
        query = self.signatures.find({"paper_id": {"$in": paperids}})
        all_sigs: List[SignatureRec] = [load_signature(sig) for sig in query]

        sigdict = dict([(sig.signature_id, sig) for sig in all_sigs])
        combined_sigdict = mentions.signatures | sigdict
        return MentionRecords(papers=mentions.papers, signatures=combined_sigdict)

    def get_canopied_signatures(self, canopystr: str) -> List[SignatureRec]:
        coll = self.signatures.aggregate(
            [
                {"$match": {"author_info.block": {"$eq": canopystr}}},
                {
                    "$lookup": {
                        "from": "clusters",
                        "localField": "signature_id",
                        "foreignField": "signature_id",
                        "as": "clusters",
                    }
                },
                {"$set": {"cluster": {"$arrayElemAt": ["$clusters", 0]}}},
                {"$set": {"cluster_id": "$cluster.cluster_id"}},
                {"$project": {"_id": 0, "__v": 0, "clusters": 0, "cluster": 0}},
            ]
        )
        signatures: List[SignatureRec] = [load_signature(p) for p in coll]
        return signatures

    def get_canopy(self, canopystr: str) -> MentionRecords:
        sigs = self.get_canopied_signatures(canopystr)
        sig_dict = signatures2dict(sigs)

        coll = self.signatures.aggregate(
            [
                {"$match": {"author_info.block": {"$eq": canopystr}}},
                {"$project": {"_id": 0, "paper_id": 1}},
                {
                    "$lookup": {
                        "from": "papers",
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

        papers: List[PaperRec] = [load_paper(p) for p in coll]

        paper_dict = papers2dict(papers)

        return MentionRecords(papers=paper_dict, signatures=sig_dict)

    def get_canopy_strs(self) -> List[str]:
        distinct_canopies: Dict[str, Any] = self.db.db.command(
            {"distinct": "signatures", "key": "author_info.block"}
        )
        canopies: List[str] = distinct_canopies["values"]
        return canopies

    def get_cluster(self, clusterstr: str) -> ClusteringRecord:
        coll = self.signatures.aggregate(
            [
                {"$match": {"cluster_id": {"$eq": clusterstr}}},
                {"$project": {"_id": 0}},
                {
                    "$lookup": {
                        "from": "signatures",
                        "localField": "signature_id",
                        "foreignField": "signature_id",
                        "as": "signatures",
                    }
                },
                {
                    "$lookup": {
                        "from": "papers",
                        "localField": "signatures.paper_id",
                        "foreignField": "id",
                        "as": "papers",
                    }
                },
            ]
        )

        final_cluster = [p for p in coll]

        # paper_canopy_dict = dict(paper_canopy)

        # pprint.pprint(final_cluster)
        papers = [load_paper(rec["papers"][0]) for rec in final_cluster]
        signatures = [load_signature(rec["signatures"][0]) for rec in final_cluster]
        paperdict = dict([(p.paper_id, p) for p in papers])
        sigdict = dict([(s.signature_id, s) for s in signatures])
        mentions = MentionRecords(papers=paperdict, signatures=sigdict)

        c0 = final_cluster[0]
        cluster_id = c0["cluster_id"]
        canopystr = c0["canopy"]

        return ClusteringRecord(mentions=mentions, cluster_id=cluster_id, canopy=canopystr)

    def commit_cluster(self, cluster: ClusteringRecord):
        cluster_members = [
            dict(
                cluster_id=cluster.cluster_id,
                signature_id=sigid,
                canopy=cluster.canopy,
            )
            for sigid, _ in cluster.mentions.signatures.items()
        ]
        self.clusters.insert_many(cluster_members)


_query_api: Optional[QueryAPI] = None


def getQueryAPI() -> QueryAPI:
    global _query_api
    if _query_api is None:
        _query_api = QueryAPI()
    return _query_api
