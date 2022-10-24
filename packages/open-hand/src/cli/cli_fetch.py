from dataclasses import asdict
from pprint import pprint
from typing import Optional

import click

from .utils import validate_slice

from lib.open_exchange.open_fetch import (
    fetch_note,
    fetch_notes_for_author,
    fetch_notes_for_dblp_rec_invitation,
    fetch_profile,
    fetch_profiles,
)
from lib.predef.typedefs import Slice

from lib.shadowdb.data import mention_records_from_notes

from .cli_base import cli


@cli.group()
def fetch():
    """OpenReview fetcher; interact with REST API"""


@fetch.command("author")
@click.argument("authorid", type=str)
def author(authorid: str):
    """Fetch and display author profile info and papers"""

    notes = list(fetch_notes_for_author(authorid))
    print(f"{authorid} note count: {len(notes)}")

    profile = fetch_profile(authorid)
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


@fetch.command()
@click.option("--slice", type=(int, int), callback=validate_slice)
def profiles(slice: Slice):
    """Fetch and display a list of user profiles from OpenReview"""
    profiles = fetch_profiles(slice=slice)
    for p in profiles:
        names = p.content.names
        print(f"Profile: {names}")


@fetch.command()
@click.argument("id", type=str)
def profile(id: str):
    """Fetch (by id) and display a user profile from OpenReview"""
    profile = fetch_profile(id)
    if profile:
        pprint(asdict(profile))
    else:
        print("No Profile found")


@fetch.command()
@click.option("--brief", is_flag=True)
@click.option("--slice", type=(int, int), default=None, callback=validate_slice)
def notes(brief: bool, slice: Optional[Slice]):
    """Fetch and display a list of notes from OpenReview"""
    if slice:
        print(f"Fetching Notes {slice}")
    else:
        print(f"Fetching All Notes")

    notes = fetch_notes_for_dblp_rec_invitation(slice=slice)
    for note in notes:
        if brief:
            print(f"{note.id} #{note.number}: {note.content.title}")
        else:
            pprint(asdict(note))


@fetch.command()
@click.argument("id", type=str)
def note(id: str):
    """Fetch (by id) and display a note from OpenReview"""
    note = fetch_note(id)
    pprint(asdict(note))
