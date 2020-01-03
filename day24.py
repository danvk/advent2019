#!/usr/bin/env python

import fileinput


DXDY = [
    (-1, 0),
    (1, 0),
    (0, 1),
    (0, -1)
]


def neighbors(x, y, z):
    for dx, dy in DXDY:
        nx = x + dx
        ny = y + dy

        if nx == 2 and ny == 2:
            # increase depth 1
            xy = (x, y)
            if xy == (1, 2):
                for i in range(5):
                    yield (0, i, z + 1)
            elif xy == (2, 1):
                for i in range(5):
                    yield (i, 0, z + 1)
            elif xy == (2, 3):
                for i in range(5):
                    yield (i, 4, z + 1)
            elif xy == (3, 2):
                for i in range(5):
                    yield (4, i, z + 1)
            else:
                raise ValueError('surprise')
        elif nx < 0:
            yield (1, 2, z - 1)  # decrease depth 1
        elif nx > 4:
            yield (3, 2, z - 1)  # increase depth 1
        elif ny < 0:
            yield (2, 1, z - 1)  # increase depth 1
        elif ny > 4:
            yield (2, 3, z - 1)  # increase depth 1
        else:
            yield (nx, ny, z)  # normal


def read_grid(inp):
    grid = {}
    for y, line in enumerate(inp):
        line = line.strip()
        for x, ch in enumerate(line):
            if ch == '#':
                grid[(x, y, 0)] = 1
    return grid


def minmaxz(g):
    zs = [z for x, y, z in g.keys()]
    return min(zs), max(zs)


def print_grid(g):
    # print(grid_to_str(g))
    minz, maxz = minmaxz(g)
    for z in range(minz, maxz + 1):
        print(f'Depth {z}:')
        for y in range(5):
            for x in range(5):
                c = '.'
                if (x, y) == (2, 2):
                    c = '?'
                elif g.get((x, y, z)):
                    c = '#'
                print(c, end='')
            print()
        print()


def grid_to_str(g):
    return '\n'.join(
        (''.join('#' if g[(x, y)] else '.' for x in range(5)))
        for y in range(5)
    )


def biodiversity_score(g):
    n = 1
    tot = 0
    for y in range(5):
        for x in range(5):
            if g[(x, y)]:
                tot += n
            n *= 2
    return tot


def step(grid):
    ng = {}
    minz, maxz = minmaxz(grid)

    for z in range(minz - 1, maxz + 2):
        for x in range(5):
            for y in range(5):
                if (x, y) == (2, 2):
                    continue
                n = sum(grid.get(node, 0) for node in neighbors(x, y, z))
                ch = grid.get((x, y, z), 0)
                if n == 1 or (ch == 0 and n == 2):
                    ng[(x, y, z)] = 1

    return ng


def count_bugs(g):
    return sum(
        c
        for (x, y, z), c in g.items()
        if (x, y) != (2, 2)
    )


if __name__ == '__main__':
    inp = fileinput.input()
    g = read_grid(inp)
    print_grid(g)
    for i in range(200):
        g = step(g)
    # print_grid(g)

    print(count_bugs(g))
