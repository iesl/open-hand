from typing import NamedTuple, Set, Dict, Tuple

import pickle
import os

StringCountDict = Dict[str, int]
NameCountDict = Dict[str, StringCountDict]

# e.g., {  ("abi", "abigail"), ("abbie", "abigail") ... }
# TODO this can be a much more efficient bimap implementation
NameEquivalenceSet = Set[Tuple[str, str]]

from lib.predef.log import logger

from s2and.consts import PROJECT_ROOT_PATH, NAME_COUNTS_PATH

from s2and.file_cache import cached_path


def setup_s2and_env():
    print("In setup_s2and_env()")

    s2and_cache = os.environ.get("S2AND_CACHE")
    project_root_path = os.environ.get("PROJECT_ROOT_PATH")
    print(f"s2and_cache: {s2and_cache}")
    print(f"project_root_path: {project_root_path}")

    try:
        root_path = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
    except NameError:
        root_path = os.path.abspath(os.path.join(os.getcwd()))

    os.environ["S2AND_CACHE"] = os.path.join(root_path, ".feature_cache.d")


class DataPreloads(NamedTuple):
    name_tuples: NameEquivalenceSet
    name_counts: NameCountDict


EMPTY_NAME_COUNTS: NameCountDict = {
    "first_dict": dict(),
    "last_dict": dict(),
    "first_last_dict": dict(),
    "last_first_initial_dict": dict(),
}

EMPTY_NAME_EQUIVS: NameEquivalenceSet = set()


def preload_data(*, use_name_counts: bool, use_name_tuples: bool) -> DataPreloads:
    name_counts: NameCountDict = load_name_counts() if use_name_counts else EMPTY_NAME_COUNTS
    name_tuples = load_name_tuples() if use_name_tuples else EMPTY_NAME_EQUIVS
    return DataPreloads(name_counts=name_counts, name_tuples=name_tuples)


def load_name_tuples() -> NameEquivalenceSet:
    logger.info("Loading named Tuples")
    name_tuples: NameEquivalenceSet = set()
    with open(os.path.join(PROJECT_ROOT_PATH, "data", "s2and_name_tuples.txt"), "r") as f2:  # type: ignore
        for line in f2:
            line_split = line.strip().split(",")  # type: ignore
            name_tuples.add((line_split[0], line_split[1]))

    return name_tuples


def load_name_counts() -> NameCountDict:
    logger.info("Loading name counts")
    counts: NameCountDict = dict()
    with open(cached_path(NAME_COUNTS_PATH), "rb") as f:
        (
            first_dict,
            last_dict,
            first_last_dict,
            last_first_initial_dict,
        ) = pickle.load(f)
        counts["first_dict"] = first_dict
        counts["last_dict"] = last_dict
        counts["first_last_dict"] = first_last_dict
        counts["last_first_initial_dict"] = last_first_initial_dict

    return counts


# from s2and.data import ANDData
## TODO can this be run once for papers, then again for signatures, or does the normalization need the paper data
##    Is it embarrassingly parallel for both papers/signatures?
# def normalize_signatures_papers(signature_dict, paper_dict, pre: DataPreloads):
#     name_counts = pre.name_counts if pre.name_counts is not None else False
#     name_tuples = pre.name_tuples if pre.name_tuples is not None else NameEquivalenceSet()
#     anddata = ANDData(
#         signatures=signature_dict,
#         papers=paper_dict,
#         name="unnamed",
#         mode="inference",  # or 'train'
#         block_type="s2",  # or 'original', refers to canopy method 's2' => author_info.block is canopy
#         name_tuples=name_tuples,
#         load_name_counts=name_counts,
#     )

#     return (anddata.signatures, anddata.papers)
