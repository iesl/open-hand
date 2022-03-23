import pickle
from os.path import join
import os

from s2and.consts import (
    PROJECT_ROOT_PATH,
)
from s2and.data import ANDData
from s2and.model import Clusterer

modeldir = join(PROJECT_ROOT_PATH, os.pardir, "s2and-model")
model_file = join(modeldir, "production_model.pickle")


def load_model() -> Clusterer:
    with open(model_file, "rb") as _pkl_file:
        clusterer = pickle.load(_pkl_file)
        cl: Clusterer = clusterer["clusterer"]
        cl.use_cache = False
        return cl


def predict(cl: Clusterer, anddata: ANDData):
    pred_clusters, pred_distance_matrices = cl.predict(anddata.get_blocks(), anddata)

    # clust: Dict[str, List[str]]
    # mats: Dict[str, ndarray[Unknown, Unknown]] | None
