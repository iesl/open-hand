from typing import List
import pytest
import os

from pathlib import Path
from jinja2.environment import Environment

# from jinja2.exceptions import TemplateNotFound
# from jinja2.exceptions import TemplatesNotFound
# from jinja2.exceptions import TemplateSyntaxError
# from jinja2.exceptions import UndefinedError
from jinja2.loaders import DictLoader, FileSystemLoader

from lib.data import AuthorInfoBlock, AuthorRec, MentionRecords, PaperRec, SignatureRec, get_paper_with_signatures


@pytest.fixture
def test_env():
    env = Environment(
        loader=DictLoader(
            dict(
                module="{% macro test() %}[{{ foo }}|{{ bar }}]{% endmacro %}",
                header="[{{ foo }}|{{ 23 }}]",
                o_printer="({{ o }})",
            )
        )
    )
    env.globals["bar"] = 23
    return env


@pytest.fixture
def fs_env() -> Environment:
    searchpath = (Path(__file__) / os.pardir / os.pardir / "web" / "templates").resolve()
    env = Environment(loader=FileSystemLoader(searchpath))
    return env


def gen_authorrec(position: int) -> AuthorRec:
    return AuthorRec(f"A. N{position}. Author", position)


def gen_authorrecs(n: int) -> List[AuthorRec]:
    return [gen_authorrec(i) for i in range(n)]


def gen_paperrec() -> PaperRec:
    rec = PaperRec(
        abstract=None,
        authors=gen_authorrecs(4),
        journal_name=None,
        paper_id="p#1",
        references=[],
        title="Some Paper Title",
        venue=None,
        year=1999,
    )
    return rec


def gen_mentions(paper: PaperRec) -> MentionRecords:
    num_authors = len(paper.authors)
    signature_ids = [(f"{paper.paper_id}_{i}", i) for i in range(num_authors)]
    signatures = [
        SignatureRec(
            author_id=id,
            signature_id=id,
            paper_id=paper.paper_id,
            cluster_id=None,
            author_info=AuthorInfoBlock(
                affiliations=[],
                block="a lin",
                given_block="a lin",
                email="a@lin.com",
                fullname="Adrian Lin",
                first="Adrian",
                last="Lin",
                middle=None,
                openId="~A_Lin1",
                position=i,
                suffix=None,
            ),
        )
        for (id, i) in signature_ids
    ]
    signature_dict = dict([(s.signature_id, s) for s in signatures])
    paper_dict = dict([(paper.paper_id, paper)])
    return MentionRecords(papers=paper_dict, signatures=signature_dict)


class TestImports:
    def test_paperrec_macros(self, fs_env):

        paper = gen_paperrec()
        mentions = gen_mentions(paper)
        signatures = [mentions.signatures[k] for k in mentions.signatures.keys()]
        sig1 = signatures[1]
        paper_with_signatures = get_paper_with_signatures(mentions, sig1)

        tmp = "{% import '_paperrec.html' as _paperrec %}" "{{ _paperrec.paper(pws) }}"
        t = fs_env.from_string(tmp)

        res = t.render(pws=paper_with_signatures)
        text = os.linesep.join([s for s in res.splitlines() if len(s.strip()) > 0])
        print(text)
