from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from lib.predef.typedefs import Slice

T = TypeVar("T")

Getter = Callable[[], List[T]]


class IterGet(Generic[T]):
    """Create an Iterator[T] given a getter function

    Getter[T] is assumed to take as params a Dict, containing
    'offset' and 'limit' keys to control batch fetching

    This class is tailor made to integrate with the syntax of the REST API
    used in OpenReview for getting Notes/Profiles/etc.
    """

    get_function: Getter[T]
    params: Dict[str, Any]
    offset: int
    limit: int

    slice: Optional[Slice]

    current_batch: List[T]
    batch_index: int
    batch_num: int
    iterations: int

    def __init__(self, get_function: Getter[T], **params: Any):
        self.offset = 0
        self.limit = 1000

        self.current_batch = []
        self.batch_index = 0
        self.batch_num = 0
        self.slice = None

        self.iterations = 0

        self.params = params

        self.get_function = get_function

    def withSlice(self, slice: Slice) -> "IterGet[T]":
        self.slice = slice
        return self

    def _advanceOffset(self):
        self.offset += self.params["limit"]
        self.params["offset"] = self.offset

    def _update_batch(self, *, first_batch: bool):
        if first_batch:
            if self.slice is not None:
                self.offset = self.slice[0]

            self.params.update({"offset": self.offset, "limit": self.limit})
        else:
            self._advanceOffset()

        self.current_batch = self.get_function(**self.params)
        self.batch_num += 1

    def __iter__(self) -> "IterGet[T]":
        return self

    def __next__(self) -> T:
        if self.slice is not None:
            if self.iterations >= self.slice[1]:
                raise StopIteration

        if self.batch_num == 0:
            self._update_batch(first_batch=True)

        if len(self.current_batch) == 0:
            raise StopIteration
        else:
            next_obj = self.current_batch[self.batch_index]
            self.iterations += 1
            if (self.batch_index + 1) == len(self.current_batch):
                self._update_batch(first_batch=False)
                self.batch_index = 0
            else:
                self.batch_index += 1
            return next_obj
