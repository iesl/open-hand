import click
from typing import Optional

from lib.shadowdb.open_etl import (
    shadow_paper_by_id,
    shadow_profile_by_id,
    populate_shadowdb_from_notes,
    populate_shadowdb_from_profiles,
    show_unpopulated_profiles,
)
from lib.predef.typedefs import Slice
from .utils import validate_slice

from lib.shadowdb.shadowdb import getShadowDB
from .cli_base import cli


@cli.group()
def shadow():
    """Create/update local shadow DB of OpenReview papers/authors"""


@shadow.command("paper")
@click.argument("id", type=str)
def paper(id: str):
    """Shadow a single paper by ID"""
    shadow_paper_by_id(id)


@shadow.command("profile")
@click.argument("id", type=str)
def shadowdb_profile(id: str):
    """Shadow a single profile by ID"""
    shadow_profile_by_id(id)


@shadow.command("notes")
@click.option("--slice", type=(int, int), default=None, callback=validate_slice)
def shadowdb_populate_notes(slice: Optional[Slice]):
    """Create the local shadow DB"""
    populate_shadowdb_from_notes(slice)


@shadow.command("profiles")
@click.option("--slice", type=(int, int), default=None, callback=validate_slice)
def shadowdb_populate_profiles(slice: Optional[Slice]):
    """Create the local shadow DB"""
    populate_shadowdb_from_profiles(slice)

@shadow.command("missing")
def shadowdb_username_without_profiles():
    """Create the local shadow DB"""
    show_unpopulated_profiles()


@shadow.command("reset")
def shadowdb_reset():
    """Clean/recreate DB collections"""
    getShadowDB().db.reset_db()
