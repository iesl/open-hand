from dataclasses import asdict
from pprint import pprint
from typing import Optional

import click

from lib.shadowdb.loader import populate_shadowdb, shadow_paper_by_id, shadow_profile_by_id

from .utils import validate_slice

from lib.open_exchange.open_fetch import (
    get_notes_for_author,
    get_notes_for_dblp_rec_invitation,
    get_profile,
    get_profiles,
)
from lib.predef.typedefs import Slice

from lib.shadowdb.data import mention_records_from_notes

from .cli_base import cli


@cli.group()
def orx():
    """OpenReview exchange; interact with REST API"""


@orx.group()
def get():
    """OpenReview exchange; fetch notes"""


@get.command("author")
@click.argument("authorid", type=str)
def author(authorid: str):

    notes = list(get_notes_for_author(authorid))
    print(f"{authorid} note count: {len(notes)}")

    profile = get_profile(authorid)
    if profile is None:
        print(f"No Profile for {authorid}")
    else:
        d = asdict(profile)
        pprint(d)

    sortedNotes = sorted(notes, key=lambda n: n.id)

    mentionRecords = mention_records_from_notes(notes)

    print(f"{authorid} mention count: paper={len(mentionRecords.papers)}, signatures={len(mentionRecords.signatures)}")

    for idx, n in enumerate(sortedNotes):
        id = n.id
        content = n.content
        title = content.title
        authors = content.authors
        authorstr = ", ".join(authors)
        print(f"{idx+1} {title}  ({id})")
        print(f"  {authorstr}")


@get.command()
@click.option("--slice", type=(int, int), callback=validate_slice)
def profiles(slice: Slice):
    profiles = get_profiles(slice=slice)
    for p in profiles:
        names = p.content.names
        print(f"Profile: {names}")


@get.command()
@click.option("--brief", is_flag=True)
@click.option("--slice", type=(int, int), default=None, callback=validate_slice)
def notes(brief: bool, slice: Optional[Slice]):
    if slice:
        print(f"Fetching Notes {slice}")
    else:
        print(f"Fetching All Notes")

    notes = get_notes_for_dblp_rec_invitation(slice=slice)
    for note in notes:
        if brief:
            print(f"{note.id} #{note.number}: {note.content.title}")
        else:
            pprint(asdict(note))


@orx.group()
def shadowdb():
    """Create/Update shadow database for OpenReview notes/profiles"""


@shadowdb.command("paper")
@click.argument("id", type=str)
def paper(id: str):
    shadow_paper_by_id(id)


@shadowdb.command("profile")
@click.argument("id", type=str)
def shadowdb_profile(id: str):
    shadow_profile_by_id(id)


@shadowdb.command("update")
@click.option("--slice", type=(int, int), default=None, callback=validate_slice)
def shadowdb_populate(slice: Optional[Slice]):
    populate_shadowdb(slice)
