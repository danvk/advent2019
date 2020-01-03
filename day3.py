#!/usr/bin/env python

import fileinput

DELTAS = {
    'U': (0, 1),
    'D': (0, -1),
    'L': (-1, 0),
    'R': (1, 0),
}


def trace(path):
    x, y = 0, 0
    grid = {}
    n = 1
    for direction, d in path:
        dx, dy = DELTAS[direction]
        for i in range(0, d):
            x += dx
            y += dy
            xy = (x, y)
            if xy not in grid:
                grid[xy] = n
            n += 1
    return grid


def parse_path(path_str):
    return [(part[0], int(part[1:])) for part in path_str.split(',')]


def manhattan(xy):
    return abs(xy[0]) + abs(xy[1])


def find_intersections(grid1, grid2):
    return [
        *sorted((
            (grid1[xy] + grid2[xy], xy)
            for xy in grid1.keys()
            if xy in grid2)
        )
    ]


if __name__ == '__main__':
    wires = [parse_path(line) for line in fileinput.input()]
    wire1, wire2 = wires
    ixns = find_intersections(trace(wire1), trace(wire2))

    print(ixns)
