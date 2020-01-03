#!/usr/bin/env python

import fileinput
import time

import numpy as np


BASE_PATTERN = [0, 1, 0, -1]


def digits(x):
    return np.asarray([int(d) for d in str(x)])


def fft(inputs):
    N = len(inputs)
    # cumsum = [0] * N
    # cumsum[0] = inputs[0]
    # for i in range(1, N):
    #     cumsum[i] = cumsum[i - 1] + inputs[i]

    # cumsum[i] = sum of inputs[x<=i]
    cumsum = np.cumsum(inputs)
    out = np.zeros(N)  # [0] * N

    out[0] = ones(
        inputs[0:N:4].sum() - inputs[2:N:4].sum()
    )

    for i in range(1, N):
        stride = i
        offset = 0
        base_i = 0
        tally = 0
        while offset < N:
            k = BASE_PATTERN[base_i]
            if k:
                top = cumsum[offset + stride - 1] if offset + stride <= N else cumsum[-1]
                bottom = cumsum[offset - 1] if offset > 0 else 0
                tally += k * (top - bottom)
            base_i = (base_i + 1) % len(BASE_PATTERN)
            offset += stride
            stride = i + 1
        out[i] = abs(tally) % 10

    return out


def ones(x):
    return abs(x) % 10


# Seems to only be obvious repeating patterns in the last few digits.
# Idea: precompute all sums and distribute the multiplication.
#       this should linearize the calculation.

if __name__ == '__main__':
    signal = digits(''.join(fileinput.input()).strip())
    # signal = [*chain(*repeat(signal, 10))]
    print(signal)
    offset = int(''.join(str(d) for d in signal[0:7]))
    print(offset)
    signal = np.tile(signal, 10_000)
    for i in range(0, 100):
        start_t = time.time()
        signal = fft(signal)
        print(f'Completed {i} FFTs, ∆t = {time.time() - start_t:.2}s')
        # print(signal)

    output = signal[offset:offset + 8]

    print(''.join(str(int(d)) for d in output))
