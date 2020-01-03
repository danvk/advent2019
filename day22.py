#!/usr/bin/env python

from dataclasses import dataclass
import fileinput


@dataclass
class ModEq:
    """f(x) = ax + b mod n."""
    a: int
    b: int
    n: int

    def cut(self, x):
        self.b = (self.b - x) % self.n

    def increment(self, x):
        self.a = (self.a * x) % self.n
        self.b = (self.b * x) % self.n

    def stack(self):
        self.a = -self.a % self.n
        self.b = (-1 - self.b) % self.n

    def fwd(self, x):
        return (self.a * x + self.b) % self.n

    def inv(self, x):
        return (x - self.b) * modinv(self.a, self.n) % self.n

    def compose(self, other):
        """Returns a new ModEq."""
        assert self.n == other.n
        r = ModEq(self.a, self.b, self.n)
        r.increment(other.a)
        r.cut(-other.b)
        return r

    def to_pow(self, k):
        """Apply the equation recursively k times."""
        r = ModEq(1, 0, self.n)
        pot = self

        while k:
            if k % 2 == 1:
                r = pot.compose(r)
            pot = pot.compose(pot)
            k = k // 2

        return r

    def repr(self):
        return f'{self.a}x + {self.b} mod {self.n}'

    @staticmethod
    def from_file(inp, n):
        eq = ModEq(a=1, b=0, n=n)
        for line in inp:
            line = line.strip()
            if line == NEW_STACK:
                eq.stack()
            elif line.startswith(CUT):
                c = int(line[len(CUT):])
                eq.cut(c)
            elif line.startswith(INC):
                c = int(line[len(INC):])
                eq.increment(c)
            else:
                raise ValueError(f'Unknown shuffle type {line}')
        return eq


def cut(deck, n):
    return deck[n:] + deck[:n]


def cut_inv(n, deck_len, x):
    """Where is the card at position x before this cut?"""
    return (x + n) % deck_len


def increment(deck, n):
    out = [None] * len(deck)
    for i, c in enumerate(deck):
        p = (i * n) % len(deck)
        assert out[p] is None
        out[p] = c
    return out


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def increment_inv(n, deck_len, x):
    mult_inv = modinv(n, deck_len)
    return (mult_inv * x) % deck_len


def new_stack(deck):
    return deck[::-1]


def new_stack_inv(deck_len, x):
    return deck_len - 1 - x


def print_deck(deck):
    print(' '.join(str(d) for d in deck))


NEW_STACK = 'deal into new stack'
CUT = 'cut '
INC = 'deal with increment '


def shuffle(inp, deck):
    for line in inp:
        line = line.strip()
        if line == NEW_STACK:
            deck = new_stack(deck)
        elif line.startswith(CUT):
            c = int(line[len(CUT):])
            deck = cut(deck, c)
        elif line.startswith(INC):
            c = int(line[len(INC):])
            deck = increment(deck, c)
        else:
            raise ValueError(f'Unknown shuffle type {line}')
    return deck


def shuffle_inv(commands, deck_len, x):
    for line in reversed(commands):
        if line == NEW_STACK:
            x = new_stack_inv(deck_len, x)
        elif line.startswith(CUT):
            c = int(line[len(CUT):])
            x = cut_inv(c, deck_len, x)
        elif line.startswith(INC):
            c = int(line[len(INC):])
            x = increment_inv(c, deck_len, x)
        else:
            raise ValueError(f'Unknown shuffle type {line}')
    return x


if __name__ == '__main__':
    # N = 10
    # N = 10007
    N = 119315717514047
    lines = [*fileinput.input()]

    # deck = [*range(N)]
    # deck = shuffle(lines, deck)
    # deck = shuffle(lines, deck)
    # print_deck(deck)
    # print(deck.index(2019))

    eq = ModEq.from_file(lines, N)
    eq = eq.to_pow(101741582076661)
    print(eq.inv(2020))
    # eq = eq.compose(eq)
    # print(eq)
    # print(eq.fwd(2019))
    # print(eq.inv(2480))
    # print([eq.inv(i) for i in range(N)])

    # x = 2020
    # i = 0
    # while True:
    #     i += 1
    #     x = shuffle_inv(lines, N, x)
    #     print(f'{i:9d} {x}')
    # print(f'Period for {x} == {i}')

# 101741582076661
# 119315717514047
