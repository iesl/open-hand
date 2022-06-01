from typing import Optional
from lib.predef.listops import ListOps
from lib.predef.typedefs import Slice

from lib.predef.utils import is_valid_email

from lib.open_exchange.note_schemas import Note
from lib.open_exchange.open_fetch import (
    fetch_note,
    fetch_notes_for_author,
    fetch_notes_for_dblp_rec_invitation,
    fetch_profile,
    fetch_profiles,
)

from lib.open_exchange.profile_schemas import Profile

from .queries import getQueryAPI
from .data import mention_records_from_note


def putstr(s: str, level: int):
    indented = f"{''.ljust(level*4)}{s}"
    print(indented)


def populate_shadowdb_from_notes(slice: Optional[Slice]):
    for note in fetch_notes_for_dblp_rec_invitation(slice=slice):
        shadow_note(note, level=0)


def populate_shadowdb_from_profiles(slice: Optional[Slice]):
    print(f"Populating shadow DB; range = {slice}")
    for profile in fetch_profiles(slice=slice):
        shadow_profile(profile, level=0)


def shadow_profile(profile: Profile, *, alias: Optional[str] = None, level: int):
    queryAPI = getQueryAPI()
    if alias is None:
        putstr(f"+ Profile {profile.id}", level)
    else:
        putstr(f"+ Aliasing Profile {profile.id} as {alias}", level)

    usernames = [name.username for name in profile.content.names if name.username is not None]
    usernames.append(profile.id)
    if alias is not None:
        usernames.append(alias)
    usernames = ListOps.uniq(usernames)
    putstr(f"  usernames = {', '.join(usernames)}", level)

    queryAPI.create_equivalence(usernames)

    if alias is not None:
        # if alias is set, just record username/id/email equivalency
        return

    notes = list(fetch_notes_for_author(profile.id))
    putstr(f"  note count = {len(notes)}", level)
    # TODO will all usernames/aliases return the same list of notes?? check...
    for note in notes:
        shadow_note(note, level=level + 1)


def shadow_note(note: Note, *, level: int):
    """Shadow an openreview note as a PaperRec"""

    queryAPI = getQueryAPI()
    putstr(f"+ Note: {note.id}, authors: {note.content.authors}", level)

    mentions = mention_records_from_note(note)

    queryAPI.insert_papers(mentions.get_papers())
    queryAPI.insert_signatures(mentions.get_signatures())

    for paperRec in mentions.get_papers():
        for author in paperRec.authors:
            putstr(f"  - {author.author_name}; {author.id}", level)
            if author.id is None:
                continue

            if not is_valid_email(author.id):
                continue

            profile = fetch_profile(author.id)

            if profile is None:
                continue

            shadow_profile(profile, alias=author.id, level=level + 1)


def shadow_paper_by_id(id: str):
    """Shadow an openreview note as a PaperRec"""
    note = fetch_note(id)
    if note is None:
        print(f"No Paper for id = {id}")
        return

    shadow_note(note, level=0)


def shadow_profile_by_id(id: str):
    profile = fetch_profile(id)
    if profile is None:
        print(f"No Profile for id = {id}")
        return

    shadow_profile(profile, level=0)
