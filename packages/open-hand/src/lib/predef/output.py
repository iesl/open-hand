import click


def dim(s: str) -> str:
    return click.style(s, dim=True)


def yellowB(s: str) -> str:
    return click.style(s, fg="yellow", bold=True)
