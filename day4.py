#!/usr/bin/env python

from itertools import groupby


def digits(x):
    return [int(d) for d in str(x)]


def is_six_digits(d):
    return len(d) == 6


def has_adjacent_pair(digits):
    return any(
        d
        for d, g in groupby(digits)
        if len([*g]) == 2
    )


def is_nondecreasing(d):
    return all(x <= y for x, y in zip(d[:-1], d[1:]))


def is_ok(num):
    d = digits(num)
    return is_six_digits(d) and has_adjacent_pair(d) and is_nondecreasing(d)


if __name__ == '__main__':
    num_ok = 0
    for num in range(246540, 787419 + 1):
        if is_ok(num):
            num_ok += 1

    print(num_ok)
