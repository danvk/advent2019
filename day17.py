#!/usr/bin/env python

from collections import defaultdict
import fileinput
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


def print_area(area, dx=0, dy=0):
    s = area
    minx = min(x for (x, y) in s)
    maxx = max(x for (x, y) in s)
    miny = min(y for (x, y) in s)
    maxy = max(y for (x, y) in s)

    for y in range(maxy, miny - 1, -1):
        for x in range(minx, maxx + 1):
            print(s.get((x, y)), end='')
        print('')


def read_memory(inp):
    text = ''.join(line for line in inp)
    return [int(x) for x in text.split(',')]


def make_grid(asciis):
    grid = {}
    x = 0
    y = 0
    scaffolds = {'#', '^', '<', '>', 'v'}
    for c in asciis:
        if c == 10:
            x = 0
            y += 1
            continue
        elif chr(c) in scaffolds:
            grid[(x, y)] = '#'
        x += 1

    return grid


def is_intersect(grid, x, y):
    return (
        grid.get((x, y)) == '#' and
        grid.get((x + 1, y)) == '#' and
        grid.get((x - 1, y)) == '#' and
        grid.get((x, y - 1)) == '#' and
        grid.get((x, y + 1)) == '#'
    )


def sum_alignments(grid):
    tally = 0
    for (x, y) in grid.keys():
        if is_intersect(grid, x, y):
            tally += x * y
    return tally


def read_grid(inp):
    grid = {}
    robot = None
    for y, line in enumerate(inp):
        line = line.strip()
        for x, ch in enumerate(line):
            if ch == '#':
                grid[(x, y)] = 1
            if ch == '^':
                robot = (x, y)
    assert robot
    return robot, grid


DXDY = [
    (0, -1),  # up = default
    (1, 0),  # right
    (0, 1),  # down
    (-1, 0),  # left
]


def trace(robot, grid, d):
    d = 0
    x, y = robot
    while grid:
        left_dx, left_dy = DXDY[(d - 1) % 4]
        right_dx, right_dy = DXDY[(d + 1) % 4]
        if grid.get((x + left_dx, y + left_dy)):
            print('L')
            d = (d - 1) % 4
        elif grid.get((x + right_dx, y + right_dy)):
            print('R')
            d = (d + 1) % 4
        else:
            raise ValueError('Nowhere to turn!')

        n = 0
        dx, dy = DXDY[d]
        while True:
            nx = x + dx
            ny = y + dy
            if (nx, ny) not in grid:
                break
            n += 1
            # del grid[(nx, ny)]
            x, y = nx, ny
        print(n)


if __name__ == '__main__':
    # inp = fileinput.input()
    # robot, grid = read_grid(inp)
    # trace(robot, grid, 0)
    inp = open('inputs/day17.txt')
    memory = read_memory(inp)
    assert memory[0] == 1
    memory[0] = 2  # wake up
    program = IntCode(memory)
    program.inputs = [ord(c) for c in ''.join(open('data/day17.seq.txt'))]
    # explore(droid)
    outputs = program.run()
    print(outputs)
    # print(''.join(chr(x) for x in outputs))
    # grid = make_grid(outputs)
    # print(grid)
    # print(sum_alignments(grid))
    # print_hull(program.colors)
    # print(len(program.colors))
    # area = eval(open('area.txt').read())
    # print_area(area, dx=0, dy=0)
    # oxygen = find_oxygen(area)
    # bfs(area, oxygen)
