#!/usr/bin/env python

import fileinput

from intcode import read_program


'''
A & B & not C:
.................
.................
..@..............
#####.###########
   ABCDEFGHI

  do jump (D & E):
  .................
  .................
  ..@..............
  #####.##.########
     ABCDEFGHI

  do jump (D & not E & not F)
  .................
  .................
  ..@..............
  #####.#..########
     ABCDEFGHI
     110100111

  do jump: (D & H & not E & not G)
  .................
  .................
  ..@..............
  #####.#.#.##.####
     ABCDEFGHI

  do _not_ jump: (D & not E & not H)
  .................
  .................
  ..@..............
  #####.#.#...#####
     ABCDEFGHI

  do _not_ jump:
  .................
  .................
  ..@..............
  #####...#########
     ABCDEFGHI
     110001111

  B & not C & D & (E | (not E & not F))
= B & D & not C & not (F & not E)
= B & D & not (C | (F & not E))

  B & not C & D & (E | (not E & not F) | (not E & not G))
= B & not C & D & (E | (not E & (not F | not G)))
= B & not C & D & (E | (not E & not (F & G)))

(E | (not E & not F))
E=0 F=0 -> 1
E=1 F=0 -> 1
E=1 F=1 -> 1
E=0 F=1 -> 0
not (F & not E)

E | (not E & not F) | (not E & not G)

E F G ->
1 * * 1
0 0 0 1
0 1 0 1
0 0 1 1
0 1 1 0

not (F & G & not E)

(D & E) | (D & not E & not F) | (D & H & not E & not G)
= D & (E | (not E & (not F | (H & not G)))
= D & (E | (not F | (H & not G)))
= D & (E | not (F & (G | not H)))

NOT H T
OR G T
AND F T
NOT T T
OR E T
AND D T

X | ((not X) & Y)
= X | Y

A & not B:
.................
.................
...@.............
#####.###########
    ABCDEFGHI

  do jump (D & not E):
  .................
  .................
  ...@.............
  #####..#.########
      ABCDEFGHI
      100101111

  not B & not E & D
  = not (E | B) & D
  = not B & not (E | not D)
  = not (B | E | not D)

not A = jump
.................
.................
....@............
#####.###########
     ABCDEFGHI

when you jump you land on D
'''


springscript = '''
# Jump three squares out
# = B & D & not (C | (F & not E))
NOT H T
OR G T
AND F T
NOT T T
OR E T
AND D T
NOT C J
AND T J
# Jump two squares out
NOT D T
OR E T
OR B T
NOT T T
OR T J
# Jump one square out
NOT A T
OR T J
RUN
'''


def should_jump(sensors):
    A, B, C, D, E, F, G, H, I = sensors

    if not C and D and (E or not (F and (not H or G))):
        return True

    if not B and D and not E:
        return True

    if not A:
        return True

    return False


def should_jump_spring(sensors):
    A, B, C, D, E, F, G, H, I = sensors

    J = T = False

    # three squares out
    T = not H
    T = G or T
    T = F and T
    T = not T
    T = E or T
    T = D and T
    J = not C
    J = T and J

    # two squares out
    T = not D
    T = E or T
    T = B or T
    T = not T
    J = T or J

    # one square out
    T = not A
    J = T or J

    return J


if __name__ == '__main__':
    inp = fileinput.input()
    program = read_program(inp)
    springscript = '\n'.join(
        line
        for line in springscript.split('\n')
        if line and not line.startswith('#')
    ) + '\n'
    program.inputs = [ord(x) for x in springscript]
    program.run()
    print(''.join(chr(x) if x < 255 else str(x) for x in program.outputs))
