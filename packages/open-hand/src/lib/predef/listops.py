from dataclasses import dataclass
from typing import Generic, List, Optional, Tuple, TypeVar
from itertools import chain

T = TypeVar("T")


@dataclass
class ListOps(Generic[T]):
    @staticmethod
    def headopt(ts: List[T]) -> Optional[T]:
        return ListOps.destructure(ts)[0]

    @staticmethod
    def uniq(ts: List[T]) -> List[T]:
        return list(set(ts))

    @staticmethod
    def flatten(ts: List[List[T]]) -> List[T]:
        return list(chain(*ts))

    @staticmethod
    def intersection(l1: List[T], l2: List[T]) -> List[T]:
        return [t for t in l1 if t in l2]

    @staticmethod
    def has_intersection(l1: List[T], l2: List[T]) -> bool:
        return len(ListOps.intersection(l1, l2)) == 0

    @staticmethod
    def destructure(ts: List[T]) -> Tuple[Optional[T], List[T]]:
        if len(ts) == 0:
            return None, ts

        return ts[0], ts[1:]
