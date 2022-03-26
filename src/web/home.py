from typing import List
from flask import (
    Blueprint,
    render_template,
    # request, url_for, flash, g, redirect,
)

from lib.canopies import CanopyMentions, get_canopy, get_canopy_strs, list_canopies

# from werkzeug.exceptions import abort

bp = Blueprint("app", __name__, template_folder="templates")

from flask import render_template


@bp.route("/")
def home():
    return render_template("home.html")


import math


def author_name_variants(canopy: CanopyMentions) -> List[str]:
    variants: List[str] = []

    for sigid, sig in canopy.signatures.items():
        paper = canopy.papers[sig["paper_id"]]
        if "authors" in paper:
            for author in paper["authors"]:
                if author["position"] == sig["author_info"]["position"]:
                    variants.append(author["author_name"])

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
    papers, signatures = get_canopy(id)
    return render_template("canopy.html", canopy=id, signatures=signatures, papers=papers)


@bp.route("/clusters")
def show_clusters():
    return render_template("canopies.html")


@bp.route("/cluster/<string:id>")
def show_cluster(id: str):
    return render_template("cluster.html")
