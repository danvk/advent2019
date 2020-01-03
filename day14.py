#!/usr/bin/env python

import fileinput
import itertools
import math
import re


def parse_component(comp):
    """Parse "10 ORE" -> (10, 'ORE')."""
    m = re.match(r'(\d+) ([A-Z]+)$', comp)
    assert m, comp
    amt, what = m.groups()
    return int(amt), what


def read_reactions(inp):
    """Returns map from product -> (amount, inputs).

    inputs is a list of (amount, what) pairs.
    """
    reactions = {}
    products = set()
    for line in inp:
        line = line.strip()
        inp, out = line.split(' => ')
        amt, product = parse_component(out)
        assert product not in products
        products.add(product)
        reactions[product] = (
            amt,
            [parse_component(c) for c in inp.split(', ')]
        )
    return reactions


def waste(chemical, amount, reactions):
    if chemical == 'ORE':
        return math.inf  # We can't produce ORE
    produce_amt = reactions[chemical][0]
    mult = math.ceil(amount / produce_amt)
    return mult * produce_amt - amount


def find_generations(reactions):
    """Returns a map from chemical --> generation."""
    generation = 0
    gens = {'ORE': generation}

    while True:
        generation += 1
        new_produce = {}
        for product, (_, inputs) in reactions.items():
            if product in gens:
                continue
            if all(c in gens for _, c in inputs):
                new_produce[product] = generation

        if not len(new_produce):
            break
        print(generation, new_produce)
        gens.update(new_produce)

    return gens


num_calls = 0
num_prune = 0


def min_ore_needed(
    reactions,
    needs,
    generations,
):
    global num_calls

    if len(needs) == 1 and 'ORE' in needs:
        return needs['ORE']

    num_calls += 1

    # Produce all the highest-generation chemicals first.
    # There is no other way to produce them.
    highest_gen = max(generations[n] for n in needs.keys())
    highest_needs = [n for n in needs.keys() if generations[n] == highest_gen]

    for need in highest_needs:
        need_amt = needs[need]

        produce_amt, inputs = reactions[need]
        k = math.ceil(need_amt / produce_amt)

        for inp_amt, inp in inputs:
            needs[inp] = needs.get(inp, 0) + k * inp_amt
        del needs[need]

    return min_ore_needed(reactions, needs, generations)


def min_ore_for_fuel(reactions, generations, fuel):
    return min_ore_needed(reactions, {'FUEL': fuel}, generations)


def bsearch(low, hi, target, fn):
    # range is inclusive
    while hi > low:
        x = (low + hi) // 2
        v = fn(x)
        if v < target:
            low = x + 1
        elif v > target:
            hi = x - 1
        else:
            return x
    return low


if __name__ == '__main__':
    inp = fileinput.input()
    reactions = read_reactions(inp)
    amt, inputs = reactions['FUEL']
    assert amt == 1
    generations = find_generations(reactions)

    fuel = bsearch(
        1, 1e12, 1e12,
        lambda fuel: min_ore_for_fuel(reactions, generations, fuel)
    )

    print(fuel - 1, min_ore_for_fuel(reactions, generations, fuel - 1))
    print(fuel + 0, min_ore_for_fuel(reactions, generations, fuel))
    print(fuel + 1, min_ore_for_fuel(reactions, generations, fuel + 1))

    # print(generations)
    # needs = {'FUEL': 1}
    # print(min_ore_needed(reactions, needs, generations))
    # print(f'Calls / prunes: {num_calls} / {num_prune}')
