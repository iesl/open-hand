from typing import NamedTuple, Set, Dict, Tuple, Optional, Any

import pickle
import os


StringCountDict = Dict[str, int]
NameCountDict = Dict[str, StringCountDict]

# e.g., {  ("abi", "abigail"), ("abbie", "abigail") ... }
# TODO this can be a much more efficient bimap implementation
NameEquivalenceSet = Set[Tuple[str, str]]

from lib.predef.log import logger

from s2and.consts import PROJECT_ROOT_PATH, NAME_COUNTS_PATH, FASTTEXT_PATH

from s2and.file_cache import cached_path
import fasttext

def load_fasttext_model() -> Optional[Any]:
    return fasttext.load_model(cached_path(FASTTEXT_PATH))

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
    fasttext_model: Any


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
    ftmodel = load_fasttext_model()
    return DataPreloads(name_counts=name_counts, name_tuples=name_tuples, fasttext_model=ftmodel)


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
