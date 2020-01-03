#!/usr/bin/env python

from collections import defaultdict
import fileinput
import itertools
import math


def read_asteroid_map(inp):
    out = []
    loc = None
    for y, line in enumerate(inp):
        for x, c in enumerate(line.strip()):
            if c == '#':
                out.append((x, y))
            if c == 'X':
                loc = (x, y)
    return loc, out


def slope(a, b):
    """Return slope from a to b as a reduced fraction."""
    # slope(a, b) == -slope(b, a) for all a, b
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    if dx == 0:
        return (0, -1 if dy < 0 else 1)
    elif dy == 0:
        return (-1 if dx < 0 else 1, 0)

    gcd = math.gcd(abs(dx), abs(dy))
    return (int(dx / gcd), int(dy / gcd))


def get_slope_pairs(asteroids):
    """Returns a map from asteroid1 --> slope --> asteroid2."""
    d = defaultdict(lambda: defaultdict(list))
    for a, b in itertools.combinations(asteroids, 2):
        d[a][slope(a, b)].append(b)
        d[b][slope(b, a)].append(a)
    return d


# STATION_LOC = (23, 19)

def make_angle_map(loc, asteroids):
    d = defaultdict(list)
    x, y = loc
    for a in asteroids:
        if a == loc:
            continue
        ax, ay = a
        angle = (360 + 90 - 180 / math.pi * math.atan2(y - ay, ax - x)) % 360
        d2 = (x - ax) ** 2 + (y - ay) ** 2
        d[angle].append((d2, a))

    for angle, pairs in d.items():
        d[angle] = [*sorted(pairs)]

    return d


def nuke_in_order(asteroids, by_angle):
    nuked = []
    angles = [*sorted(by_angle.keys())]
    print(angles)
    for a in angles:
        print(a, by_angle[a])

    while len(nuked) < len(asteroids) - 1:
        for angle in angles:
            a_at_a = by_angle[angle]
            if a_at_a:
                nuke, *rest = a_at_a
                nuked.append(nuke)
                by_angle[angle] = rest
    return nuked


if __name__ == '__main__':
    loc, asteroids = read_asteroid_map(fileinput.input())
    if not loc:
        slope_pairs = get_slope_pairs(asteroids)
        count, loc = max(
            (len(slope_pairs[a]), a)
            for a in asteroids
        )

    # print(loc)
    by_angle = make_angle_map(loc, asteroids)
    # print(by_angle)
    nuked = nuke_in_order(asteroids, by_angle)
    # print(nuked)
    print(nuked[200 - 1])

    # 1002 = too low
