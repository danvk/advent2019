#!/usr/bin/env python

import fileinput
import sys

import intcode


class NIC(intcode.IntCode):
    def __init__(self, code, id_):
        super().__init__(code)
        self.id = id_
        self.inputs = [id_]
        self.packet = []
        self.others = []
        self.nat = None
        self.is_idle = False

    def pop_input(self):
        if self.inputs:
            self.is_idle = False
            return super().pop_input()
        self.is_idle = True
        return -1

    def receive_packet(self, x, y):
        self.inputs.append(x)
        self.inputs.append(y)
        self.is_idle = False

    def output(self, value):
        self.is_idle = False
        self.packet.append(value)
        if len(self.packet) == 3:
            addr, x, y = self.packet
            self.packet = []
            print(f'{self.id} -> addr={addr}, x={x}, y={y}')
            if addr == 255:
                self.nat.receive_packet(x, y)
            else:
                self.others[addr].receive_packet(x, y)


class NAT(intcode.IntCode):
    def __init__(self, nics):
        self.nics = nics
        self.packet = None
        self.last_y = None

    def receive_packet(self, x, y):
        self.packet = (x, y)

    def send_if_idle(self):
        if all(nic.is_idle for nic in self.nics):
            if not self.packet:
                print('Would de-idle but no packet')
                return
            x, y = self.packet
            print(f'NAT is de-idling {x} {y}')
            nics[0].receive_packet(x, y)
            if y == self.last_y:
                print(f'Delivered {y} twice in a row')
                sys.exit(0)
            self.last_y = y


if __name__ == '__main__':
    memory = intcode.read_memory(fileinput.input())
    nics = [NIC(memory, i) for i in range(50)]
    nat = NAT(nics)

    for nic in nics:
        nic.others = nics
        nic.nat = nat

    step = 0
    while True:
        for nic in nics:
            nic.run_one_instruction()
        nat.send_if_idle()

        step += 1
        if step % 10_000 == 0:
            print(f'Completed {step} steps...')
