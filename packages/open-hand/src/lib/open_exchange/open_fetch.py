from dataclasses import asdict
from pprint import pprint
from typing import Any, Iterator, Tuple, TypeVar
from typing import Optional, List

import requests
from requests import Response

import openreview as op

from lib.predef.config import get_config
from lib.predef.iterget import IterGet
from lib.predef.utils import is_valid_email

from . import logger

from .profile_schemas import Profile, load_profile
from .note_schemas import Note, load_notes


def get_client() -> op.Client:
    config = get_config()
    baseurl = config.openreview.restApi
    username = config.openreview.restUser
    password = config.openreview.restPassword
    client = op.Client(baseurl=baseurl, username=username, password=password)

    return client


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
    if len(ts) == 0:
        return None
    if len(ts) > 1:
        logger.warn(f"Expected 0 or 1 items, got {len(ts)}")
        for t in ts:
            pprint(asdict(t))

    return ts[0]


QueryParms = Any


def note_getter(client: op.Client, **params: QueryParms) -> List[Note]:
    rawresponse = requests.get(notes_url(), params=params, headers=client.headers)
    response = _handle_response(rawresponse)
    notes = load_notes(response.json())
    return notes.notes


def get_notes(*, slice: Optional[Tuple[int, int]], **initparams: QueryParms) -> Iterator[Note]:
    client = get_client()

    def _getter(**params: QueryParms) -> List[Note]:
        return note_getter(client, **params)

    iter = IterGet(_getter, **initparams)

    if slice:
        iter = iter.withSlice(slice[0], slice[1])

    return iter


def get_note(id: str) -> Optional[Note]:
    client = get_client()
    notes = note_getter(client, id=id)
    return list_to_optional(notes)


def get_notes_for_dblp_rec_invitation(*, slice: Optional[Tuple[int, int]]) -> Iterator[Note]:
    return get_notes(slice=slice, invitation="dblp.org/-/record", sort="number:desc")


def get_notes_for_author(authorid: str) -> Iterator[Note]:
    return get_notes(slice=None, **{"content.authorids": authorid})


def profile_getter(client: op.Client, **params: QueryParms) -> List[Profile]:
    rawresponse = requests.get(profiles_url(), params=params, headers=client.headers)
    response = _handle_response(rawresponse)
    profiles = [load_profile(p) for p in response.json()["profiles"]]
    return profiles


def get_profile(user_id: str) -> Optional[Profile]:
    client = get_client()
    if is_valid_email(user_id):
        return list_to_optional(profile_getter(client, emails=user_id))

    return list_to_optional(profile_getter(client, id=user_id))


def get_profiles(*, slice: Optional[Tuple[int, int]]) -> Iterator[Profile]:
    client = get_client()

    def _getter(**params: QueryParms) -> List[Profile]:
        return profile_getter(client, **params)

    params = {"invitation": "~/-/profiles"}
    iter = IterGet(_getter, **params)
    if slice:
        iter = iter.withSlice(slice[0], slice[1])

    return iter
