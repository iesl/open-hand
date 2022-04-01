from cli import utils
from cli import commands as cmd

## Commands in this module are called from the cli module, and have the same names as
## the calling functions.

app = utils.make_celery()

@app.task
def normalize():
    """Normalize all un-normalized papers/signatures"""
    from lib.normalizer import normalize

    return normalize()


if __name__ == "__main__":
    app.worker_main()
