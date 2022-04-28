from typing import Union
from celery.app.base import Celery
from click.core import Context


def run(ctx: Context, task, *args, **kwds):
    remote: bool = ctx.parent.params["remote"]
    if remote:
        print("Calling remote function")
        task.delay(*args, **kwds).get()
    else:
        print("Calling local function")
        task(*args, **kwds)


from celery import Task

current_app: Union[Celery, None] = None


def make_celery() -> Celery:
    global current_app

    if current_app is None:
        current_app = Celery(
            "cli",
            broker="redis://localhost:6379/0",
            backend="redis://localhost:6379/0",
        )
        # current_app.Task = MTask

    return current_app


class MTask(Task):
    """
    Celery task running within a Flask application context.
    """

    def __call__(self, *args, **kwargs):
        # self.app is the Celery app instance
        with self.app.flask_app.app_context():
            Task.__call__(self, *args, **kwargs)
