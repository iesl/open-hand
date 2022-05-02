from pprint import pprint
import re
from typing import Any, Dict, Iterator, Optional, Union, List
from bibtexparser.bibdatabase import BibDatabase
import openreview
from openreview import Client, Note

# from openreview.openreview import Profile as ORProfile
from openreview.tools import iterget_notes
import requests

from lib import get_config
from lib.orx.profile_schemas import load_profile, Profile
from lib.predefs.data import AuthorInfoBlock, AuthorRec, MentionRecords, PaperRec, SignatureRec, mergeMentions

import bibtexparser


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


def mention_records_from_note(note: Note) -> MentionRecords:
    recs = MentionRecords(papers=dict(), signatures=dict())
    try:
        paper_id: str = note.id
        content: Any = note.content

        bibdb: Optional[BibDatabase] = None
        bibtex = optstr_entry("venue", content)
        if bibtex is not None:
            bibdb = bibtexparser.loads(bibtex)

        title = str_entry("title", content, bibdb)
        venue = optstr_entry("venue", content, bibdb)
        abstract = optstr_entry("abstract", content, bibdb)
        year = optint_entry("year", content, bibdb)

        authors = list_entry("authors", content)
        author_ids = list_entry("authorids", content)
        signature_ids: List[str] = []
        authorRecs: List[AuthorRec] = []

        for idx, (id, name) in enumerate(zip(author_ids, authors)):
            signature_ids.append(f"{paper_id}_{idx}")
            authorRecs.append(AuthorRec(author_name=name, position=idx))

        prec = PaperRec(
            paper_id=paper_id,
            title=title,
            abstract=abstract,
            authors=authorRecs,
            journal_name=None,
            year=year,
            venue=venue,
            references=[],
        )

        recs.papers[paper_id] = prec

        for position, authorRec in enumerate(authorRecs):
            ws = re.compile("[ ]+")
            nameParts = ws.split(authorRec.author_name)
            firstName = nameParts[0]
            lastName = nameParts[-1]
            firstInitial = firstName[0]
            block = f"{firstInitial} {lastName}".lower()
            middleName: Optional[str] = None
            if len(nameParts) > 2:
                middleParts = nameParts[1:-1]
                middleName = " ".join(middleParts)

            openId = author_ids[position]
            signature_id = signature_ids[position]

            aib = AuthorInfoBlock(
                position=position,
                block=block,
                given_block=block,
                openId=openId,
                first=firstName,
                last=lastName,
                middle=middleName,
                suffix=None,
                affiliations=[],
                email=None,
                fullname=authorRec.author_name,
            )
            sigRec = SignatureRec(
                paper_id=paper_id, author_id=signature_id, signature_id=signature_id, author_info=aib, cluster_id=None
            )

            recs.signatures[signature_id] = sigRec
    except Exception as inst:
        print("Error Converting note to mentions")
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)  # __str__ allows args to be printed directly,
        js = note.to_json()
        pprint(js)

    return recs


def mention_records_from_notes(notes: List[Note]) -> MentionRecords:
    recs = MentionRecords(papers=dict(), signatures=dict())
    for note in notes:
        mrs = mention_records_from_note(note)
        recs = mergeMentions(recs, mrs)

    return recs


def get_profile(user_id: str) -> Profile:
    client = get_client()
    pjson = client.get_profile(user_id).to_json()
    profile = load_profile(pjson)
    print(f"Profile for {user_id}")
    return profile


def get_profiles_url() -> str:
    config = get_config()
    baseurl = config.openreview.restApi
    return f"{baseurl}/profiles"


def get_profiles(offset: int, limit: int) -> List[Profile]:
    client = get_client()
    params = {"offset": offset, "limit": limit, "invitation": "~/-/profiles"}
    response = requests.get(get_profiles_url(), params=params, headers=client.headers)
    # handled = client.__handle_response(response)
    profiles = [load_profile(p) for p in response.json()["profiles"]]
    return profiles
