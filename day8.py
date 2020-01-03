#!/usr/bin/env python

import fileinput

WIDTH = 25
HEIGHT = 6
# WIDTH = 2
# HEIGHT = 2


def make_layers(digits, width, height):
    """Returns a list of list of lists."""
    pix_per_layer = width * height
    assert len(digits) % pix_per_layer == 0

    def make_layer(ds):
        return {
            (i, j): int(ds[j * width + i])
            for i in range(0, width)
            for j in range(0, height)
        }

    return [
        make_layer(digits[base:base+pix_per_layer])
        for base in range(0, len(digits), pix_per_layer)
    ]


def merge_layers(layers):
    result = {}
    for layer in reversed(layers):
        for xy, v in layer.items():
            if v == 0 or v == 1:
                result[xy] = v
    return result


def print_layer(layer):
    for j in range(0, HEIGHT):
        print(
            ''.join(
                '*' if layer[(i, j)] == 1 else ' '
                # str(layer[(i, j)])
                for i in range(0, WIDTH)
            )
        )


if __name__ == '__main__':
    text = ''.join(line.strip() for line in fileinput.input())
    # text = '0222112222120000'
    layers = make_layers(text, WIDTH, HEIGHT)
    # for i in range(0, 4):
    #    print(i)
    #    print_layer(layers[i])

    layer = merge_layers(layers)
    print_layer(layer)
    # layer = least_zeroey_layer(layers)
    # print(layer)
    # print(layer[1] * layer[2])
