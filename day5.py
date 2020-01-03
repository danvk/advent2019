#!/usr/bin/env python

import fileinput


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


def run_program(memory, inputs):
    instruct_ptr = 0
    inputs = iter(inputs)
    outputs = []

    while True:
        instruction = memory[instruct_ptr]
        opcode, modes = decode_instruction(instruction)

        if opcode == STOP:
            break

        num_params = len(modes)
        parameters = memory[instruct_ptr + 1:instruct_ptr + 1 + num_params]

        vals = [
            v if mode == MODE_IMM else memory[v]
            for v, mode in zip(parameters, modes)
        ]

        instruct_ptr += 1 + len(parameters)

        if opcode == ADD:
            memory[parameters[2]] = vals[0] + vals[1]
        elif opcode == MULTIPLY:
            memory[parameters[2]] = vals[0] * vals[1]
        elif opcode == INPUT:
            val = next(inputs)
            memory[parameters[0]] = val
        elif opcode == OUTPUT:
            outputs.append(vals[0])
        elif opcode == JUMP_IF_TRUE:
            if vals[0] != 0:
                instruct_ptr = vals[1]
        elif opcode == JUMP_IF_FALSE:
            if vals[0] == 0:
                instruct_ptr = vals[1]
        elif opcode == LESS_THAN:
            memory[parameters[2]] = 1 if vals[0] < vals[1] else 0
        elif opcode == EQUALS:
            memory[parameters[2]] = 1 if vals[0] == vals[1] else 0
        else:
            raise ValueError(f'Invalid opcode: {opcode}')

    return outputs


def read_memory(inp):
    text = ''.join(line for line in inp)
    return [int(x) for x in text.split(',')]


if __name__ == '__main__':
    memory = read_memory(fileinput.input())
    print(run_program(memory, [5]))
