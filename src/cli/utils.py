from typing import Union
from celery.app.base import Celery
import click
from click.core import Context
from functools import wraps


def rcall(*args, **kwds):
    f = args[0]
    impl = kwds["impl"]
    print(impl)
    # print(f"Decorating function {f.__name__} with {impl})

    @click.pass_context
    @wraps(f)
    def wrapper(*args, **kwds):
        print("Calling decorated function")
        return f(*args, **kwds)

    return wrapper


def impl(impl):
    def decorate(f):
        @click.pass_context
        @wraps(f)
        def wrapper(*args, **kwds):
            print(f"Calling decorated function {f.__name__}({impl.__name__})({[a for a in args]})")
            # return impl(*args, **kwds)

        return wrapper

    return decorate


def run(ctx: Context, task, *args, **kwds):
    remote: bool = ctx.parent.params["remote"]
    if remote:
        print("Calling remote function")
        task.delay(*args, **kwds).get()
    else:
        print("Calling local function")
        task(*args, **kwds)



from celery import current_app as current_celery_app
from celery import Task

current_app: Union[Celery, None] = None

def make_celery() -> Celery:
    global current_app

    if current_app is None:
        current_app  = Celery(
            "cli",
            broker = "redis://localhost:6379/0",
            backend = "redis://localhost:6379/0",
            # include=('cli')
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
