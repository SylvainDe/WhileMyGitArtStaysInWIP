from enum import Enum, auto
import random
import collections
import time

# Values for development purposes
SHOW_GAME_STATE_AT_THE_END = False
SHOW_GAME_STATE_ON_EACH_TURN = False
SHOW_PLAYER_ACTIONS = False
RANDOM_SEED = 42 # Consistent behavior for the time being - use None for real random values


random.seed(RANDOM_SEED)


class Color(Enum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    WHITE = auto()
    MULTI = auto()

class Card(object):
    def __init__(self, number, color):
        self.number = number
        self.color = color

    def __eq__(self, other):
        """Overrides the default implementation"""
        return isinstance(other, Card) and \
            self.number == other.number and \
            self.color == other.color

    def __hash__(self):
        """Overrides the default implementation"""
        return hash((self.number, self.color))

    def __str__(self):
        return f"{self.number}{self.color.name[0]}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.number}, {self.color.name})"


class CardContainer(object):

    def __init__(self, cards):
        if cards is None:
            1/0
        self.cards = cards

    def add(self, card):
        self.cards.append(card)

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __bool__(self):
        return bool(self.cards)

    def __str__(self):
        return f"{','.join(map(str, self.cards))}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cards!r})"


class Hand(CardContainer):

    def pop(self, index):
        return self.cards.pop(index)


class CardStack(CardContainer):

    def __init__(self):
        super().__init__(cards=[])

    def get_last_number(self):
        return self.cards[-1].number if self.cards else 0

    def card_can_be_played(self, card):
        return self.get_last_number() + 1 == card.number


class Deck(CardContainer):

    @classmethod
    def get_deck(cls):
        deck_comp = {
            1: (3, 1),
            2: (2, 1),
            3: (2, 1),
            4: (2, 1),
            5: (1, 1),
        }

        deck = []
        for col in Color:
            for nb, nb_card in deck_comp.items():
                deck.extend([Card(nb, col)] * nb_card[col == Color.MULTI])
        random.shuffle(deck)
        return cls(deck)

    def draw_card(self):
         return self.cards.pop()


class Player(object): # To replace Hand ?
    pass


class CheatingPlayer(Player):
    pass


def count_cards_by_color(cards):
    color_dict = dict()
    for c in cards:
        color_dict.setdefault(c.color, []).append(c.number)
    return { k: collections.Counter(v) for k, v in color_dict.items() }


class Game(object):
    MAX_NB_HINTS = 8
    NB_CARDS_IN_HAND = 5

    def __init__(self, nb_player):
        self.discard = CardContainer([])
        self.hints = self.MAX_NB_HINTS
        self.errors_allowed = 3
        self.stacks = { col: CardStack() for col in Color}

        self.deck = Deck.get_deck()
        self.hands = [Hand([self.draw_card() for _ in range(self.NB_CARDS_IN_HAND)]) for _ in range(nb_player)]

        self.remaining_turns = 100

    def __str__(self):
        show_hands = True
        show_deck = True
        ret = "Hints: %s" % self.hints
        ret += "\nErrors allowed: %s" % self.errors_allowed
        ret += "\nScore: %d" % self.get_score()
        ret += "\nStacks:\n\t"
        ret += "\n\t".join(f"{col.name}: {s!s}" for col, s in self.stacks.items())
        ret += "\nHands:\n\t"
        ret += "\n\t".join(str(h) if show_hands else "Hidden" for h in self.hands)
        ret += "\nDeck:\n\t"
        ret += str(self.deck) if show_deck else f"{len(self.deck)} cards"
        ret += "\nDiscard:\n\t"
        ret += str(self.discard)
        ret += "\n\n"
        return ret

    def draw_card(self):
        nb_card = len(self.deck)
        if nb_card == 0:
            return None
        if nb_card == 1:
            self.remaining_turns = len(self.hands)
        return self.deck.draw_card()

    def refill_hand(self, player_index):
        hand = self.hands[player_index]
        if len(hand) < self.NB_CARDS_IN_HAND:
            new_card = self.draw_card()
            if new_card is not None:
                hand.add(new_card)

    def give_hints(self, player_index, target_player_index, color_told=None, number_told=None):
        if SHOW_PLAYER_ACTIONS:
            print("Player %d gives hint to player %d" % (player_index, target_player_index))
        if self.hints <= 0:
            1/0
        self.hints -= 1

    def pop_card(self, player_index, card_index):
        return self.hands[player_index].pop(card_index)

    def add_hint(self):
        self.hints = min(self.hints + 1, self.MAX_NB_HINTS)

    def get_score(self):
        return 0 if self.errors_allowed == 0 else sum(len(s) for _, s in self.stacks.items())

    def discard_card(self, player_index, card_index):
        card = self.pop_card(player_index, card_index)
        if SHOW_PLAYER_ACTIONS:
            print("Player %d discards %s" % (player_index, card))
        self.discard.add(card)
        self.add_hint()
        self.refill_hand(player_index)

    def play_card(self, player_index, card_index):
        card = self.pop_card(player_index, card_index)
        if SHOW_PLAYER_ACTIONS:
            print("Player %d plays %s" % (player_index, card))
        stack = self.stacks[card.color]
        if stack.card_can_be_played(card):
            stack.add(card)
            if card.number == 5:
                self.add_hint()
        else:
            self.discard.add(card)
            self.errors_allowed = max(0, self.errors_allowed - 1)
            if self.errors_allowed == 0:
                self.remaining_turns = 0
        self.refill_hand(player_index)


    def play_turn(self, player_index):
        if 0 and SHOW_PLAYER_ACTIONS:
            print("Starting Player %d's turn" % (player_index, ))

        # Note: This can be seen by player
        other_hands = sum((hand.cards for i, hand in enumerate(self.hands) if i != player_index), [])
        other_hands_by_color = count_cards_by_color(other_hands)
        # Note: this is cheating
        all_hands = sum((hand.cards for hand in self.hands), [])
        # Note: this could be deduced from discard and played stacks
        remaining_by_color = count_cards_by_color(self.deck.cards + all_hands)

        playables = []
        useless = []
        discardables = []
        must_be_kept = []
        for i, card in enumerate(self.hands[player_index]):  # Note: this is cheating
            remaining_for_color = remaining_by_color[card.color]
            remaining_higher_cards_in_color = sum(1 for n in remaining_for_color if n > card.number)
            last_stack_number = self.stacks[card.color].get_last_number()
            if card.number <= last_stack_number:
                useless.append(i)
            elif card.number == last_stack_number + 1:
                other_hands_for_color = other_hands_by_color.get(card.color, [])
                higher_cards_in_other_hands = sum(1 for n in other_hands_for_color if n > card.number)
                succ_in_other_hands = (card.number + 1) in other_hands_for_color
                playables.append((succ_in_other_hands, higher_cards_in_other_hands, remaining_higher_cards_in_color, i))
            else:
                assert card.number > last_stack_number + 1
                if not all(remaining_for_color[n] for n in range(last_stack_number + 1, card.number)):
                    useless.append(i)
                elif remaining_for_color[card.number] > 1:
                    # At least 1 because of the card we are considering
                    # (and at most 2 with standard rules because the only card in more than 2 specimen
                    # is number 1 which is always playable or useless)
                    discardables.append((-remaining_higher_cards_in_color, -i, i))
                else:
                    must_be_kept.append((remaining_higher_cards_in_color, i))

        # TODO: The logic between discarding and giving hints should probably
        # be more subtle to optimise the end of games (we may want to draw or
        # may want not to draw if the deck is getting thin).
        if playables:
            self.play_card(player_index, max(playables)[-1])
        elif useless:
            self.discard_card(player_index, min(useless))
        elif self.hints > 0:
            self.give_hints(player_index, (player_index + 1) % 2)
        elif discardables:
            self.discard_card(player_index, max(discardables)[-1])
        else:
            self.discard_card(player_index, min(must_be_kept)[-1])

        self.remaining_turns = max(0, self.remaining_turns - 1)
        if 0 and SHOW_PLAYER_ACTIONS:
            print("Ending Player %d's turn" % (player_index, ))

    def play(self):
        player_turn = 0
        while self.remaining_turns:
            if SHOW_GAME_STATE_ON_EACH_TURN:
                print(g)
            self.play_turn(player_turn)
            player_turn = (player_turn + 1) % len(self.hands)
        if SHOW_GAME_STATE_AT_THE_END:
            print(g)
        return self.get_score()


def compare_performances():
    before_scores = [26, 28, 24, 25, 30, 28, 25, 19, 30, 30, 29, 28, 27, 28, 22, 30, 29, 27, 27, 26, 29, 30, 30, 29, 25, 30, 27, 24, 30, 24, 27, 28, 30, 24, 24, 27, 27, 26, 29, 28, 29, 26, 30, 30, 24, 24, 29, 29, 27, 30, 28, 21, 29, 26, 30, 28, 30, 24, 30, 22, 29, 29, 27, 28, 25, 29, 27, 28, 30, 27, 26, 28, 25, 29, 26, 28, 27, 30, 29, 26, 29, 28, 27, 27, 29, 27, 28, 25, 29, 29, 28, 30, 30, 29, 27, 28, 30, 26, 28, 27, 29, 28, 30, 28, 28, 29, 29, 28, 29, 28, 26, 30, 30, 30, 30, 23, 29, 29, 25, 30, 25, 29, 30, 29, 25, 21, 30, 30, 26, 25, 28, 29, 23, 27, 29, 30, 27, 30, 30, 29, 28, 30, 30, 27, 25, 30, 30, 29, 24, 29, 30, 30, 28, 30, 30, 28, 29, 27, 25, 30, 29, 26, 28, 27, 27, 27, 30, 30, 29, 29, 26, 24, 30, 26, 29, 24, 27, 28, 25, 30, 30, 25, 26, 30, 27, 25, 29, 24, 30, 29, 26, 27, 26, 30, 26, 29, 30, 30, 27, 28, 27, 27, 28, 29, 30, 28, 29, 30, 23, 27, 25, 30, 27, 30, 28, 26, 29, 25, 26, 25, 30, 27, 25, 27, 27, 26, 30, 30, 29, 27, 29, 27, 30, 23, 29, 28, 27, 27, 25, 26, 30, 26, 28, 25, 30, 21, 30, 26, 30, 30, 28, 30, 30, 28, 28, 28, 27, 30, 24, 27, 30, 29, 28, 30, 30, 29, 23, 27, 28, 26, 30, 28, 29, 27, 27, 28, 26, 30, 27, 29, 30, 28, 29, 29, 21, 30, 30, 25, 21, 30, 20, 30, 26, 26, 30, 30, 22, 24, 26, 21, 29, 28, 26, 29, 27, 27, 27, 29, 30, 29, 28, 27, 29, 30, 29, 22, 25, 24, 30, 29, 26, 25, 30, 28, 28, 29, 30, 29, 28, 28, 28, 30, 27, 27, 30, 29, 29, 28, 28, 28, 22, 26, 26, 28, 30, 30, 29, 30, 30, 27, 30, 29, 30, 24, 29, 30, 30, 24, 29, 28, 28, 29, 27, 27, 28, 26, 29, 30, 28, 30, 30, 28, 27, 27, 30, 25, 26, 30, 30, 30, 30, 30, 29, 27, 29, 26, 29, 27, 27, 30, 28, 27, 30, 29, 29, 29, 27, 30, 29, 27, 28, 30, 30, 30, 27, 28, 29, 26, 27, 28, 30, 27, 30, 27, 29, 28, 24, 30, 27, 29, 23, 29, 23, 27, 28, 29, 24, 27, 29, 30, 30, 28, 24, 27, 29, 29, 30, 25, 25, 30, 29, 30, 26, 29, 30, 30, 29, 29, 29, 27, 30, 25, 28, 29, 28, 26, 30, 27, 30, 28, 27, 30, 27, 29, 24, 27, 29, 25, 24, 28, 30, 25, 29, 25, 29, 27, 28, 30, 30, 28, 26, 30, 27, 28, 24, 27, 29, 28, 29, 26, 25, 28, 22, 26, 26, 29, 21, 30, 27, 29, 27, 30, 27, 27, 30, 27, 27, 29, 29, 28, 22, 23, 29, 30, 25, 29, 29, 27, 30, 29, 30, 25, 30, 30, 30, 29, 27, 30, 30, 29, 29, 28, 25, 30, 28, 29, 30, 30, 25, 27, 30, 29, 30, 27, 25, 29, 28, 22, 29, 27, 30, 30, 26, 30, 27, 29, 30, 28, 30, 30, 25, 30, 24, 24, 30, 24, 29, 29, 30, 28, 26, 30, 28, 27, 22, 25, 30, 30, 30, 27, 29, 28, 27, 29, 28, 30, 29, 30, 30, 30, 28, 29, 25, 26, 26, 28, 29, 30, 27, 30, 30, 28, 27, 30, 30, 27, 28, 25, 25, 27, 26, 29, 29, 29, 28, 28, 27, 30, 26, 24, 26, 29, 27, 29, 28, 29, 24, 29, 30, 30, 24, 25, 29, 24, 30, 25, 30, 30, 29, 30, 29, 29, 26, 28, 25, 30, 24, 28, 30, 27, 29, 29, 27, 24, 30, 29, 29, 30, 26, 29, 27, 26, 27, 29, 28, 30, 30, 30, 30, 30, 30, 27, 30, 27, 28, 27, 25, 30, 28, 29, 29, 29, 29, 25, 30, 24, 30, 30, 30, 25, 25, 21, 28, 30, 26, 26, 29, 30, 25, 27, 30, 30, 30, 29, 27, 24, 28, 23, 26, 30, 30, 30, 30, 25, 29, 27, 30, 30, 28, 29, 29, 28, 30, 29, 27, 30, 23, 28, 26, 29, 25, 28, 28, 29, 29, 27, 25, 27, 26, 26, 29, 24, 25, 28, 24, 29, 29, 30, 30, 25, 29, 29, 30, 24, 30, 27, 30, 26, 30, 27, 23, 29, 28, 30, 29, 27, 26, 30, 27, 28, 30, 26, 23, 30, 30, 26, 30, 28, 29, 29, 30, 29, 29, 24, 30, 30, 27, 30, 27, 26, 25, 29, 29, 27, 24, 27, 30, 23, 30, 28, 28, 29, 30, 30, 27, 27, 27, 28, 29, 30, 25, 27, 26, 26, 29, 30, 28, 30, 28, 28, 29, 28, 25, 29, 26, 29, 30, 30, 24, 27, 30, 27, 29, 30, 28, 29, 26, 30, 26, 28, 29, 28, 30, 29, 29, 28, 29, 28, 26, 26, 27, 29, 29, 30, 28, 25, 30, 30, 30, 26, 30, 30, 30, 28, 25, 27, 28, 25, 29, 27, 29, 29, 24, 30, 30, 30, 30, 28, 28, 30, 26, 30, 28, 25, 30, 28, 27, 30, 29, 29, 26, 26, 27, 29, 30, 27, 30, 22, 27, 30, 28, 30, 26, 25, 30, 30, 30, 30, 28, 30, 25, 29, 26, 26, 29, 30, 30, 30, 28, 26, 25, 28, 26, 30, 29, 30, 30, 29, 27, 30, 29, 30, 28, 26, 30, 30, 29, 27, 28, 25, 28, 30, 30, 27, 30, 30, 27, 29, 29, 28, 30, 27, 25, 29, 30, 30, 26, 29, 26, 27, 28, 22, 27, 28, 30, 25, 28, 27, 27, 30, 30, 30, 30, 25, 30, 28, 28, 27, 30, 29, 30, 28, 28, 26, 30, 22, 30, 27, 26, 25, 30, 29, 26, 30, 28, 25, 30, 30, 29, 30, 27, 30, 25, 30, 30, 30, 30, 30, 29, 30, 29, 29, 29, 24, 29, 28, 29, 30, 30, 30, 28, 30, 29, 25, 26, 26, 26, 30, 28, 29, 29, 26, 30, 27, 29, 29, 25, 30, 27, 27, 26, 26, 29, 26, 27, 30, 26, 27, 29, 30, 29, 29, 29, 30, 27, 30, 29, 27, 29, 29, 30, 24, 30, 28, 29, 29, 25, 27, 28, 30, 25, 29, 29, 27, 28, 25, 26, 29, 20, 29, 29, 28, 29, 29, 30, 30, 28, 29, 28, 24, 29, 30, 30, 29, 30, 29, 26, 28, 29, 27, 27, 27, 27, 28, 23, 29, 30, 30, 29, 30, 30, 27, 30, 29, 30, 27, 28, 30, 30, 27, 22, 30, 27, 28, 29, 27, 30, 28, 23, 28, 27, 29, 30, 29, 25, 29, 24, 30, 27, 27, 28, 30, 20, 25, 28, 30, 30, 27, 24, 30, 29, 25, 27, 30, 29, 30, 28, 25, 26, 27, 27, 30, 29, 29, 28, 29, 28, 27, 27, 30, 27, 29, 25, 26, 29, 25, 30, 30, 29, 28, 24, 27, 30, 29, 29, 30, 29, 28, 29, 25, 26, 27, 27, 26, 27, 27, 30, 27, 27, 28, 30, 27, 30, 29, 29, 24, 30, 30, 27, 27, 30, 27, 25, 30, 28, 29, 30, 30, 27, 28, 24, 29, 30, 30, 30, 30, 28, 29, 28, 29, 24, 29, 28, 29, 30, 30, 30, 28, 29, 25, 27, 28, 29, 26, 29, 30, 29, 26, 30, 26]

    games = [Game(nb_player=2) for i in range(len(before_scores))]
    begin = time.time()
    scores = [g.play() for g in games]
    end = time.time()
    print("before_scores =", scores)

    gains = []
    losses = []
    for i, (a, b) in enumerate(zip(before_scores, scores)):
        if a != b:
            d = b - a
            if d > 0:
                gains.append(d)
            else:
                losses.append(d)
            print(i, a, b, b - a, "     >" if a > b else "             <")

    print("Computed scores in %f" % (end - begin))
    print("Before: avg:%f, min:%d, max:%d" % (sum(before_scores) / len(before_scores), min(before_scores), max(before_scores)))
    print("After: avg:%f, min:%d, max:%d" % (sum(scores) / len(scores), min(scores), max(scores)))
    print("Losses", min(losses) if losses else "NA", len(losses), sorted(losses))
    print("Gains", max(gains) if gains else "NA", len(gains), sorted(gains))

compare_performances()
