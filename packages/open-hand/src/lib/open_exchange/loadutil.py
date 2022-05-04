from typing import Any, Optional, List
from bibtexparser.bibdatabase import BibDatabase

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
