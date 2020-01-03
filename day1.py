#!/usr/bin/env python

import fileinput


def get_fuel(mass):
    return mass // 3  - 2


def get_total_fuel(mass):
    """Fuel for mass + fuel for fuel + fuel for fuel for fuel, etc."""
    total_fuel = 0

    while True:
        additional_fuel = get_fuel(mass)
        if additional_fuel <= 0:
            break
        total_fuel += additional_fuel
        mass = additional_fuel

    return total_fuel


def sum_fuel(inp):
    return sum(get_total_fuel(int(line)) for line in inp)


if __name__ == '__main__':
    print(sum_fuel(fileinput.input()))
