import re
from typing import Any, Optional, List
from bibtexparser.bibdatabase import BibDatabase
from typing import Any, List, Optional, Dict
from . import logger as log

TILDE_ID_RE = re.compile("^~.+\\d$")

def is_tildeid(id: str) -> bool:
    return TILDE_ID_RE.match(id) is not None


def opt_entry(key: str, content: Any, bibdb: Optional[BibDatabase]) -> Optional[Any]:
    if key in content:
        return content[key]

    if bibdb is not None and key in bibdb.entries_dict:
        return bibdb.entries_dict[key]

    return None


def req_entry(key: str, content: Any, bibdb: Optional[BibDatabase]) -> Any:
    value = opt_entry(key, content, bibdb)
    if value is None:
        raise Exception(f"Required field {key} missing")

    return value


def optstr_entry(key: str, content: Any, bibdb: Optional[BibDatabase] = None) -> Optional[str]:
    return opt_entry(key, content, bibdb)


def optint_entry(key: str, content: Any, bibdb: Optional[BibDatabase]) -> Optional[int]:
    return opt_entry(key, content, bibdb)


def str_entry(key: str, content: Any, bibdb: Optional[BibDatabase]) -> str:
    return req_entry(key, content, bibdb)


def list_entry(key: str, content: Any, bibdb: Optional[BibDatabase] = None) -> List[str]:
    return req_entry(key, content, bibdb)


def clean_string_data(data: Dict[str, Any], **keys: bool):

    def validate(key: str, val: Any) -> str:
        if isinstance(val, str):
            return val
        log.warn(f"wrong type {key}='{val}'; setting to 'nil'; data={data}")
        return 'nil'

    for key in keys:
        have_value = key in data
        value = data[key] if have_value else None
        value_required = keys[key]
        # missing_required_key = not have_value and value_required
        # if missing_required_key:
        #     log.warn(f"missing required key '{key}'; setting to 'nil'; data={data}")
        #     data[key] = "nil"
        #     continue

        if value_required:
            data[key] = validate(key, value)
            continue

        have_wrong_type = have_value and not isinstance(data[key], str)
        if have_value and isinstance(data[key], str):
            value = data[key]

            if len(value.strip()) == 0:
                log.warn(f"whitespace-only str: {key}='{value}'; setting to None; data={data}")
                data[key] = None
            # else:
            #     log.warn(f"expected str: {key}='{value}'; data={data}")

    return data
