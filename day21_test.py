import day21


def digits(x):
    return [int(c) for c in x]


def test_should_jump():
    should_jump = day21.should_jump
    assert not should_jump(digits('111111111'))  # A
    assert should_jump(digits('011111111'))  # B

    # do jump (D & not E):
    # .................
    # .................
    # ...@.............
    # #####..#.########
    #     ABCDEFGHI
    #     100101111
    assert should_jump(digits('100101111'))  # C

    # do jump (D & E):
    # .................
    # .................
    # ..@..............
    # #####.##.########
    #    ABCDEFGHI
    #    110110111
    assert should_jump(digits('110110111'))  # D

    # do jump (D & not E & not F)
    # .................
    # .................
    # ..@..............
    # #####.#..########
    #    ABCDEFGHI
    #    110100111
    assert should_jump(digits('110100111'))  # E

    # do jump: (D & H & not E & not G)
    # .................
    # .................
    # ..@..............
    # #####.#.#.##.####
    #    ABCDEFGHI
    #    110101011
    assert should_jump(digits('110101011'))  # F

    # do _not_ jump: (D & not E & not H)
    # .................
    # .................
    # ..@..............
    # #####.#.#...#####
    #    ABCDEFGHI
    #    110101000
    assert not should_jump(digits('110101000'))  # G

    # do _not_ jump:
    # .................
    # .................
    # ..@..............
    # #####...#########
    #    ABCDEFGHI
    #    110001111
    assert not should_jump(digits('110001111'))  # H


def test_mismatch():
    ds = digits('110110111')
               # ABCDEFGHI
    assert day21.should_jump(ds)
    assert day21.should_jump_spring(ds)


def test_springscript():
    should_jump = day21.should_jump
    should_jump_spring = day21.should_jump_spring

    for sensors in [
        '111111111',
        '011111111',
        '100101111',
        '110110111',
        '110100111',
        '110101011',
        '110101000',
        '110001111'
    ]:
        ds = digits(sensors)
        assert should_jump(ds) == should_jump_spring(ds), sensors
