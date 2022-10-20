"""
Create a local database from queries to the OpenReview REST API, mirroring
the data
"""

from typing import Optional
from lib.open_exchange.utils import is_tildeid
from lib.predef.listops import ListOps
from lib.predef.typedefs import AuthorID, Slice

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

from .shadowdb import getShadowDB
from . import shadowdb_schemas as sdb
from .data import mention_records_from_note


def putstr(s: str, level: int):
    indented = f"{''.ljust(level*4)}{s}"
    print(indented)


def populate_shadowdb_from_notes(slice: Optional[Slice]):
    print(f"Populating ShadowDB from Notes {slice}")
    queryAPI = getShadowDB()
    min_num, max_num = queryAPI.get_note_number_range()

    print(f"Recorded note numbers range from {min_num}-{max_num}")

    skipped = 0
    for note in fetch_notes_for_dblp_rec_invitation(slice=slice, newestFirst=False):
        if note.number <= max_num:
            skipped += 1
            continue

        shadow_note(note, level=0)

    print(f"Skipped {skipped} records")


def show_unpopulated_profiles():
    print("Unpopulated Profiles:")
    queryAPI = getShadowDB()
    queryAPI.find_usernames_without_profiles()


def populate_shadowdb_from_profiles(slice: Optional[Slice]):
    print(f"Populating shadow DB; range = {slice}")
    for profile in fetch_profiles(slice=slice):
        shadow_profile(profile, level=0)


def shadow_profile(profile: Profile, level: int):
    queryAPI = getShadowDB()
    putstr(f"+ Profile {profile.id}", level)

    nameentries = [sdb.NameEntry.fromOpenNameEntry(name) for name in profile.content.names]
    shadow_profile = sdb.Profile(id=profile.id, content=sdb.ProfileContent(names=nameentries))
    queryAPI.insert_profile(shadow_profile)

    usernames = [name.username for name in profile.content.names if name.username is not None]
    usernames.append(profile.id)
    usernames = ListOps.uniq(usernames)
    putstr(f"  usernames = {', '.join(usernames)}", level)

    queryAPI.create_equivalence(usernames)


def shadow_profile_greedy(profile: Profile, *, alias: Optional[str] = None, level: int):
    queryAPI = getShadowDB()
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

    queryAPI = getShadowDB()
    putstr(f"+ Note: {note.id}, authors: {note.content.authors}", level)

    if len(note.content.authors) == 0:
        putstr(f"+ Skipping {note.id}, no authors found", level)
        return

    mentions = mention_records_from_note(note)

    queryAPI.insert_papers(mentions.get_papers())
    queryAPI.insert_signatures(mentions.get_signatures())

    for paperRec in mentions.get_papers():
        for author in paperRec.authors:
            putstr(f"  - {author.author_name}; {author.id}", level)
            if author.id is None:
                continue

            is_valid_id = is_tildeid(author.id) or is_valid_email(author.id)

            if not is_valid_id:
                putstr(f"no profile for author {author.author_name}, id={author.id}", level)
                continue

            ## Insert singleton equivalence, to be joined later
            queryAPI.create_equivalence([author.id])


def shadow_note_and_alias(note: Note, *, level: int):
    """Shadow an openreview note as a PaperRec"""

    queryAPI = getShadowDB()
    putstr(f"+ Note: {note.id}, authors: {note.content.authors}", level)

    if len(note.content.authors) == 0:
        putstr(f"+ Skipping {note.id}, no authors found", level)
        return

    mentions = mention_records_from_note(note)

    queryAPI.insert_papers(mentions.get_papers())
    queryAPI.insert_signatures(mentions.get_signatures())

    ## Traverse the authorIDs in the note to profile.
    ## May be tilde-id, email, or search string
    ## e.g., ~Auth_Name1, name@place.com, http://search-string..
    ## We need to look each of these up directly to make sure we
    ## have a complete snapshot of all papers attributed to that author
    for paperRec in mentions.get_papers():
        for author in paperRec.authors:
            putstr(f"  - {author.author_name}; {author.id}", level)
            if author.id is None:
                continue

            do_profile_lookup = is_tildeid(author.id) or is_valid_email(author.id)

            if not do_profile_lookup:
                putstr(f"no profile for author {author.author_name}", level)
                continue

            profile = fetch_profile(author.id)

            if profile is None:
                putstr(f"no profile found for author {author.author_name}, {author.id}", level)
                continue

            shadow_profile_greedy(profile, alias=author.id, level=level + 1)


def shadow_paper_by_id(id: str):
    """Shadow an openreview note as a PaperRec"""
    note = fetch_note(id)
    if note is None:
        print(f"No Paper for id = {id}")
        return

    shadow_note(note, level=0)


def shadow_profile_by_id(id: AuthorID):
    profile = fetch_profile(id)
    if profile is None:
        print(f"No Profile for id = {id}")
        return

    shadow_profile(profile, level=0)
