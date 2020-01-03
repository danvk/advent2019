#!/usr/bin/env python

import fileinput


def read_orbit(line):
    a, b = line.strip().split(')')
    return a, b


def make_orbit_map(orbits):
    parent = {}
    for big, small in orbits:
        parent[small] = big
    return parent


def num_direct_and_indirect(orbit_map, obj):
    num = 0
    while obj in orbit_map:
        num += 1
        obj = orbit_map[obj]
    return num


def trace_back(orbit_map, start):
    ds = {start: 0}
    n = 1
    while start in orbit_map:
        start = orbit_map[start]
        ds[start] = n
        n += 1
    return ds


def distance_to_santa(orbit_map):
    you_ds = trace_back(orbit_map, orbit_map['YOU'])
    santa_ds = trace_back(orbit_map, orbit_map['SAN'])
    return min(
        (you_ds[k] + santa_ds[k], k)
        for k in you_ds if k in santa_ds
    )[0]


if __name__ == '__main__':
    orbits = [read_orbit(line) for line in fileinput.input()]
    orbit_map = make_orbit_map(orbits)
    print(distance_to_santa(orbit_map))
