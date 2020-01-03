#!/usr/bin/env python

from collections import defaultdict
# import fileinput
import json
import random


ADD = 1
MULTIPLY = 2
INPUT = 3
OUTPUT = 4
JUMP_IF_TRUE = 5
JUMP_IF_FALSE = 6
LESS_THAN = 7
EQUALS = 8
ADJUST_RELATIVE_BASE = 9
STOP = 99


NUM_PARAMS = {
    ADD: 3,
    MULTIPLY: 3,
    INPUT: 1,
    OUTPUT: 1,
    JUMP_IF_TRUE: 2,
    JUMP_IF_FALSE: 2,
    LESS_THAN: 3,
    EQUALS: 3,
    ADJUST_RELATIVE_BASE: 1,
    STOP: 0
}

MODE_POS = 0
MODE_IMM = 1
MODE_REL = 2


def decode_instruction(instruction):
    opcode = instruction % 100
    num_params = NUM_PARAMS[opcode]
    modes = [MODE_POS] * num_params
    instruction //= 100
    i = 0
    while instruction:
        modes[i] = instruction % 10
        instruction //= 10
        i += 1
    return opcode, modes


class IntCode:
    def __init__(self, memory, inputs=None):
        self.memory = defaultdict(int)
        self.memory.update(enumerate(memory))
        self.instruction_ptr = 0
        self.inputs = inputs or []
        self.outputs = []
        self.is_halted = False
        self.relative_base = 0

    def pop_input(self):
        v, *rest = self.inputs
        self.inputs = rest
        return v

    def output(self, value):
        self.outputs.append(value)

    def decode_param(self, v, mode):
        if mode == MODE_IMM:
            return v
        elif mode == MODE_POS:
            return self.memory[v]
        elif mode == MODE_REL:
            return self.memory[self.relative_base + v]
        raise ValueError(f'Invalid mode {mode}')

    def write_memory(self, parameter, mode, value):
        if mode == MODE_POS:
            self.memory[parameter] = value
        elif mode == MODE_REL:
            self.memory[self.relative_base + parameter] = value
        else:
            raise ValueError(f'Invalid mode for write: {mode}')

    def run_one_instruction(self):
        m = self.memory
        instruction = m[self.instruction_ptr]
        opcode, modes = decode_instruction(instruction)

        if opcode == STOP:
            self.is_halted = True
            return

        num_params = len(modes)
        parameters = [
            m[self.instruction_ptr + i]
            for i in range(1, 1 + num_params)
        ]

        vals = [
            self.decode_param(v, mode)
            for v, mode in zip(parameters, modes)
        ]

        self.instruction_ptr += 1 + len(parameters)

        if opcode == ADD:
            self.write_memory(parameters[2], modes[2], vals[0] + vals[1])
        elif opcode == MULTIPLY:
            self.write_memory(parameters[2], modes[2], vals[0] * vals[1])
        elif opcode == INPUT:
            val = self.pop_input()
            self.write_memory(parameters[0], modes[0], val)
        elif opcode == OUTPUT:
            self.output(vals[0])
        elif opcode == JUMP_IF_TRUE:
            if vals[0] != 0:
                self.instruction_ptr = vals[1]
        elif opcode == JUMP_IF_FALSE:
            if vals[0] == 0:
                self.instruction_ptr = vals[1]
        elif opcode == LESS_THAN:
            self.write_memory(
                parameters[2], modes[2],
                1 if vals[0] < vals[1] else 0
            )
        elif opcode == EQUALS:
            self.write_memory(
                parameters[2], modes[2],
                1 if vals[0] == vals[1] else 0
            )
        elif opcode == ADJUST_RELATIVE_BASE:
            self.relative_base += vals[0]
        else:
            raise ValueError(f'Invalid opcode: {opcode}')

    def run(self):
        """Run to halt. Returns outputs."""
        while not self.is_halted:
            self.run_one_instruction()

        return self.outputs

    def run_to_output(self):
        """Run until the program outputs.

        Returns that output or None if the program halts before output."""
        self.outputs = []
        while not self.is_halted and not self.outputs:
            self.run_one_instruction()

        return self.outputs[0] if self.outputs else None


DIR_N = 1
DIR_S = 2
DIR_W = 3
DIR_E = 4

DXDY = {
    DIR_N: (0, -1),
    DIR_S: (0, +1),
    DIR_W: (-1, 0),
    DIR_E: (+1, 0),
}

OPEN = 0
WALL = 1
OXYGEN = 2
REPRS = {
    OPEN: '.',
    WALL: '#',
    OXYGEN: 'o',
}


class RepairDroid(IntCode):
    def __init__(self, memory):
        super().__init__(memory)
        self.x = 0
        self.y = 0
        self.area = {(0, 0): OPEN}
        self.oxygen = None

    def exec(self, command):
        self.inputs = [command]
        dx, dy = DXDY[command]
        out = self.run_to_output()
        if out == 0:
            # Droid hit a wall.
            self.area[(self.x + dx, self.y + dy)] = WALL
        elif out == 1:
            # Droid moved one step
            self.x += dx
            self.y += dy
            self.area[(self.x, self.y)] = OPEN
        elif out == 2:
            self.x += dx
            self.y += dy
            self.area[(self.x, self.y)] = OXYGEN
            self.oxygen = (self.x, self.y)
        else:
            raise ValueError(f'Surprise output: {out}')

    def print_area(self):
        print_area(self.area, self.x, self.y)


def print_area(area, dx=0, dy=0):
    s = area
    minx = min(x for (x, y) in s)
    maxx = max(x for (x, y) in s)
    miny = min(y for (x, y) in s)
    maxy = max(y for (x, y) in s)
    print(f'x: [{minx}, {maxx}]')
    print(f'y: [{miny}, {maxy}]')

    for y in range(maxy, miny - 1, -1):
        for x in range(minx, maxx + 1):
            if x == dx and y == dy:
                c = 'D'
            elif x == 0 and y == 0:
                c = '0'
            else:
                c = REPRS.get(s.get((x, y)), ' ')
            print(c, end='')
        print('')


def read_memory(inp):
    text = ''.join(line for line in inp)
    return [int(x) for x in text.split(',')]


def open_neighbors(area):
    """Returns a list of coordinates for open cells."""
    openings = set()
    for (x, y), v in area.items():
        if v == WALL:
            continue
        for (dx, dy) in DXDY.values():
            n = (x + dx, y + dy)
            if n not in area:
                openings.add(n)
    return openings


def desire_trail(area, openings):
    # For each opening, do a flood fill
    fringe = [*openings]
    scores = {xy: 1000 for xy in openings}
    while fringe:
        xy = fringe.pop()
        score = scores[xy]
        ns = score - 1
        x, y = xy
        for (dx, dy) in DXDY.values():
            n = (x + dx, y + dy)
            if area.get(n) == OPEN and scores.get(n, -1e6) < ns:
                scores[n] = ns
                fringe.append(n)
    return scores


def explore(droid):
    # a = droid.area
    steps = 0

    # Start w/ some randomish exploration
    dirs = [*DXDY.keys()]
    for i in range(1_000_000):
        # Find the closest unexplored cell that we can get to via open cells.
        # x = droid.x
        # y = droid.y
        # n = {
        #     d: a.get(x + dx, y + dy)
        #     for d, (dx, dy) in DXDY.items()
        #     if a.get(x + dx, y + dy) != WALL
        # }
        # if not n:
        #     raise ValueError('Boxed in!')
        # d = min(
        #     n.keys(),
        #     key=lambda d: (0 if n[d] is None else 1, random.random())
        # )
        d = random.choice(dirs)
        droid.exec(d)
        steps += 1

        if steps % 10_000 == 0:
            print('------')
            print(steps)
            droid.print_area()
            with open('area.txt', 'w') as out:
                out.write(str(droid.area))

    print(droid.area)


def bfs(area, start):
    reached = set([start])
    d = 0
    fringe = set([start])

    def unexplored_neighbors(x, y):
        for (dx, dy) in DXDY.values():
            n = (x + dx, y + dy)
            v = area.get(n)
            if (v == OPEN or v == OXYGEN) and n not in reached:
                yield n

    while fringe:
        d += 1
        new_cells = set()
        for x, y in fringe:
            new_cells.update(unexplored_neighbors(x, y))

        for c in new_cells:
            if area.get(c) == OXYGEN:
                print(f'Found oxygen after {d} steps')

        fringe = new_cells
        reached.update(new_cells)
        print(f'{d} minutes, reached {len(reached)} cells')

    print(d)


def find_oxygen(area):
    for xy, v in area.items():
        if v == OXYGEN:
            return xy
    raise KeyError(f'No Oxygen!')


if __name__ == '__main__':
    # inp = fileinput.input()
    # inp = open('inputs/day15.txt')
    # memory = read_memory(inp)
    # memory = [104, 1125899906842624, 99]
    # droid = RepairDroid(memory)
    # explore(droid)
    # program.run()
    # print_hull(program.colors)
    # print(len(program.colors))
    area = eval(open('area.txt').read())
    print_area(area, dx=0, dy=0)
    oxygen = find_oxygen(area)
    bfs(area, oxygen)
