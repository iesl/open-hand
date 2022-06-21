from dataclasses import dataclass
from typing import Generic, List, Optional, Tuple, TypeVar

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
    def destructure(ts: List[T]) -> Tuple[Optional[T], List[T]]:
        if len(ts) == 0:
            return None, ts

        return ts[0], ts[1:]
