from typing import NewType, NamedTuple, Union, Literal

ClusterID = NewType("ClusterID", str)

TildeID = str
EmailID = str
AuthorQueryID = str
AuthorID = Union[TildeID, EmailID, AuthorQueryID]
OpenID = AuthorID

PaperID = str
SignatureID = str
CatalogID = str

CatalogType = Union[
    Literal["Predicted"],
    Literal["OpenReviewProfile"]
]

class Slice(NamedTuple):
    start: int
    length: int

    def end(self) -> int:
        return self.start + self.length

    def __str__(self) -> str:
        return f"slice({self.start}-{self.end()})"

    def __repr__(self) -> str:
        return str(self)

    def __format__(self, __format_spec: str) -> str:
        return format(str(self), __format_spec)
