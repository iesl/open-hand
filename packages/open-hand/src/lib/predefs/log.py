import logging


def setup(logname: str):
    logger = logging.getLogger(logname)
    logger.setLevel(logging.INFO)
    # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    return logger


def createlogger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(name)s:%(levelname)s] %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    return logger


s2and_logger = logging.getLogger("s2and")
s2and_logger.setLevel("INFO")
s2and_logger.disabled = True

logger = setup("open-coref")
