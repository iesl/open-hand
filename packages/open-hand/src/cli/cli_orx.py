import typing as t
from pprint import pprint

import click
from .cli_base import cli

from lib.orx.open_exchange import get_notes_for_author, get_profile, get_profiles

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
    get_profile(authorid)
    for n in notes:
        id = n.id
        content = n.content
        title = content.get('title') if 'title' in content else '??'
        authors = content.get('authors') if 'authors' in content else '??'
        authorstr = ", ".join(authors)
        print(f"{title}  ({id})")
        print(f"  {authorstr}")

@get.command()
def profiles():
    profiles = get_profiles()
    print("Profile 0")
    pprint(profiles[0: 3])
