#!/usr/bin/env python

import fileinput
import sys


ADD = 1
MULTIPLY = 2
STOP = 99


def run_program(memory):
    instruct_ptr = 0
    while True:
        opcode = memory[instruct_ptr]
        if opcode == STOP:
            break
        parameters = memory[instruct_ptr + 1:instruct_ptr + 4]

        in0_addr, in1_addr, out_addr = parameters
        in0 = memory[in0_addr]
        in1 = memory[in1_addr]
        if opcode == ADD:
            out = in0 + in1
        elif opcode == MULTIPLY:
            out = in0 * in1
        else:
            raise ValueError(f'Invalid opcode: {opcode}')

        memory[out_addr] = out
        instruct_ptr += 1 + len(parameters)

    return memory[0]


def read_memory(inp):
    text = ''.join(line for line in inp)
    return [int(x) for x in text.split(',')]


def replace_gravity_assist(memory, noun, verb):
    memory[1] = noun
    memory[2] = verb


def find_inputs(init_memory, target_value):
    for total in range(0, 200):
        for verb in range(0, 1 + total):
            noun = total - verb
            memory = init_memory[:]
            replace_gravity_assist(memory, noun, verb)
            run_program(memory)
            output = memory[0]
            sys.stderr.write(f'{noun} {verb} -> {output}\n')
            if output == target_value:
                return (noun, verb)


if __name__ == '__main__':
    memory = read_memory(fileinput.input())
    print(find_inputs(memory, target_value=19690720))
