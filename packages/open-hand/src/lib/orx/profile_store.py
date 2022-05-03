from logging import Logger
from typing import Dict, List, Set

from lib.orx.profile_schemas import Profile
from lib.predefs.data import MentionRecords, PaperRec, PaperWithPrimaryAuthor, SignatureRec, mergeMentions
from lib.predefs.typedefs import TildeID
from lib.orx.open_exchange import get_notes_for_author, get_profile, mention_records_from_notes

from lib.predefs.log import createlogger

from disjoint_set import DisjointSet


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

    def fetch_user_mentions(self, id: TildeID) -> MentionRecords:
        self.add_profile(id)
        if id not in self.userMentions:
            notes = get_notes_for_author(id)
            notelist = list(notes)
            mentionRecs = mention_records_from_notes(notelist)
            self.userMentions[id] = mentionRecs
            self.allMentions = mergeMentions(self.allMentions, mentionRecs)
        return self.userMentions[id]

    def fetch_papers(self, id: TildeID) -> List[PaperRec]:
        userMentions = self.fetch_user_mentions(id)
        return [p for _, p in userMentions.papers.items()]

    def fetch_signatures(self, id: TildeID) -> List[SignatureRec]:
        userMentions = self.fetch_user_mentions(id)
        return [s for _, s in userMentions.signatures.items() if s.author_info.openId == id]

    def fetch_signatures_as_pwpa(self, id: TildeID) -> List[PaperWithPrimaryAuthor]:
        sigs = self.fetch_signatures(id)
        pwpas = [PaperWithPrimaryAuthor.from_signature(self.allMentions, s) for s in sigs]
        return pwpas
