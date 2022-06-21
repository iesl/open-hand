import re
from typing import Any, Optional, List, Union
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


def clean_string_data(data: Dict[str, Any], **keyspec: bool):
    def warn(key: str, info: str):
        m = f"data['{key}'] is {info}; data={data}"
        log.warn(m)

    def sub(key: str, v: Optional[str]):
        data[key] = v

    for key in keyspec:
        is_present = key in data
        is_nullable = keyspec[key]
        value = data[key] if is_present else None
        is_correct_type = isinstance(value, str)
        is_empty_str = isinstance(value, str) and len(value.strip()) == 0
        is_valid = is_present and is_correct_type and not is_empty_str

        if is_valid:
            continue

        if is_nullable:
            sub(key, None)
            continue

        if not is_present:
            warn(key, "required but missing")
        elif not is_correct_type:
            warn(key, "required but wrong type")
        elif is_empty_str:
            warn(key, "required, present, but only whitespace")

        sub(key, None)


def to_int(value: Optional[Union[str, int]], coerceWarning: str) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value

    try:
        return int(value)
    except:
        log.warn(coerceWarning)
        return None


def clean_int_data(data: Dict[str, Any], **keyspec: bool):
    def warn(key: str, info: str):
        m = f"data['{key}'] is {info}; data={data}"
        log.warn(m)

    def sub(key: str, v: Optional[int]):
        data[key] = v

    for key in keyspec:
        is_present = key in data
        is_nullable = keyspec[key]
        value = data[key] if is_present else None
        as_int = to_int(value, f"Failed to coerce data['{key}']={value} to int")
        is_correct_type = as_int is not None

        if is_present and is_correct_type:
            sub(key, as_int)
            continue

        if is_nullable:
            sub(key, None)
            continue

        warn(key, "wrong type")
        sub(key, None)


def set_data_defaults(data: Dict[str, Any], **defaults: Any):
    for key in defaults:
        if key not in data:
            data[key] = defaults[key]
