from dataclasses import dataclass
from typing import Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T")


@dataclass
class ListOps(Generic[T]):
    @staticmethod
    def headopt(ts: List[T]) -> Optional[T]:
        return ListOps.headopt_strict(ts)[0]

    @staticmethod
    def uniq(ts: List[T]) -> List[T]:
        return list(set(ts))

    @staticmethod
    def headopt_strict(ts: List[T]) -> Tuple[Optional[T], Optional[List[T]]]:
        if len(ts) == 0:
            return None, None
        if len(ts) == 1:
            return ts[0], None

        return ts[0], ts[1:]
