from dataclasses import asdict
from pprint import pprint
from typing import Any, Iterator, TypeVar
from typing import Optional, List

import requests
from requests import Response

import openreview as op
from requests.sessions import Session

from lib.predef.config import get_config
from lib.predef.iterget import IterGet
from lib.predef.listops import ListOps
from lib.predef.typedefs import Slice
from lib.predef.utils import is_valid_email

from . import logger

from .profile_schemas import Profile, load_profile
from .note_schemas import Note, load_notes


cached_client: Optional[op.Client] = None

def get_client() -> op.Client:
    global cached_client
    if not cached_client:
        config = get_config()
        baseurl = config.openreview.restApi
        username = config.openreview.restUser
        password = config.openreview.restPassword
        cached_client = op.Client(baseurl=baseurl, username=username, password=password)

    return cached_client


cached_session: Optional[Session] = None

def get_session() -> Session:
    global cached_session
    if not cached_session:
        cached_session = requests.Session()
    return cached_session

def resolve_api_url(urlpath: str) -> str:
    config = get_config()
    baseurl = config.openreview.restApi
    return f"{baseurl}/{urlpath}"


def profiles_url() -> str:
    return resolve_api_url("profiles")


def notes_url() -> str:
    return resolve_api_url("notes")


def _handle_response(response: Response) -> Response:
    try:
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPError: {e} {e.args}")
        raise


T = TypeVar("T")


def list_to_optional(ts: List[T]) -> Optional[T]:
    head, tail = ListOps.destructure(ts)
    if len(tail) > 0:
        logger.warn(f"Expected 0 or 1 items, got {len(ts)}")
        for t in ts:
            pprint(asdict(t))

    return head


QueryParms = Any


def _note_fetcher(client: op.Client, **params: QueryParms) -> List[Note]:
    s = get_session()
    rawresponse = s.get(notes_url(), params=params, headers=client.headers)
    response = _handle_response(rawresponse)
    notes = load_notes(response.json())
    return notes.notes


def _fetch_notes(*, slice: Optional[Slice], **initparams: QueryParms) -> Iterator[Note]:
    client = get_client()

    def _fetcher(**params: QueryParms) -> List[Note]:
        return _note_fetcher(client, **params)

    iter = IterGet(_fetcher, **initparams)

    if slice:
        iter = iter.withSlice(slice)

    return iter


def fetch_note(id: str) -> Optional[Note]:
    client = get_client()
    notes = _note_fetcher(client, id=id)
    return list_to_optional(notes)


def fetch_notes_for_dblp_rec_invitation(*, slice: Optional[Slice], newestFirst: bool = True) -> Iterator[Note]:
    sort = "number:desc" if newestFirst else "number:asc"
    return _fetch_notes(slice=slice, invitation="dblp.org/-/record", sort=sort)


def fetch_notes_for_author(authorid: str) -> Iterator[Note]:
    return _fetch_notes(slice=None, **{"content.authorids": authorid})


def profile_fetcher(client: op.Client, **params: QueryParms) -> List[Profile]:
    s = get_session()
    rawresponse = s.get(profiles_url(), params=params, headers=client.headers)
    response = _handle_response(rawresponse)
    profiles = [load_profile(p) for p in response.json()["profiles"]]
    return profiles


def fetch_profile(user_id: str) -> Optional[Profile]:
    client = get_client()
    if is_valid_email(user_id):
        return list_to_optional(profile_fetcher(client, emails=user_id))

    return list_to_optional(profile_fetcher(client, id=user_id))


def fetch_profiles(*, slice: Optional[Slice]) -> Iterator[Profile]:
    client = get_client()

    def _fetcher(**params: QueryParms) -> List[Profile]:
        return profile_fetcher(client, **params)

    params = {"invitation": "~/-/profiles"}
    iter = IterGet(_fetcher, **params)
    if slice:
        iter = iter.withSlice(slice)

    return iter
