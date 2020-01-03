"""The elves' favorite computer."""

from collections import defaultdict


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


def read_memory(inp):
    text = ''.join(line for line in inp)
    return [int(x) for x in text.split(',')]


def read_program(inp) -> IntCode:
    return IntCode(read_memory(inp))
