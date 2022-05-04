from typing import Generator

def nextnums(init: int = 0) -> Generator[int, None, None]:
    i = init
    while 1:
        yield i
        i = i + 1


