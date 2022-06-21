from pprint import pprint
from typing import Any, Callable, List, NoReturn, Tuple, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")


class OneOrBoth(Generic[T]):
    pass


@dataclass
class Left(OneOrBoth[T]):
    value: T

    @staticmethod
    def of(value: T) -> OneOrBoth[T]:
        return Left[T](value)


@dataclass
class Right(OneOrBoth[T]):
    value: T

    @staticmethod
    def of(value: T) -> OneOrBoth[T]:
        return Right[T](value)


@dataclass
class Both(OneOrBoth[T]):
    value: T

    @staticmethod
    def of(value: T) -> OneOrBoth[T]:
        return Both[T](value)


@dataclass
class Alignment(Generic[T]):
    values: List[OneOrBoth[T]]


def isLeft(oob: OneOrBoth[Any]) -> bool:
    return isinstance(oob, Left)


def isRight(oob: OneOrBoth[Any]) -> bool:
    return isinstance(oob, Right)


def assert_never(x: Any) -> NoReturn:
    raise AssertionError("Unhandled type: {}".format(type(x).__name__))


U = TypeVar("U")


class Fold(Generic[T, U]):
    onLeft: Callable[[T], U]
    onRight: Callable[[T], U]
    onBoth: Callable[[T], U]

    def __init__(self, onLeft: Callable[[T], U], onRight: Callable[[T], U], onBoth: Callable[[T], U]):
        self.onLeft = onLeft
        self.onRight = onRight
        self.onBoth = onBoth

    def __call__(self, oob: OneOrBoth[T]):
        if isinstance(oob, Left):
            return self.onLeft(oob.value)
        elif isinstance(oob, Right):
            return self.onRight(oob.value)
        elif isinstance(oob, Both):
            return self.onBoth(oob.value)
        else:
            assert_never(oob)


def separateOOBs(oobs: List[OneOrBoth[T]]) -> Tuple[Left[List[T]], Right[List[T]], Both[List[T]]]:
    ls: List[T] = []
    rs: List[T] = []
    bs: List[T] = []
    fold = Fold[T, Any](
        lambda l: ls.append(l),
        lambda r: rs.append(r),
        lambda b: bs.append(b),
    )
    for oob in oobs:
        fold(oob)

    return (Left(ls), Right(rs), Both(bs))


if __name__ == "__main__":

    l0 = Left.of(0)
    la = Left.of("a")
    ra = Right.of("qwerty")
    raIsLeft = isinstance(ra, Left)
    raIsRight = isinstance(ra, Right)
    pprint(f"l0 = {l0}")
    pprint(f"la = {la}")
    pprint(f"ra = {ra}")
    pprint(f"left = {raIsLeft} right= {raIsRight}")
    align0 = Alignment(values=[la, ra])
    pprint(align0)

    OobToStr = Fold[str, str](
        lambda l: f"Left:{l}",
        lambda r: f"Right:{r}",
        lambda b: f"Both:{b}",
    )

    ooa = OobToStr(la)
    oora = OobToStr(ra)
    print(f"ooa = {ooa}")
    print(f"oora = {oora}")
