#!/usr/bin/env python

from collections import defaultdict
import fileinput
from heapq import heappop, heappush, heapify
import math
import time
from typing import List


ENTRANCE = "@"
OPEN = "."
WALL = "#"
ENTRANCES = (ENTRANCE, '1', '2', '3', '4')

# keys = lowercase
# doors = uppercase
# collecting a unlocks A


MOVES = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]


def is_key(v):
    return "a" <= v <= "z"


def is_door(v):
    return "A" <= v <= "Z"


class Grid:
    def __init__(self, chars):
        self.grid = {}
        self.key_to_loc = {}
        self.door_to_loc = {}
        for y, row in enumerate(chars):
            for x, v in enumerate(row):
                xy = (x, y)
                self.grid[xy] = v
                if is_key(v):
                    self.key_to_loc[v] = xy
                elif is_door(v):
                    self.door_to_loc[v] = xy
                elif v == ENTRANCE:
                    self.entrance = xy
        self.num_keys = len(self.key_to_loc)

    def path_to_keys(self, xy, keys_in_hand):
        """Returns sorted list of (key, distance) pairs."""
        reached = set([xy])
        d = 0
        fringe = set([xy])
        g = self.grid
        new_keys = []

        def unexplored_neighbors(x, y):
            for (dx, dy) in MOVES:
                n = (x + dx, y + dy)
                v = g.get(n)
                if v == WALL or n in reached:
                    continue
                if (
                    v == OPEN
                    or is_key(v)
                    or (is_door(v) and v.lower() in keys_in_hand)
                    or v in ENTRANCES
                ):
                    yield n

        while fringe:
            d += 1
            new_cells = set()
            for x, y in fringe:
                new_cells.update(unexplored_neighbors(x, y))

            for c in new_cells:
                v = g.get(c)
                if is_key(v) and v not in keys_in_hand:
                    new_keys.append((v, d))

            fringe = new_cells
            reached.update(new_cells)

        return new_keys

    def all_paths(self, key, xy=None):
        """Returns a map from other key --> (distance, keys req for path)."""
        if not xy:
            xy = self.key_to_loc[key]
        reached = set([xy])
        d = 0
        fringe = [(xy, [])]  # list of (node, doors crossed)
        g = self.grid
        new_keys = {}

        def unexplored_neighbors(x, y):
            for (dx, dy) in MOVES:
                n = (x + dx, y + dy)
                v = g.get(n)
                if v == WALL or n in reached:
                    continue
                if is_door(v):
                    yield n, v
                if v == OPEN or is_key(v) or v in ENTRANCES:
                    yield n, None

        while fringe:
            d += 1
            new_fringe = []
            for (x, y), doors in fringe:
                for c, door in unexplored_neighbors(x, y):
                    reached.add(c)
                    v = g.get(c)
                    new_doors = doors + ([door] if door else [])
                    if is_key(v):
                        new_keys[v] = (d, {d.lower() for d in new_doors})
                    new_fringe.append((c, new_doors))

            fringe = new_fringe

        return new_keys

    def compartmentalize(self):
        # ...     @#@
        # .@.  -> ###
        # ...     @#@
        x, y = self.entrance
        g = self.grid
        g[(x - 1, y - 1)] = '1'
        g[(x + 0, y - 1)] = '#'
        g[(x + 1, y - 1)] = '2'
        g[(x - 1, y + 0)] = '#'
        g[(x + 0, y + 0)] = '#'
        g[(x + 1, y + 0)] = '#'
        g[(x - 1, y + 1)] = '3'
        g[(x + 0, y + 1)] = '#'
        g[(x + 1, y + 1)] = '4'
        self.is_compartmentalized = True

    def build_path_cache(self):
        """Compute all pairs distance between keys."""
        self.key_cache = {}
        for k in self.key_to_loc.keys():
            self.key_cache[k] = self.all_paths(k)
        if not self.is_compartmentalized:
            self.key_cache[ENTRANCE] = {
                k: (d, set())
                for k, d in self.path_to_keys(self.entrance, set())
            }
        else:
            x, y = self.entrance
            entrances = {
                '1': (x - 1, y - 1),
                '2': (x + 1, y - 1),
                '3': (x - 1, y + 1),
                '4': (x + 1, y + 1),
            }
            for eid, pos in entrances.items():
                self.key_cache[eid] = self.all_paths(None, pos)
        # self.key_to_loc[ENTRANCE] = self.entrance


# State = namedtuple('State', ['steps', 'keyseq'])
# State = (steps, current keys, key sequence)

def state_repr(state):
    return (state[0], state[1], ''.join(sorted(state[2])))


def uniqify(states):
    by_keys = defaultdict(list)
    for state in states:
        steps, current, keyseq = state
        k = (current, ''.join(sorted(keyseq)))
        by_keys[k].append(state)

    out = [min(vs) for vs in by_keys.values()]
    # print(f'{num_uniq - len(out):6} by dominance.')

    heapify(out)
    return out


def explore(grid: Grid, states: List, max_steps):
    last_steps = None
    last_time = time.time()
    num_pruned = 0
    while states:
        state = heappop(states)
        steps, current, keyseq = state
        if len(keyseq) == grid.num_keys:
            return steps

        keys_in_hand = set(keyseq)

        if steps != last_steps:
            states = uniqify(states)
            t = time.time()
            print(f'Steps: {steps}, len(states)={len(states)}, pruned={num_pruned} {t - last_time:.2} s')
            last_steps = steps
            last_time = t
            num_pruned = 0

        for c in current:  # each robot can potentially make the next move
            next_keys = grid.key_cache[c]
            for k, (d, keys_needed) in next_keys.items():
                if k in keys_in_hand:
                    continue
                if not keys_in_hand.issuperset(keys_needed):
                    continue
                new_steps = steps + d
                if new_steps > max_steps:
                    num_pruned += 1
                    continue
                new_current = current.replace(c, k)
                new_state = (new_steps, new_current, keyseq + k)
                # print(f'{state} --> {new_state}')
                heappush(states, new_state)


if __name__ == "__main__":
    inp = fileinput.input()
    # inp = open('/tmp/day18.part2.1.txt')
    chars = [[*line.strip()] for line in inp]
    g = Grid(chars)
    g.compartmentalize()
    g.build_path_cache()

    print(explore(g, [(0, '1234', '')], math.inf))

# 5112 = too high
# 4928 = too high
# 4816 = too high
# 4700 = correct

# 60 steps in 7:28.58

# Part 2:
# 3000 = too high
