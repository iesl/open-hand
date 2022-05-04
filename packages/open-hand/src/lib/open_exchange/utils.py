import re

TILDE_ID_RE = re.compile("^~.+\\d$")

def is_tildeid(id: str) -> bool:
    return TILDE_ID_RE.match(id) is not None
