import pickle
from os.path import join

from s2and.model import Clusterer
from lib.log import logger

from s2and.consts import CONFIG

MAIN_DATA_DIR = CONFIG["main_data_dir"]

# modeldir = join(PROJECT_ROOT_PATH, os.pardir, "s2and-model")
model_file = join(MAIN_DATA_DIR, "production_model.pickle")

logger.info(f"Using model files in data dir {MAIN_DATA_DIR}")

def load_model() -> Clusterer:
    with open(model_file, "rb") as _pkl_file:
        clusterer = pickle.load(_pkl_file)
        cl: Clusterer = clusterer["clusterer"]
        cl.use_cache = False
        return cl
