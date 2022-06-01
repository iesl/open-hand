from typing import Any, Dict, Union, Optional, Tuple
from celery.app.base import Celery

import click
from lib.predef.typedefs import Slice


# def run(ctx: Context, task, *args, **kwds):
#     remote: bool = ctx.parent.params["remote"]
#     if remote:
#         print("Calling remote function")
#         task.delay(*args, **kwds).get()
#     else:
#         print("Calling local function")
#         task(*args, **kwds)


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

    def __call__(self, *args: Any, **kwargs: Dict[str, Any]):
        # self.app is the Celery app instance
        with self.app.flask_app.app_context():
            Task.__call__(self, *args, **kwargs)


def validate_slice(ctx: click.Context, param: click.Parameter, value: Optional[Tuple[int, int]]) -> Optional[Slice]:
    if value is None:
        return None
    return Slice(start=value[0], length=value[1])
