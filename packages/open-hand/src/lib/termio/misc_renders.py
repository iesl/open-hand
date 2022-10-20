from typing import List
import click
from lib.facets.authorship import AuthorCatalog

from lib.predef.typedefs import SignatureID
from lib.predef.output import dim, yellowB

from lib.open_exchange.utils import is_tildeid
from lib.predef.zipper import HasFocus

from lib.shadowdb.data import (
    MentionRecords,
    PaperRec,
    SignedPaper,
    SignatureRec,
)

def format_signature(item: HasFocus[SignatureRec]) -> str:
    sig = item.val

    openId = sig.author_info.openId
    ts = ""
    if openId is not None and is_tildeid(openId):
        ts = "~"
    if item.has_focus:
        return yellowB(f"{ts}{sig.author_info.fullname}")
    return dim(f"{ts}{sig.author_info.fullname}")


def format_signature_id(item: HasFocus[SignatureRec]) -> str:
    sig = item.val
    openId = sig.author_info.openId
    if openId is None:
        openId = "undefined"
    if openId is not None and is_tildeid(openId):
        return yellowB(f"{openId}")
    return dim(openId)


def render_paper(paper: PaperRec):
    title = click.style(paper.title, fg="blue")
    author_names = [f"{p.author_name}" for p in paper.authors]
    auths = ", ".join(author_names)
    id = paper.paper_id
    click.echo(f"{title} ({id})")
    click.echo(f"      {auths}")


def render_papers(papers: List[PaperRec]):
    for p in papers:
        render_paper(p)


def render_signature(sig_id: SignatureID, entry_num: int, mentions: MentionRecords):
    sig = mentions.signatures[sig_id]
    signed_paper = SignedPaper.from_signature(mentions, sig)
    render_signed_paper(signed_paper, entry_num)


def render_signed_paper(signed_paper: SignedPaper, n: int):
    title = click.style(signed_paper.paper.title, fg="blue")
    sid = signed_paper.primary_signature().signature_id
    fmtsigs = [format_signature(sig) for sig in signed_paper.signatures.items()]
    auths = ", ".join(fmtsigs)
    click.echo(f"{n}.   {title} ({sid})")
    click.echo(f"      {auths}")



def render_author_catalog(catalog: AuthorCatalog):
    click.echo(f"IDS: ")
    for un in catalog.usernames:
        click.echo(f"{un}")

    click.echo(f"Papers")
    for i, sp in enumerate(catalog.signed_papers):
        render_signed_paper(sp, i+1)
