from pprint import pprint
from typing import List, TypeVar, Generic
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
