#!/usr/bin/env python

import fileinput
import re


def sgn(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0


class Body:
    def __init__(self, pos, vel=None):
        self.pos = pos
        self.vel = vel or [0, 0, 0]

    def __repr__(self):
        p = self.pos
        v = self.vel
        return (
            f'pos=<x={p[0]}, y={p[1]}, z={p[2]}>, '
            f'vel=<x={v[0]}, y={v[1]}, z={v[2]}>'
        )

    def apply_gravity(self, others):
        """Returns delta v from gravity of other on us."""
        p = self.pos
        dv = [0, 0, 0]
        for other in others:
            po = other.pos
            for i in (0, 1, 2):
                dv[i] += sgn(po[i] - p[i])

        self.vel = [v + dv for v, dv in zip(self.vel, dv)]

    def step(self):
        self.pos = [p + v for p, v in zip(self.pos, self.vel)]

    def pot(self):
        return sum(abs(p) for p in self.pos)

    def kin(self):
        return sum(abs(v) for v in self.vel)

    def total_energy(self):
        return self.pot() * self.kin()


def step(bodies):
    for body in bodies:
        body.apply_gravity(bodies)
    for body in bodies:
        body.step()


def read_positions(inp):
    return [
        Body([int(x) for x in m.groups()])
        for m in [
            re.match(r'<x=(-?\d+), y=(-?\d+), z=(-?\d+)>', line)
            for line in inp
        ]
    ]


def print_bodies(bodies):
    print('\n'.join(repr(b) for b in bodies))
    print('Energy', sum(b.total_energy() for b in bodies))


def bodies_repr(bodies):
    return '\n'.join(repr(b) for b in bodies)


def repr_axis(bodies, axis: int):
    return ' '.join(f'{b.pos[axis]},{b.vel[axis]}' for b in bodies)


def period_for_axis(bodies, axis: int):
    seen = {}

    i = 0
    while True:
        r = repr_axis(bodies, axis)
        if r in seen:
            p = seen[r]
            print(f'{i:5} rep {p:5} (∆={i - p}): {r}')
            if seen[r] == 0:
                break
        else:
            seen[r] = i
        step(bodies)
        i += 1

    return i


if __name__ == '__main__':
    lines = [*fileinput.input()]

    for i in (0, 1, 2):
        bodies = read_positions(lines)
        print(period_for_axis(bodies, i))


# 2772 = 2^2 × 3^2 × 7 × 11
# 4686774924 = 2^2 × 3 × 13^2 × 983 × 2351

# Small sample:
# period for 0: 924x + 0;   924 = 2^2 × 3 × 7 × 11
# period for 1: 522x + 201; 522 = 2 × 3^2 × 29
# period for 2: 616x + 7;   616 = 2^3 * 7 * 11
# period for 3: 924x + 0;  (plus some others)
