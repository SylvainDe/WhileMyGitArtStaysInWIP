"""
Inspired from:
 - https://www.youtube.com/watch?v=bDZieLmya_I
 "This May Be The Most Counterintuitive Probability Paradox I've Ever Seen | Can you spot the error?"
 - https://www.youtube.com/watch?v=ElB350w8iJo
 "The Boy or Girl Probability Paradox Resolved | It was never really a paradox"
"""

import itertools


genders = ['boy', 'girl']


girl_names = [
    ('emma', 10),
    ('julie', 20),
    ('charlotte', 30),
    ('linda', 40),
]



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



def part2(name='julie', same_name_in_family=True):
    """ Someone says: "I have two children, at least one of which
    is a girl, whose name is Julie." - what is the probability that
    the other is a girl as well ? (from 2:40 on the video) """

    # Generate girl universe
    ratio = 10
    girls = []
    for (nam, proba) in girl_names:
        girls.extend([('girl', nam)] * (proba // ratio))

    # Generate boy universe
    boys = [('boy', 'whocares')] * len(girls)

    # Generate universe...
    if same_name_in_family:
        universe = list(itertools.product(boys + girls, repeat=2))
    else:
        # ...which is assumed not to have duplicated names
        # TODO: This filtering seems to be pretty wrong
        universe = list(itertools.product(boys + girls, repeat=2))
        universe = [l for l in universe if len(set(e[1] for e in l)) == len(l)]

    # Check basics from previous step
    at_least_1_girl = [l for l in universe if any(e[0] == 'girl' for e in l)]
    exactly_2_girls = [l for l in universe if all(e[0] == 'girl' for e in l)]
    step1 = len(exactly_2_girls) / len(at_least_1_girl)
    assert step1 == 1/3

    # Generate sub-universes
    at_least_1_girl_whose_name =       [l for l in universe if any(e[0] == 'girl' and e[1] == name for e in l)]
    exactly_2_girls_and_1_whose_name = [l for l in universe if any(e[0] == 'girl' and e[1] == name for e in l) and all(e[0] == 'girl' for e in l)]

    # Check a few values ?
    # print(len(universe))
    # print(len(at_least_1_girl_whose_name), len(at_least_1_girl))
    # print(len(exactly_2_girls_and_1_whose_name), len(exactly_2_girls))

    # Compute probability
    ret = len(exactly_2_girls_and_1_whose_name) / len(at_least_1_girl_whose_name)
    print("part2 (", name, ") ->", ret)
    return ret



print(part1() == 1/3)
for (nam, proba) in girl_names:
    print(part2(nam) == 1/2)

