from dataclasses import asdict
import typing as t
from pprint import pprint

import click
from .cli_base import cli

from lib.orx.open_exchange import get_notes_for_author, get_profile, get_profiles, mention_records_from_notes


@cli.group()
def orx():
    """OpenReview exchange; fetch/update notes"""


@orx.group()
def get():
    """OpenReview exchange; fetch/update notes"""


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
        title = content.get("title") if "title" in content else "??"
        authors = content.get("authors") if "authors" in content else "??"
        authorstr = ", ".join(authors)
        print(f"{idx+1} {title}  ({id})")
        print(f"  {authorstr}")


@get.command()
@click.argument("offset", type=int)
@click.argument("limit", type=int)
def profiles(offset: int, limit: int):
    profiles = get_profiles(offset, limit)
    for p in profiles:
        names = p.content.names
        print(f"Profile: {names}")
