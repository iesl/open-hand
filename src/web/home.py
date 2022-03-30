from typing import List
from flask import (
    Blueprint,
    render_template,
    abort,
    redirect,
    url_for,
    # request, url_for, flash, g, redirect,
)

from lib.data import MentionRecords, get_paper_with_signatures
from lib.database import add_all_referenced_signatures, get_canopy, get_canopy_strs
from lib.predict import mentions_to_displayables

import math


bp = Blueprint("app", __name__, template_folder="templates")

from flask import render_template


@bp.route("/")
def index():
    return redirect(url_for(".show_canopies"))


def author_name_variants(canopy: MentionRecords) -> List[str]:
    variants: List[str] = []

    for sigid, sig in canopy.signatures.items():
        paper = canopy.papers[sig.paper_id]
        for author in paper.authors:
            if author.position == sig.author_info.position:
                variants.append(author.author_name)

    return list(set(variants))


@bp.route("/canopies")
@bp.route("/canopies/<int:page>")
def show_canopies(page: int = None):
    if page is None:
        page = 0

    pagesize = 50
    offset = page * pagesize

    canopystrs = get_canopy_strs()

    pagecount = math.ceil(len(canopystrs) / pagesize)

    canopypage = canopystrs[offset : offset + pagesize]
    canopies = [(i, cstr, get_canopy(cstr)) for i, cstr in enumerate(canopypage)]
    counted_canopies = [
        (i, len(mentions.papers), cstr, author_name_variants(mentions)) for i, cstr, mentions in canopies
    ]
    counted_canopies.sort(reverse=True, key=lambda r: r[1])

    return render_template(
        "canopies.html", canopies=counted_canopies, pagecount=pagecount, offset=offset, pagesize=pagesize, page=page
    )


@bp.route("/canopy/<string:id>")
def show_canopy(id: str):
    mentions = get_canopy(id)
    _, cluster_dict = mentions_to_displayables(mentions)
    cluster_ids = list(cluster_dict)

    return render_template("canopy.html", canopy=id, cluster_ids=cluster_ids, cluster_dict=cluster_dict)


def XXXshow_canopy0(id: str):
    mentions_init = get_canopy(id)
    init_signatures = mentions_init.signatures.values()
    mentions = add_all_referenced_signatures(mentions_init)
    papers_with_sigs = [get_paper_with_signatures(mentions, s) for s in init_signatures]

    return render_template("canopy.html", canopy=id, pws_iter=papers_with_sigs)


@bp.route("/clusters")
def show_clusters():
    return render_template("canopies.html")


@bp.route("/cluster/<string:id>")
def show_cluster(id: str):
    mentions = get_canopy(id)
    papers, signatures = mentions.papers, mentions.signatures
    return render_template("cluster.html")
