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


# Basic configuration
#####################

# Reproducible results
reproducible = False
# Number of simulations
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
# Display
graph_char = "#"
width_graph_count = 40
width_graph_cum = 40


def run_simu():
    tasks = [incertitude.apply(t) for t in order.apply(input_tasks)]

    heap = [0] * nb_consumer
    for task in tasks:
        time = heapq.heappop(heap)
        heapq.heappush(heap, time + task)
    return max(heap)


def main():
    if reproducible:
        print("Warning: random.seed: results will not be as random as expected")
        random.seed(42)
    count = collections.Counter(
        [my_round(run_simu(), rounding_precision) for _ in range(nb_simu)]
    )
    cum = 0
    max_count = count.most_common(1)[0][1]
    max_count_len = len(str(max_count))
    max_cum_len = len(str(nb_simu))
    for k in sorted(count.keys()):
        v = count[k]
        cum += v
        width_count = int(width_graph_count * v / max_count)
        graph_count_left = graph_char * width_count
        graph_count_right = " " * (width_graph_count - width_count)
        width_cum = int(width_graph_cum * cum / nb_simu)
        graph_cum_left = graph_char * width_cum
        graph_cum_right = " " * (width_graph_cum - width_cum)
        count_str = str(v).ljust(max_count_len)
        cum_str = str(cum).ljust(max_cum_len)
        count_percent = "{:6.2f}%".format(v * 100 / nb_simu)
        cum_percent = "{:6.2f}%".format(cum * 100 / nb_simu)
        print(
            k,
            graph_count_left,
            count_str,
            graph_count_right,
            count_percent,
            graph_cum_left,
            cum_str,
            graph_cum_right,
            cum_percent,
        )


if __name__ == "__main__":
    main()
