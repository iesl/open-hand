from pprint import pprint
from typing import Dict, Iterator, Union, List
import openreview
from openreview import Client, Note

# from openreview.openreview import Profile as ORProfile
from openreview.tools import iterget_notes
import requests

from lib import get_config
from lib.orx.profile_schemas import load_profile, Profile


def get_client() -> Client:
    config = get_config()
    baseurl = config.openreview.restApi
    username = config.openreview.restUser
    password = config.openreview.restPassword
    client = openreview.Client(baseurl=baseurl, username=username, password=password)

    return client


def get_notes(**kwds: Union[str, Dict[str, str]]):
    client = get_client()
    return iterget_notes(client, **kwds, sort="number:desc")


def get_notes_for_dblp_rec_invitation():
    return get_notes(invitation="dblp.org/-/record")


def get_notes_for_author(authorid: str) -> Iterator[Note]:
    return get_notes(content={"authorids": authorid})


def get_profile(user_id: str) -> Profile:
    client = get_client()
    pjson = client.get_profile(user_id).to_json()
    profile = load_profile(pjson)
    print(f"Profile for {user_id}")
    # pprint(pjson)
    return profile


def get_profiles_url() -> str:
    config = get_config()
    baseurl = config.openreview.restApi
    return f"{baseurl}/profiles"


def get_profiles(offset: int, limit: int) -> List[Profile]:
    client = get_client()
    params = {
        "offset": offset,
        "limit": limit,
        "invitation": "~/-/profiles"
    }
    response = requests.get(get_profiles_url(), params=params, headers=client.headers)
    # handled = client.__handle_response(response)
    profiles = [load_profile(p) for p in response.json()["profiles"]]
    return profiles
