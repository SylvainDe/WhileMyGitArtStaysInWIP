"""
Inspired from https://www.youtube.com/watch?v=bDZieLmya_I
"This May Be The Most Counterintuitive Probability Paradox I've Ever Seen | Can you spot the error?"
"""

import itertools


genders = ['boy', 'girl']


def part1():
    """ Someone says: "I have two children, at least one of which
    is a girl." - what is the probablity that the other is a girl
    as well ? (from 0:40 on the video) """

    # Generate universe
    universe = list(itertools.product(genders, repeat=2))

    # Generate sub-universes
    at_least_1_girl = [l for l in universe if any(e == 'girl' for e in l)]
    exactly_2_girls = [l for l in universe if all(e == 'girl' for e in l)]

    # Compute probability
    ret = len(exactly_2_girls) / len(at_least_1_girl)
    print("part1 -> ", ret)
    return ret



print(part1() == 1/3)

