from typing import Optional, List, Iterator

import requests

from openreview import Note
from openreview.openreview import OpenReviewException

from .profile_schemas import Profile, load_profile
from .open_fetch import get_client, get_notes, get_profiles_url


def get_profile(user_id: str) -> Optional[Profile]:
    client = get_client()
    try:
        pjson = client.get_profile(user_id).to_json()
        profile = load_profile(pjson)
        return profile
    except OpenReviewException:
        return None


def get_profiles(offset: int, limit: int) -> List[Profile]:
    client = get_client()
    params = {"offset": offset, "limit": limit, "invitation": "~/-/profiles"}
    response = requests.get(get_profiles_url(), params=params, headers=client.headers)
    # handled = client.__handle_response(response)
    profiles = [load_profile(p) for p in response.json()["profiles"]]
    return profiles


def get_notes_for_dblp_rec_invitation():
    return get_notes(invitation="dblp.org/-/record")


def get_notes_for_author(authorid: str) -> Iterator[Note]:
    return get_notes(content={"authorids": authorid})
