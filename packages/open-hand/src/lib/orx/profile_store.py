from pprint import pprint
from typing import Dict, List, Set

from lib.orx.profile_schemas import Profile
from lib.predefs.typedefs import TildeID
from lib.orx.open_exchange import get_profile

from disjoint_set import DisjointSet

class ProfileStore:
    profiles: Dict[str, Profile]
    ds: DisjointSet[TildeID]

    def __init__(self) -> None:
        self.profiles = dict()
        self.ds = DisjointSet()

    def add_profile(self, id: TildeID) -> TildeID:
        if id not in self.ds:
            print(f"getting profile for {id}")
            p = get_profile(id)
            self.ds.find(id)  # implicitly adds id to disjoint set
            self.profiles[id] = p
            for name in p.content.names:
                ## Putting id as 2nd param to ds.union() guarantees that it will
                ##   always be the canonical version for connected elements
                self.ds.union(name.username, id)

        return self.ds.find(id)

    def canonicalize_ids(self, ids: List[TildeID]) -> Set[TildeID]:
        return set([self.ds.find(id) for id in ids])
