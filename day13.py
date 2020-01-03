#!/usr/bin/env python

import curses
import fileinput
import json
import os
import time
import sys

from intcode import IntCode, read_memory


TILE_EMPTY = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_H_PADDLE = 3
TILE_BALL = 4

REPRS = {
    TILE_EMPTY: ' ',
    TILE_WALL: 'W',
    TILE_BLOCK: 'x',
    TILE_H_PADDLE: '-',
    TILE_BALL: 'o',
}


class ArcadeCabinet(IntCode):
    def __init__(self, memory):
        super().__init__(memory)
        self.x = 0
        self.y = 0
        self.which = 0
        self.score = 0
        self.screen = None
        self.paddle = None
        self.ball = None
        self.last_hit = None
        self.screen_contents = {}
        self.log = open(f'data/breakout.{int(time.time())}.log.txt', 'w')

    def pop_input(self):
        k = self.screen.getch()
        if k == ord('j'):  # J
            return -1
        elif k == ord('k'):  # K
            return +1
        elif k == ord('s'):
            self.save()
        return 0

    def output(self, val):
        if self.which == 0:
            self.x = val
        elif self.which == 1:
            self.y = val
        elif self.which == 2:
            x, y = self.x, self.y
            if x == -1 and y == 0:
                self.score = val
                self.screen.addstr(0, 45, f'Score: {self.score}')
                self.screen.refresh()
                self.log.write(f'Score\t{self.score}\n')
                self.log.flush()
            else:
                # x: [0, 40]
                # y: [0, 24]
                c = REPRS.get(val, ' ')

                if c == ' ' and self.screen_contents.get((x, y)) == 'x':
                    self.log.write(f'Break\t{x}\t{y}\n')
                if c == 'o':
                    self.log.write(f'Ball\t{x}\t{y}\n')

                self.screen_contents[(x, y)] = c
                self.screen.addch(y, x, ord(c))
                self.screen.refresh()
                if val == TILE_BALL:
                    # if y > 10:
                    time.sleep(0.5)
                    # else:
                    #    time.sleep(0.1)
                    if self.paddle and self.ball:
                        px, py = self.paddle
                        pbx, pby = self.ball
                        dx, dy = x - pbx, y - pby
                        if dy > 0:
                            # find where it would hit the paddle
                            hit_x = int(round(pbx + dx * (py - pby) / dy))
                            if hit_x <= 0:
                                hit_x = 1 - hit_x
                            if hit_x > 40:
                                hit_x = 40 - hit_x
                            hit_x = max(0, min(40, hit_x))
                            if hit_x != px and hit_x != self.last_hit:
                                if self.last_hit:
                                    self.screen.addch(py, hit_x, ord(' '))
                                self.screen.addch(py, hit_x, ord('.'))
                                self.last_hit = hit_x

                            # if y > 15:
                            #    time.sleep(0.5)
                        else:
                            self.last_hit = None
                    self.ball = (x, y)
                elif val == TILE_H_PADDLE:
                    self.paddle = (x, y)
            # self.screen[(self.x, self.y)] = val
        self.which = (self.which + 1) % 3

    def num_blocks(self):
        return sum(1 for v in self.screen.values() if v == TILE_BLOCK)

    def save(self):
        obj = {
            'mem': self.memory,
            'scr': [
                (x, y, c) for (x, y), c in self.screen_contents.items()
            ],
            'x': self.x,
            'y': self.y,
            'i': self.instruction_ptr,
        }
        with open('data/breakout.json', 'w') as f:
            json.dump(obj, f)
        with open(f'data/breakout.{self.score}.json', 'w') as f:
            json.dump(obj, f)


def address_for_block_intcode(x, y):
    # a = 429
    c = 25 * x + y
    print('c', c)
    d = 521
    e = 1011
    # f = 1025
    # b = 630
    g = c * d
    g = g + e
    print('g', g)
    # e = e + g
    g = g % (64 * 1025)
    print('g', g)
    g = g % (8 * 1025)
    print('g', g)
    g = g % 1025
    print('g', g)
    return 1664 + g


def address_for_block(x, y):
   return 1664 + ((((((25 * x + y) * 521) + 1011) % (64 * 1025)) % (8 * 1025)) % 1025)

# sum(memory[day13.address_for_block(x, y)] for x in range(0, 41) for y in range(0, 25) if tiles[41 * y + x] == 2)

if __name__ == '__main__':
    restore_from_saved = False

    if not restore_from_saved:
        # inp = fileinput.input()
        inp = open('inputs/day13.txt')
        memory = read_memory(inp)
        memory[0] = 2  # play for free
    # memory = [104, 1125899906842624, 99]
    else:
        obj = json.load(open('data/breakout.json'))
        memory = {}
        for k, v in obj['mem'].items():
            memory[int(k)] = v

    os.system('clear')
    screen = curses.initscr()
    screen.nodelay(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    if restore_from_saved:
        for x, y, v in obj['scr']:
            screen.addch(y, x, v)
    screen.refresh()

    program = ArcadeCabinet(memory)
    program.screen = screen
    if restore_from_saved:
        program.screen_contents = {
            (x, y): c for (x, y, c) in obj['scr']
        }
        program.instruction_ptr = obj['i']
        program.x = obj['x']
        program.y = obj['y']

    program.run()

# 11414 = too high
# 11296 = too high
# 11140 = correct!
# 10800 = too low
