from typing import Dict, Set, Tuple
from s2and.data import ANDData
import pickle
import os

from s2and.consts import (
    PROJECT_ROOT_PATH,
    NAME_COUNTS_PATH
)

from s2and.file_cache import cached_path

def load_name_tuples() -> Set[Tuple[str, str]]:
    name_tuples: Set[Tuple[str, str]] = set()
    with open(os.path.join(PROJECT_ROOT_PATH, "data", "s2and_name_tuples.txt"), "r") as f2:  # type: ignore
        for line in f2:
            line_split = line.strip().split(",")  # type: ignore
            name_tuples.add((line_split[0], line_split[1]))

    return name_tuples

debug = True

def load_name_counts() -> Dict[str, Dict[str, int]]:
    counts = {}
    if debug:
        counts["first_dict"] = {}
        counts["last_dict"] = {}
        counts["first_last_dict"] = {}
        counts["last_first_initial_dict"] = {}
    else:
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

## TODO can this be run once for papers, then again for signatures, or does the normalization need the paper data
##    Is it embarrassingly parallel for both papers/signatures?
def normalize_signatures_papers(
        signature_dict,
        paper_dict,
        name_tuples: Set[Tuple[str, str]],
        name_counts: Dict[str, Dict[str, int]]):
    ##
    anddata = ANDData(
        signatures=signature_dict,
        papers=paper_dict,
        name='unnamed',
        mode="inference", # or 'train'
        block_type="s2", # or 'original', refers to canopy method 's2' => author_info.block is canopy
        name_tuples=name_tuples,
        load_name_counts=name_counts
    )

    return (anddata.signatures, anddata.papers)
