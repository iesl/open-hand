from typing import Optional
from lib.predef.typedefs import Slice


from lib.predef.utils import is_valid_email

from lib.open_exchange.note_schemas import Note
from lib.open_exchange.open_fetch import get_note, get_notes_for_author, get_profile, get_profiles
from lib.open_exchange.profile_schemas import Profile

from .data import paperrec_from_note


def putstr(s: str, level: int):
    indented = f"{''.ljust(level*4)}{s}"
    print(indented)


def populate_shadowdb(slice: Optional[Slice]):
    print(f"Populating shadow DB; range = {slice}")
    for profile in get_profiles(slice=slice):
        shadow_profile(profile, level=0)


def shadow_profile(profile: Profile, *, alias: Optional[str] = None, level: int):
    if alias is None:
        putstr(f"+ Profile {profile.id}", level)
    else:
        putstr(f"+ Aliasing Profile {profile.id} as {alias}", level)

    usernames = [name.username for name in profile.content.names if name.username is not None]
    usernames.append(profile.id)
    if alias is not None:
        usernames.append(alias)
    usernames = list(set(usernames))
    putstr(f"  usernames = {', '.join(usernames)}", level)
    # TODO Store uniq usernames as equivalency set

    if alias is not None:
        # if alias is set, just record username/id/email equivalency
        return

    notes = list(get_notes_for_author(profile.id))
    putstr(f"  note count = {len(notes)}", level)
    # TODO will all usernames/aliases return the same list of notes?? check...
    for note in notes:
        shadow_note(note, level=level + 1)


def shadow_note(note: Note, *, level: int):
    """Shadow an openreview note as a PaperRec"""
    putstr(f"+ Note: {note.id}, authors: {note.content.authors}", level)
    paperRec = paperrec_from_note(note)
    # Save paperRec to mongo
    for author in paperRec.authors:
        putstr(f"  - {author.name}; {author.id}", level)
        if author.id is None:
            continue

        if not is_valid_email(author.id):
            continue

        profile = get_profile(author.id)

        if profile is None:
            continue

        shadow_profile(profile, alias=author.id, level=level + 1)


def shadow_paper_by_id(id: str):
    """Shadow an openreview note as a PaperRec"""
    note = get_note(id)
    if note is None:
        print(f"No Paper for id = {id}")
        return

    shadow_note(note, level=0)


def shadow_profile_by_id(id: str):
    profile = get_profile(id)
    if profile is None:
        print(f"No Profile for id = {id}")
        return

    shadow_profile(profile, level=0)
