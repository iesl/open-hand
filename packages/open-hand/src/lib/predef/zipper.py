### A Zipper is a list-like data structure which has a current location, or 'focus'
### It supports movement to the next/previous item
### The helper class HasFocus is used as a marker trait, when converting the Zipper to a List,
###     pairing each value with a flag indicating whether it is the focused element


from dataclasses import dataclass
from typing import Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class HasFocus(Generic[T]):
    val: T
    has_focus: bool


@dataclass
class Zipper(Generic[T]):
    pre: List[T]
    post: List[T]
    focus: T

    def to_list(self) -> List[T]:
        pre = self.pre
        return [*pre, self.focus, *self.post]

    def items(self) -> List[HasFocus[T]]:
        pre = [HasFocus(val=t, has_focus=False) for t in self.pre]
        post = [HasFocus(val=t, has_focus=False) for t in self.post]
        f = HasFocus(val=self.focus, has_focus=True)
        return [*pre, f, *post]

    def forward(self, n: int = 1) -> "Optional[Zipper[T]]":
        if n == 0:
            return self

        if n > len(self.post):
            return None

        newfocus: T = self.post[n - 1]
        newpost: List[T] = self.post[n:]
        post2pre: List[T] = self.post[0 : n - 1]
        newpre: List[T] = self.pre + [self.focus] + post2pre

        return Zipper(pre=newpre, focus=newfocus, post=newpost)

    def find(self, f: Callable[[T], bool]) -> "Optional[Zipper[T]]":
        curr = self
        while curr is not None:
            if f(curr.focus):
                return curr
            curr = curr.forward(1)
        return None

    def __str__(self) -> str:
        return f"zipper[{self.pre} <{self.focus}> {self.post}]"

    @classmethod
    def fromList(cls, l: List[T]) -> "Optional[Zipper[T]]":
        if len(l) == 0:
            return None

        pre = []
        post = l[1:]
        focus = l[0]
        return cls(pre=pre, post=post, focus=focus)
