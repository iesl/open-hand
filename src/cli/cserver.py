from cli import utils
from cli import commands as cmd

app = utils.make_celery()

@app.task(name='mul')
def mul(x: int, y: int):
    return cmd.mul(x, y)


@app.task
def normalize():
    """Normalize all un-normalized papers/signatures"""
    from lib.normalizer import normalize

    return normalize()

if __name__ == "__main__":
    app.worker_main()
