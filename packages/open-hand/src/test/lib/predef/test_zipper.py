from typing import List

from lib.predef.zipper import Zipper


def test_zipper_create():
    l1: List[str] = ["a", "b", "c"]

    z1 = Zipper.fromList(l1)
    assert z1 is not None

    assert z1.focus == "a"
    for i in range(len(l1)):
        zfwd = z1.forward(i)
        assert zfwd is not None
        assert zfwd.focus == l1[i]

    assert z1.forward(len(l1) + 1) is None


def test_zipper_find():
    l1: List[str] = ["apple", "banana", "cherry"]

    z1 = Zipper.fromList(l1)
    assert z1 is not None

    zf0 = z1.find(lambda x: x.endswith("na"))
    assert zf0 is not None and zf0.focus == "banana"

    zf0 = z1.find(lambda x: x.endswith("le"))
    assert zf0 is not None and zf0.focus == "apple"

    zf0 = z1.find(lambda x: x.endswith("qwer"))
    assert zf0 is None
