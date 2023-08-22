import itertools
import json
import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

from .constants import RANKS, SUITS


class CARD_SPECIALS(Enum):
    SKIP_PLAYER = 0
    DISCARD_FORWARD = 1
    DISCARD_POT = 2


class Pattern(str, Enum):
    SUITED = "Suited"
    RUN = "Run"
    SUITED_RUN = "SuitedRun"


class DiscardType(Enum):
    POT = 0
    FORWARD = 1


@dataclass
class Card:
    rank: Optional[str] = None
    suit: Optional[str] = None
    is_joker: bool = False

    # @property
    # def is_pure_joker(self) -> bool:
    #     """weather a joker is behaving as a joker i.e. > 2 or if its behaving as a sub rank card"""
    #     return self.rank is None and self.suit is None and self.is_joker

    # @property
    # def rank_value(self) -> int:
    #     if self.is_pure_joker:
    #         return 13

    #     return RANKS.get(self.rank)

    # def __repr__(self) -> str:
    # return f"Card({self.rank}, {self.suit})"
    # return f"{self.rank} of {self.suit}s"
    # return self.to_json()

    def to_json(self) -> Dict[str, str]:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str) -> "Card":
        return cls(**json.loads(json_str))

    @property
    def is_starting_card(self) -> bool:
        return self.suit == "Diamond" and self.rank == "3"


class Deck:
    def __init__(self, n_jokers=2):
        self._cards = [
            Card(rank, suit)
            for suit, rank in itertools.product(SUITS, RANKS)
            if rank != "Joker"
        ]

        for _ in range(n_jokers):
            self._cards.append(Card(is_joker=True))

    def __len__(self):
        return len(self._cards)

    def shuffle(self):
        random.shuffle(self._cards)

    def draw_one(self) -> Card:
        return self._cards.pop()

    def deal(self, n=1):
        ret = []
        for _ in range(n):
            ret.append(self._cards.pop())
        return ret


@dataclass
class CardSet:
    cards: List[Card]

    def __len__(self) -> int:
        return len(self.cards)

    @property
    def suits(self) -> Set[str]:
        return {card.suit for card in self.cards}

    @property
    def rank(self) -> str:
        return next(iter({card.rank for card in self.cards}))


@dataclass
class Discards:
    to_pot: List[Card]
    to_forward: List[Card]


@dataclass
class Player:
    id: str
    name: str
    game_id: str
    hand_id: str
    has_passed: bool
    rank: int

    @property
    def is_out(self) -> bool:
        return self.rank != -1

    @classmethod
    def from_json(cls, json_obj) -> "Player":
        return cls(
            json_obj["id"],
            json_obj["name"],
            json_obj["game_id"],
            json_obj["hand_id"],
            json_obj["has_passed"],
            int(json_obj["rank"]),
        )


@dataclass
class Game:
    id: str
    state_id: str
    joinable: bool
    players: List[str]

    @classmethod
    def from_json(cls, json_obj) -> "Game":
        return cls(
            json_obj["id"],
            json_obj["state_id"],
            json_obj["joinable"],
            json_obj["players"],
        )


# TODO: add active player id to game state as well so subscribers can filter on that
@dataclass
class GameState:
    id: str
    game_id: str
    active_player_idx: int
    active_player_id: str
    last_played_idx: int
    _top_of_pile: List[Card]
    pot_size: int
    active_pattern: Optional[Pattern]
    revolution: bool
    direction: bool

    @property
    def top_of_pile(self) -> CardSet:
        return CardSet(self._top_of_pile)

    @property
    def new_trick(self) -> bool:
        return not len(self._top_of_pile)

    @property
    def new_game(self) -> bool:
        return self.new_trick and not self.pot_size

    @classmethod
    def from_json(cls, json_obj) -> "GameState":
        top_of_pile = [
            Card.from_json(card_json) for card_json in json_obj["top_of_pile"]
        ]

        if json_obj["active_pattern"]:
            pattern = Pattern(json_obj["active_pattern"])
        else:
            pattern = None

        return cls(
            json_obj["id"],
            json_obj["game_id"],
            int(json_obj["active_player_idx"]),
            json_obj["active_player_id"],
            int(json_obj["last_played_idx"]),
            top_of_pile,
            int(json_obj["pot_size"]),
            pattern,
            json_obj["revolution"],
            json_obj["direction"],
        )


@dataclass
class Hand:
    id: str
    cards: List[Card]

    def __len__(self) -> int:
        return len(self.cards)

    @classmethod
    def from_json(cls, json_obj) -> "Hand":
        cards = [Card.from_json(card_json) for card_json in json_obj["cards"]]

        return Hand(json_obj["id"], cards)
