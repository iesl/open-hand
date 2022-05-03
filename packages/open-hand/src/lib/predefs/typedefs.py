from typing import Set, Dict, Tuple, NewType

ClusterID = NewType("ClusterID", str)
# TildeID = NewType("TildeID", str)
TildeID = str
# SignatureID = NewType("SignatureID", str)
SignatureID = str

StringCountDict = Dict[str, int]
NameCountDict = Dict[str, StringCountDict]

# e.g., {  ("abi", "abigail"), ("abbie", "abigail") ... }
# TODO this can be a much more efficient bimap implementation
NameEquivalenceSet = Set[Tuple[str, str]]
