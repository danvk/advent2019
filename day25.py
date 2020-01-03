#!/usr/bin/env python

import fileinput
import intcode


class AsciiComputer(intcode.IntCode):
    def __init__(self, memory, inputs=None):
        super().__init__(memory, inputs=inputs)

        self.last_output = ''

    def output(self, value):
        c = chr(value)
        print(chr(value), end='')

        if self.last_output.endswith('\n'):
            self.last_output = c
        else:
            self.last_output += c

            if self.last_output == 'Command?':
                self.inputs = [ord(c) for c in input(' ')] + [10]


if __name__ == '__main__':
    code = intcode.read_memory(fileinput.input())
    droid = AsciiComputer(code)
    droid.run()
