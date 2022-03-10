import heapq
import random
import enum
import collections


class Order(enum.Enum):
    UNCHANGED = enum.auto()
    SMALL_FIRST = enum.auto()
    BIG_FIRST = enum.auto()
    RANDOM = enum.auto()

    def apply(self, l):
        order_funcs = {
            Order.UNCHANGED: lambda l: None,
            Order.SMALL_FIRST: lambda l: l.sort(),
            Order.BIG_FIRST: lambda l: l.sort(reverse=True),
            Order.RANDOM: lambda l: random.shuffle(l),
        }
        l = list(l)
        order_funcs[self](l)
        return l


class Incertitude(enum.Enum):
    CERTAIN = enum.auto()
    TRIANGULAR = enum.auto()

    def apply(self, value):
        random_funcs = {
            Incertitude.CERTAIN: lambda v: v,
            Incertitude.TRIANGULAR: lambda v: v * random.triangular(0.5, 1.5),
        }
        return random_funcs[self](value)


#  Number of simulations
nb_simu = 10000
# Number of consumers
nb_consumer = 4
# Tasks
input_tasks = [3, 8, 4, 5, 6, 7, 8, 9, 2, 15, 16, 5, 6]
# Order
order = Order.BIG_FIRST
order = Order.RANDOM
# Incertitude on estimation: random distribution
incertitude = Incertitude.CERTAIN
incertitude = Incertitude.TRIANGULAR
# Rounding
# TODO: Required when random adjustment is performed


def run_simu():
    tasks = [incertitude.apply(t) for t in order.apply(input_tasks)]

    heap = [0] * nb_consumer
    for task in tasks:
        time = heapq.heappop(heap)
        heapq.heappush(heap, time + task)
    return max(heap)


count = collections.Counter([int(run_simu()) for _ in range(nb_simu)])
cum = 0
for k in sorted(count.keys()):
    v = count[k]
    cum += v
    print(k, v, v * 100 / nb_simu, cum, cum * 100 / nb_simu)
