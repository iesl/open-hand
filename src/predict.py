
from pprint import pprint
from lib.mongoconn import dbconn
from lib.log import logger
from lib.model import load_model, predict
from lib.canopies import CanopyMentions, get_canopy, get_canopy_strs
from s2and.data import ANDData
import sys
from lib.s2and_data import preloads, setup_s2and_env



def choose_canopy() -> str:
    cstrs = get_canopy_strs()
    return cstrs[0]



def init_canopy_data(mentions: CanopyMentions):
    pre = preloads()
    anddata = ANDData(
        signatures=mentions.signatures,
        papers=mentions.papers,
        name="unnamed",
        mode="inference",  # or 'train'
        block_type="s2",  # or 'original', refers to canopy method 's2' => author_info.block is canopy
        name_tuples=pre.name_tuples,
        load_name_counts=pre.name_counts,
    )
    return anddata


if __name__ == "__main__":
    logger.info("Starting...")

    # canopy = choose_canopy()
    # logger.info(f"Clustering canopy '{canopy}'")
    # mentions = get_canopy(canopy)
    # pcount = len(mentions.papers)
    # scount = len(mentions.signatures)
    # logger.info(f'Mention counts papers={pcount} / signatures={scount}')
    # andData = init_canopy_data(mentions)

    # model = load_model()
    # clusters, dist_mats = model.predict(andData.get_blocks(), andData)
    # pprint(clusters)
    # pprint(dist_mats)
    sys.exit()
