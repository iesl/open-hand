from logging import Logger
from typing import Dict, List, Set

from lib.orx.profile_schemas import Profile
from lib.predefs.typedefs import TildeID
from lib.orx.open_exchange import get_profile

from lib.predefs.log import createlogger

from disjoint_set import DisjointSet


class ProfileStore:
    profiles: Dict[str, Profile]
    ds: DisjointSet[TildeID]
    log: Logger

    def __init__(self) -> None:
        self.profiles = dict()
        self.ds = DisjointSet()
        self.log = createlogger("ProfileStore")

    def add_profile(self, id: TildeID) -> TildeID:
        if id not in self.ds:
            self.log.info(f"add_profile({id}): retrieving...")
            p = get_profile(id)
            self.ds.find(id)  # implicitly adds id to disjoint set
            self.profiles[id] = p
            for name in p.content.names:
                ## Putting id as 2nd param to ds.union() guarantees that it will
                ##   always be the canonical version for connected elements
                username = name.username
                if username is not None and username != id:
                    self.ds.union(username, id)
                    self.log.info(f"{username} == {id}")

        else:
            self.log.debug(f"add_profile({id}): already in store")

        return self.ds.find(id)

    def canonical_id(self, id: TildeID) -> TildeID:
        return self.ds.find(id)

    def canonicalize_ids(self, ids: List[TildeID]) -> Set[TildeID]:
        return set([self.canonical_id(id) for id in ids])

    def get_all_ids(self) -> List[TildeID]:
        return [id for id, _ in self.ds.itersets(with_canonical_elements=True)]

    def show_profile_sets(self):
        self.log.info("Profile ID Equivalencies")
        for s in self.ds.itersets(with_canonical_elements=True):
            id, eqivs = s
            self.log.info(f"{id}: {eqivs}")
