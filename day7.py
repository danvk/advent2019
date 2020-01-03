#!/usr/bin/env python

import fileinput
import itertools


ADD = 1
MULTIPLY = 2
INPUT = 3
OUTPUT = 4
JUMP_IF_TRUE = 5
JUMP_IF_FALSE = 6
LESS_THAN = 7
EQUALS = 8
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
    STOP: 0
}

MODE_POS = 0
MODE_IMM = 1


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
        self.memory = memory[:]
        self.instruction_ptr = 0
        self.inputs = inputs or []
        self.outputs = []
        self.is_halted = False

    def pop_input(self):
        v, *rest = self.inputs
        self.inputs = rest
        return v

    def run_one_instruction(self):
        m = self.memory
        instruction = m[self.instruction_ptr]
        opcode, modes = decode_instruction(instruction)

        if opcode == STOP:
            self.is_halted = True
            return

        num_params = len(modes)
        parameters = m[
            self.instruction_ptr + 1:self.instruction_ptr + 1 + num_params
        ]

        vals = [
            v if mode == MODE_IMM else m[v]
            for v, mode in zip(parameters, modes)
        ]

        self.instruction_ptr += 1 + len(parameters)

        if opcode == ADD:
            m[parameters[2]] = vals[0] + vals[1]
        elif opcode == MULTIPLY:
            m[parameters[2]] = vals[0] * vals[1]
        elif opcode == INPUT:
            val = self.pop_input()
            m[parameters[0]] = val
        elif opcode == OUTPUT:
            self.outputs.append(vals[0])
        elif opcode == JUMP_IF_TRUE:
            if vals[0] != 0:
                self.instruction_ptr = vals[1]
        elif opcode == JUMP_IF_FALSE:
            if vals[0] == 0:
                self.instruction_ptr = vals[1]
        elif opcode == LESS_THAN:
            m[parameters[2]] = 1 if vals[0] < vals[1] else 0
        elif opcode == EQUALS:
            m[parameters[2]] = 1 if vals[0] == vals[1] else 0
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


def run_amps(memory, phase_settings):
    signal = 0
    amps = [IntCode(memory, inputs=[setting]) for setting in phase_settings]

    is_halted = False
    while not is_halted:
        for i, amp in enumerate(amps):
            amp.inputs += [signal]
            next_signal = amp.run_to_output()
            if next_signal is None:
                is_halted = True
                break
            signal = next_signal

    return signal


if __name__ == '__main__':
    memory = read_memory(fileinput.input())
    print(max(
        (run_amps(memory, settings), settings)
        for settings in itertools.permutations(range(5, 10))
    ))
