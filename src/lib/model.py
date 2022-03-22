import pickle
from os.path import join
import os

from fasttext import (
    FastText
)

from s2and.consts import (
    PROJECT_ROOT_PATH,
)
from s2and.data import ANDData

modeldir = join(PROJECT_ROOT_PATH, os.pardir, "s2and-model")
model_file = join(modeldir, "production_model.pickle")

def load_model() -> FastText._FastText:
    with open(model_file, "rb") as _pkl_file:
        clusterer = pickle.load(_pkl_file)
        cl = clusterer['clusterer']
        return cl

def predict(ft: FastText._FastText, anddata: ANDData):
    pred_clusters, pred_distance_matrices = ft.predict(anddata.get_blocks(), anddata)
