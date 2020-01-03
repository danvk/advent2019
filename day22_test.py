import day22


def test_cut_inv():
    deck = [*range(10)]
    n = 3
    cut_deck = day22.cut(deck, n)
    for pos, card in enumerate(cut_deck):
        assert day22.cut_inv(n, len(deck), pos) == card


def test_cut_inv_neg():
    deck = [*range(10)]
    n = -3
    cut_deck = day22.cut(deck, n)
    for pos, card in enumerate(cut_deck):
        assert day22.cut_inv(n, len(deck), pos) == card


def test_stack_inv():
    deck = [*range(10)]
    stacked_deck = day22.new_stack(deck)
    for pos, card in enumerate(stacked_deck):
        assert day22.new_stack_inv(len(deck), pos) == card


def test_increment_inv():
    deck = [*range(10)]
    n = 3
    stacked_deck = day22.increment(deck, n)
    for pos, card in enumerate(stacked_deck):
        assert day22.increment_inv(n, len(deck), pos) == card
