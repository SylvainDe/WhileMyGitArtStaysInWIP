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


def my_round(value, precision):
    """
    assert my_round(0, 1) == 0
    assert my_round(0, 2) == 0
    assert my_round(-1.4, 0.5) == -1.5
    assert my_round(-1.4, 1) == -1
    assert my_round(-1.4, 2) == -2
    assert my_round(12.9, 1) == 13
    assert my_round(13.0, 1) == 13
    assert my_round(13.4, 1) == 13
    assert my_round(13.5, 1) == 14
    assert my_round(13.6, 1) == 14
    assert my_round(14.0, 1) == 14
    assert my_round(12.9, 2) == 12
    assert my_round(13.0, 2) == 12
    assert my_round(13.4, 2) == 14
    assert my_round(13.5, 2) == 14
    assert my_round(13.6, 2) == 14
    assert my_round(14.0, 2) == 14
    assert my_round(12.9, 0.5) == 13.0
    assert my_round(13.0, 0.5) == 13.0
    assert my_round(13.4, 0.5) == 13.5
    assert my_round(13.5, 0.5) == 13.5
    assert my_round(13.6, 0.5) == 13.5
    assert my_round(14.0, 0.5) == 14.0
    """
    return round(value / precision) * precision


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
rounding_precision = 1


def run_simu():
    tasks = [incertitude.apply(t) for t in order.apply(input_tasks)]

    heap = [0] * nb_consumer
    for task in tasks:
        time = heapq.heappop(heap)
        heapq.heappush(heap, time + task)
    return max(heap)


count = collections.Counter(
    [my_round(run_simu(), rounding_precision) for _ in range(nb_simu)]
)
cum = 0
for k in sorted(count.keys()):
    v = count[k]
    cum += v
    print(k, v, v * 100 / nb_simu, cum, cum * 100 / nb_simu)
