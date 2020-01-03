#!/usr/bin/env python

from collections import defaultdict
import fileinput
import networkx as nx


def is_letter(v):
    return v and 'A' <= v <= 'Z'


DELTAS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1)
]


def get_portal(grid, x, y):
    for dx, dy in DELTAS:
        a = (x + dx, y + dy)
        let1 = grid.get(a)
        if is_letter(let1):
            b = (x + 2 * dx, y + 2 * dy)
            return ''.join(grid.get(x) for x in sorted([a, b]))
    return None


def minmax(g):
    xs = [x for x, y in g.keys()]
    ys = [y for x, y in g.keys()]
    return (min(xs), max(xs)), (min(ys), max(ys))


def sort_portals(ab,  maxx, maxy):
    """Returns portals in (inner, outer) order."""
    (ax, ay), (bx, by) = ab
    ba = ab[1], ab[0]
    if ax == 2 or ay == 2 or ax == maxx - 2 or ay == maxy - 2:
        return ba
    elif bx == 2 or by == 2 or bx == maxx - 2 or by == maxy - 2:
        return ab
    raise ValueError(f'Cannot sort portals {ab}')


def read_graph(letters):
    max_level = 100
    # Read the # and .
    grid = {}
    for y, row in enumerate(letters):
        for x, c in enumerate(row):
            if c == '.' or is_letter(c):
                grid[(x, y)] = c

    (minx, maxx), (miny, maxy) = minmax(grid)
    assert minx == 0
    assert miny == 0

    # Find the portals
    portals = defaultdict(list)
    for xy, c in grid.items():
        if c != '.':
            continue
        x, y = xy
        p = get_portal(grid, x, y)
        if p:
            portals[p].append(xy)

    g = nx.Graph()
    for xy, v in grid.items():
        if v != '.':
            continue
        x, y = xy
        for dx, dy in DELTAS:
            nx_ = x + dx
            ny = y + dy
            n = (nx_, ny)
            if grid.get(n) == '.':
                for level in range(max_level):
                    g.add_edge((x, y, level), (nx_, ny, level))

    for p, nodes in portals.items():
        if p in ('AA', 'ZZ'):
            continue
        assert len(nodes) == 2, p

        inner, outer = sort_portals(nodes, maxx, maxy)
        for level in range(max_level - 1):
            g.add_edge((*inner, level), (*outer, level + 1))

    assert len(portals['AA']) == 1
    assert len(portals['ZZ']) == 1

    return g, (*portals['AA'][0], 0), (*portals['ZZ'][0], 0)


if __name__ == '__main__':
    inp = fileinput.input()
    letters = [[c for c in line if c != '\n'] for line in inp]
    g, start, stop = read_graph(letters)
    # path = nx.shortest_path_length(g, start, stop)
    path = nx.shortest_path(g, start, stop)
    print('Length:', len(path))
    print('Max level:', max(z for x, y, z in path))
    # print(nx.shortest_path(g, start, stop))
