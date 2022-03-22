import pickle
import pprint

from s2and.data import Signature, Paper
pp = pprint.PrettyPrinter(indent=2)
from lib.log import logger

from mongoconn import dbconn
from lib.s2and_data import load_name_tuples, normalize_signatures_papers, load_name_counts

def normalize():
    paper_coll = dbconn.paper
    signature_coll = dbconn.signatures

    ## TODO make sure this iterates over all un-normalized papers in collection
    papers = [(paper['paper_id'],  paper) for paper in paper_coll.find(
        {},
        # projection={"_id": False, "__v": False},
        skip=0,
        limit=3
       )]

    paper_dict = dict(papers)

    signatures = [(sig['signature_id'],  sig) for sig in signature_coll.find(
        {},
        # projection={"_id": False, "__v": False},
        projection={},
        skip=0,
        limit=3
       )]

    signature_dict = dict(signatures)

    logger.info("Loading named Tuples")
    name_tuples = load_name_tuples()
    logger.info(" ... loaded named Tuples")

    logger.info("Loading name counts")
    name_counts = load_name_counts();
    logger.info(" ... loaded name counts")

    logger.info("Normalizing data")
    normal_sigs, normal_papers = normalize_signatures_papers(signature_dict, paper_dict, name_tuples, name_counts)

    # pp.pprint("Papers==============================================")
    keys = list(normal_papers)
    key = keys[0]
    paper0: Paper = normal_papers[key]

    lp = list(paper0)

    pp.pprint(lp)

import sys

if __name__ == '__main__':
    logger.info("Starting...")
    normalize()
    sys.exit()
