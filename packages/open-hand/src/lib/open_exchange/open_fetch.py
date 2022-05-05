from pprint import pprint
from typing import Any, Iterator, Tuple
from typing import Optional, List

import requests
from requests import Response

import openreview as op

from lib.predef.config import get_config
from lib.predef.iterget import IterGet

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


QueryParms = Any


def get_notes(*, slice: Optional[Tuple[int, int]], **initparams: QueryParms) -> Iterator[Note]:
    client = get_client()

    def _getter(**params: QueryParms) -> List[Note]:
        rawresponse = requests.get(notes_url(), params=params, headers=client.headers)
        response = _handle_response(rawresponse)
        notes = load_notes(response.json())
        return notes.notes

    params = {**initparams}
    params["sort"] = initparams["sort"] if "sort" in initparams else "number:desc"
    iter = IterGet(_getter, **params)
    if slice:
        iter = iter.withSlice(slice[0], slice[1])

    return iter


def get_note(id: str) -> Optional[Note]:
    notes = list(get_notes(slice=None, id=id))
    if len(notes) == 0:
        return None
    if len(notes) > 1:
        logger.warn(f"More than one Note returned when fetching Note {id}")
    return notes[0]


def get_notes_for_dblp_rec_invitation(*, slice: Optional[Tuple[int, int]], **kwds: QueryParms) -> Iterator[Note]:
    return get_notes(slice=slice, invitation="dblp.org/-/record", **kwds)


def get_notes_for_author(authorid: str) -> Iterator[Note]:
    return get_notes(slice=None, content={"authorids": authorid})


def get_profile(user_id: str) -> Optional[Profile]:
    client = get_client()
    try:
        pjson = client.get_profile(user_id).to_json()
        profile = load_profile(pjson)
        return profile
    except op.OpenReviewException:
        return None


def get_profiles(offset: int, limit: int) -> List[Profile]:
    client = get_client()
    ## TODO use IterGet/slice rather than query params
    params = {"offset": offset, "limit": limit, "invitation": "~/-/profiles"}
    print("Params")
    pprint(params)
    rawresponse = requests.get(profiles_url(), params=params, headers=client.headers)
    response = _handle_response(rawresponse)
    profiles = [load_profile(p) for p in response.json()["profiles"]]
    return profiles
