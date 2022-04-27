from typing import Dict, Iterator, Union
import openreview
from openreview import Client, Note
from openreview.tools import iterget_notes

from lib import get_config


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
