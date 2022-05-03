from lib.db.database import get_canopy, get_canopy_strs


def list_canopies(offset: int):
    cstrs = get_canopy_strs()
    slice = cstrs[offset : offset + 15]
    print(f"Total Canopies = {len(cstrs)}")
    for i, s in enumerate(slice):
        print(f"  {i+offset}. {s}")


def list_canopies_counted(offset: int):
    cstrs = get_canopy_strs()
    canopies = [(i, cstr, get_canopy(cstr)) for i, cstr in enumerate(cstrs)]
    counted_canopies = [(i, len(mentions.papers), cstr) for i, cstr, mentions in canopies]
    counted_canopies.sort(reverse=True, key=lambda r: r[1])
    slice = counted_canopies[offset : offset + 15]
    print(f"Total Canopies = {len(cstrs)}")
    for i, n, s in slice:
        print(f" {i+offset}. n={n} '{s}'")
