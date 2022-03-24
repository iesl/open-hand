from cli import utils
from cli import commands as cmd

print("here!")

app = utils.make_celery()

# @app.task(name='add')
# def add(x: int, y: int):
#     return cli.add(x, y)
#

@app.task(name='mul')
def mul(x: int, y: int):
    return cmd.mul(x, y)


if __name__ == "__main__":
    app.worker_main()
