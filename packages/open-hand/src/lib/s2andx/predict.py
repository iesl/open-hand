from lib.predef.log import logger

from typing import List, Optional, Union

from s2and.model import Clusterer
from s2and.data import ANDData

from lib.shadowdb.data import ClusteringRecord, MentionRecords, papers2dict, signatures2dict
from lib.shadowdb.queries import getQueryAPI
from .model import load_model

from .loaders import DataPreloads, NameCountDict, NameEquivalenceSet, preload_data


def choose_canopy(n: int) -> str:
    return getQueryAPI().get_canopy_strs()[n]


def init_canopy_data(mentions: MentionRecords, pre: DataPreloads):
    signature_dict = mentions.signature_dict()
    paper_dict = mentions.paper_dict()
    name_counts: Union[NameCountDict, bool] = pre.name_counts if pre.name_counts is not None else False
    name_tuples: NameEquivalenceSet = pre.name_tuples if pre.name_tuples is not None else set()
    anddata = ANDData(
        signatures=signature_dict,
        papers=paper_dict,
        name="unnamed",
        mode="inference",  # or 'train'
        block_type="s2",  # or 'original', refers to canopy method 's2' => author_info.block is canopy
        name_tuples=name_tuples,
        load_name_counts=name_counts,
    )
    return anddata


def predict_all(*, commit: bool = True, profile: bool = False):
    model = load_model()
    pre = preload_data(use_name_counts=False, use_name_tuples=True)
    canopies = getQueryAPI().get_canopy_strs()
    for canopy in canopies:
        dopredict(canopy, commit=commit, model=model, pre=pre, profile=profile)


import cProfile, pstats


def dopredict(
    canopy: str, *, commit: bool = False, model: Optional[Clusterer] = None, pre: DataPreloads, profile: bool = False
) -> List[ClusteringRecord]:
    logger.info(f"Clustering canopy '{canopy}', commit = {commit}, profiling={profile}")

    profiler = cProfile.Profile()
    if profile:
        profiler.enable()

    mentions: MentionRecords = getQueryAPI().get_canopy(canopy)
    pcount = len(mentions.papers)
    scount = len(mentions.signatures)
    logger.info(f"Mention counts papers={pcount} / signatures={scount}")

    andData = init_canopy_data(mentions, pre)

    if model is None:
        model = load_model()

    (clustered_signatures, _) = model.predict(andData.get_blocks(), andData)
    cluster_records: List[ClusteringRecord] = []

    for cluster_id, sigids in clustered_signatures.items():
        sigs = [mentions.signatures[sigid] for sigid in sigids]
        papers = [mentions.papers[sig.paper_id] for sig in sigs]
        rec = ClusteringRecord(
            cluster_id=cluster_id,
            canopy=canopy,
            mentions=MentionRecords(signatures=signatures2dict(sigs), papers=papers2dict(papers)),
        )
        cluster_records.append(rec)

    if commit:
        logger.info(f"Committing {len(cluster_records)} clusters for {canopy}")
        commit_clusters(cluster_records)

    if profile:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("tottime")
        cname = canopy.replace(" ", "_")
        stats_file = f"canopy_{cname}_n{scount}.prof"
        logger.info(f"Writing stats to {stats_file}")
        stats.dump_stats(stats_file)

    return cluster_records


def commit_clusters(clusters: List[ClusteringRecord]):
    queryAPI = getQueryAPI()
    for c in clusters:
        queryAPI.commit_cluster(c)
