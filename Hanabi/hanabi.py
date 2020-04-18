from enum import Enum, auto
import random

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


class Game(object):
    MAX_NB_HINTS = 7

    def __init__(self, nb_player):
        self.discard = CardContainer([])
        self.hints = self.MAX_NB_HINTS
        self.errors_allowed = 3
        self.stacks = { col: CardStack() for col in Color}

        self.deck = Deck.get_deck()
        self.hands = [Hand([self.draw_card() for _ in range(5)]) for _ in range(nb_player)]

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

    def give_hints(self, player_index, color_told=None, number_told=None):
        if SHOW_PLAYER_ACTIONS:
            print("Player %d gives hint" % (player_index, ))
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

    def play_turn(self, player_index):
        # SUPER HACK TODO
        # players knows everything
        hand = self.hands[player_index]
        for i, card in enumerate(hand):
            stack = self.stacks[card.color]
            if stack.card_can_be_played(card):
                self.play_card(player_index, i)
                break
        else:
            played_cards = set()
            for _, s in self.stacks.items():
                played_cards.update(s.cards)
            for i, card in enumerate(hand):
                if card in played_cards:
                    self.discard_card(player_index, i)
                    break
            else:
                for i, card in enumerate(hand):
                    if card in self.deck.cards + self.hands[(player_index + 1) % 2].cards:
                        self.discard_card(player_index, i)
                        break
                else:
                    if self.hints > 0:
                        self.give_hints((player_index + 1) % 2)
                    else:
                        self.discard_card(player_index, 0) # TODO
        if len(hand) < 5:
            new_card = self.draw_card()
            if new_card is not None:
                hand.add(new_card)
        self.remaining_turns -= 1

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


games = [Game(nb_player=2) for i in range(30)]
#scores = sorted([g.play() for g in games])
scores = [g.play() for g in games]
print(scores)
