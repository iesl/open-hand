from dataclasses import asdict
from logging import Logger
from pprint import pprint
from typing import Dict, List, Optional, Set

from disjoint_set import DisjointSet

from lib.open_exchange.profile_schemas import Profile
from lib.open_exchange.open_fetch import get_notes_for_author, get_profile

from lib.predef.typedefs import TildeID
from lib.predef.log import createlogger

from .data import MentionRecords, mention_records_from_notes, mergeMentions, PaperWithPrimaryAuthor
from .shadowdb_schemas import PaperRec, SignatureRec


class ProfileStore:
    profiles: Dict[TildeID, Profile]
    userMentions: Dict[TildeID, MentionRecords]
    allMentions: MentionRecords
    ds: DisjointSet[TildeID]
    log: Logger

    def __init__(self) -> None:
        self.profiles = dict()
        self.ds = DisjointSet()
        self.userMentions = dict()
        self.allMentions = MentionRecords(dict(), dict())
        self.log = createlogger("ProfileStore")

    def add_profile(self, id: TildeID) -> Optional[TildeID]:
        if id not in self.ds:
            self.log.debug(f"add_profile({id}): retrieving...")
            p = get_profile(id)
            if p is None:
                self.log.warn(f"No such profile: {id}")
                return
            self.ds.find(p.id)  # implicitly adds id to disjoint set
            if id != p.id:
                self.ds.union(id, p.id)  # id might have been an email, p.id will likely be a tildeId
                self.log.debug(f"{id} == {p.id}")

            self.profiles[id] = p

            for name in p.content.names:
                ## Putting id as 2nd param to ds.union() guarantees that it will
                ##   always be the canonical version for connected elements
                user = name.username
                if user is not None and user != p.id:
                    self.ds.union(user, p.id)
                    self.log.debug(f"{user} == {p.id}")

        else:
            self.log.debug(f"add_profile({id}): already in store")

        return self.ds.find(id)

    def canonical_id(self, id: TildeID) -> TildeID:
        self.add_profile(id)
        return self.ds.find(id)

    def canonicalize_ids(self, ids: List[TildeID]) -> Set[TildeID]:
        return set([self.canonical_id(id) for id in ids])

    def get_all_ids(self) -> List[TildeID]:
        return [id for id, _ in self.ds.itersets(with_canonical_elements=True)]

    def show_profile_sets(self):
        print("Profile ID Equivalencies")
        for s in self.ds.itersets(with_canonical_elements=True):
            id, eqivs = s
            print(f"{id}: {eqivs}")
        else:
            print(f"No Equivalents")

    def get_equivalent_ids(self, id: TildeID) -> Set[TildeID]:
        for idset in self.ds.itersets(with_canonical_elements=False):
            if isinstance(idset, set) and id in idset:
                return idset
            if isinstance(idset, tuple):
                _, ids = idset
                if id in ids:
                    return ids
        return set([id])

    def fetch_user_mentions(self, id: TildeID) -> MentionRecords:
        self.log.info(f"fetch_user_mentions({id})...")
        self.add_profile(id)
        if id not in self.userMentions:
            notes = list(get_notes_for_author(id))
            self.log.info(f"    ({id}) note count = {len(notes)}")
            mentions = mention_records_from_notes(notes)
            self.log.info(f"    ({id}) paper mention count = {len(mentions.get_papers())}")
            self.userMentions[id] = mentions
            self.allMentions = mergeMentions(self.allMentions, mentions)
        return self.userMentions[id]

    def fetch_papers(self, id: TildeID) -> List[PaperRec]:
        userMentions = self.fetch_user_mentions(id)
        return userMentions.get_papers()

    def fetch_signatures(self, id: TildeID) -> List[SignatureRec]:
        userMentions = self.fetch_user_mentions(id)
        equivs = self.get_equivalent_ids(id)
        signatures_for_author = [s for s in userMentions.get_signatures() if s.author_info.openId in equivs]

        return signatures_for_author

    def fetch_signatures_as_pwpa(self, id: TildeID) -> List[PaperWithPrimaryAuthor]:
        sigs = self.fetch_signatures(id)
        pwpas = [PaperWithPrimaryAuthor.from_signature(self.allMentions, s) for s in sigs]
        return pwpas
