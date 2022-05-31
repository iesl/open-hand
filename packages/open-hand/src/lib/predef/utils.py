from typing import Generator


def nextnums(init: int = 0) -> Generator[int, None, None]:
    i = init
    while 1:
        yield i
        i = i + 1


from email_validator import validate_email, EmailNotValidError


def is_valid_email(s: str) -> bool:
    try:
        validate_email(s).email
        return True
    except EmailNotValidError:
        return False
