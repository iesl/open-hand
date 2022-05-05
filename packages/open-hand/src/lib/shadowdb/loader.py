from dataclasses import asdict
from pprint import pprint
from typing import Optional
from lib.predef.typedefs import Slice


from lib.predef.utils import is_valid_email

from lib.open_exchange.note_schemas import Note
from lib.open_exchange.open_fetch import get_note, get_notes_for_author, get_profile, get_profiles
from lib.open_exchange.profile_schemas import Profile

from .data import paperrec_from_note


def populate_shadowdb(slice: Optional[Slice]):
    print(f"Populating shadow DB; range = {slice}")
    for profile in get_profiles(slice=slice):
        shadow_profile(profile)


def shadow_profile(profile: Profile, *, alias: Optional[str] = None):
    if alias is None:
        print(f"+ Profile {profile.id}")
    else:
        print(f"+ Aliasing Profile {profile.id} as {alias}")

    usernames = [name.username for name in profile.content.names if name.username is not None]
    usernames.append(profile.id)
    if alias is not None:
        usernames.append(alias)
    usernames = list(set(usernames))
    print(f"  usernames = {', '.join(usernames)}")
    # Store uniq usernames as equivalency set

    if alias is not None:
        # if alias is set, just record username/id/email equivalency
        return

    notes = list(get_notes_for_author(profile.id))
    print(f"  note count = {len(notes)}")
    # TODO will all usernames/aliases return the same list of notes?? check...
    for note in notes:
        shadow_note(note)


def shadow_note(note: Note):
    """Shadow an openreview note as a PaperRec"""
    print(f"+ Note: {note.id}, authors: {note.content.authorids}")
    print(f"  + auths: {', '.join(note.content.authors)}")
    paperRec = paperrec_from_note(note)
    # Save paperRec to mongo
    for author in paperRec.authors:
        print(f"    {author.name}; {author.id}")
        if author.id is None:
            continue

        if not is_valid_email(author.id):
            continue

        profile = get_profile(author.id)

        if profile is None:
            continue

        shadow_profile(profile, alias=author.id)


def shadow_paper(id: str):
    """Shadow an openreview note as a PaperRec"""
    note = get_note(id)
    if note is None:
        return

    shadow_note(note)
