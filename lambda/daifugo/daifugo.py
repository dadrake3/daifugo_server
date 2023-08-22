from typing import List, Optional, Tuple

from .common import InvalidPlayError
from .constants import DOWN, RANKS, UP
from .model import Card, CardSet, Discards, GameState, Hand, Pattern, Player


class PatternResolver:
    # TODO: add paradox handler

    @staticmethod
    def is_suited(cards: CardSet, top_of_pile: CardSet) -> bool:
        return len(top_of_pile) and cards.suits == top_of_pile.suits

    @staticmethod
    def is_run(cards: CardSet, top_of_pile: CardSet) -> bool:
        return (
            len(top_of_pile) and abs(RANKS[cards.rank] - RANKS[top_of_pile.rank]) == 1
        )

    @classmethod
    def resolve(cls, cards: CardSet, top_of_pile: CardSet) -> Optional[Pattern]:
        is_suited = cls.is_suited(cards, top_of_pile)
        is_run = cls.is_run(cards, top_of_pile)

        if is_suited and is_run:
            return Pattern.SUITED_RUN
        elif is_run:
            return Pattern.RUN
        elif is_suited:
            return Pattern.SUITED

        return None


class Validator:
    def __init__(
        self,
        cards: CardSet,
        top_of_pile: CardSet,
        direction: bool,
        active_pattern: Pattern,
        infered_pattern: Pattern,
    ):
        self._cards = cards
        self._top_of_pile = top_of_pile

        self._direction = direction
        self._active_pattern = active_pattern
        self._infered_pattern = infered_pattern

    @staticmethod
    def pre_validate(cards: CardSet):
        if not len({card.rank for card in cards.cards}) == 1:
            raise InvalidPlayError(f"More than one rank")

    @classmethod
    def validate(
        cls,
        cards: CardSet,
        top_of_pile: CardSet,
        direction: bool,
        active_pattern: Optional[Pattern],
        infered_pattern: Optional[Pattern],
        discards: List[Card],
    ):
        if not cls.validate_rank(cards, top_of_pile, direction):
            raise InvalidPlayError("Invalid Rank")
        if not cls.validate_size(cards, top_of_pile):
            raise InvalidPlayError("Invalid Number of Cards")
        if not cls.validate_pattern(active_pattern, infered_pattern):
            raise InvalidPlayError(f"Doesnt Match Pattern {active_pattern}")
        if not cls.validate_discards(cards, discards):
            raise InvalidPlayError(f"Invalid discard set")

    @staticmethod
    def validate_discards(cards: CardSet, discards: List[Card]) -> bool:
        rank = cards.rank
        if discards and rank not in ["7", "10"]:
            return False

        # also need to check if its less but you could potentially end a trick with less discarded
        if len(discards) > len(cards):
            return False

        return True

    @staticmethod
    def validate_rank(
        cards: CardSet,
        top_of_pile: CardSet,
        direction: bool,
    ) -> bool:
        # if self._top_of_pile.rank == "Joker":
        #     return self._cards.rank == 3 and self._cards.suits == {"Spade"}

        if direction == UP:
            return RANKS[cards.rank] > RANKS[top_of_pile.rank]
        else:
            return RANKS[cards.rank] < RANKS[top_of_pile.rank]

    @staticmethod
    def validate_size(
        cards: CardSet,
        top_of_pile: CardSet,
    ) -> bool:
        return len(cards) == len(top_of_pile)

    @staticmethod
    def validate_pattern(
        active_pattern: Optional[Pattern], infered_pattern: Optional[Pattern]
    ) -> bool:
        if active_pattern is None or active_pattern == Pattern.NONE:
            return True

        if active_pattern == Pattern.RUN:
            return infered_pattern in [Pattern.RUN, Pattern.SUITED_RUN]

        elif active_pattern == Pattern.SUITED:
            return infered_pattern in [Pattern.SUITED, Pattern.SUITED_RUN]

        elif active_pattern == Pattern.SUITED_RUN:
            return infered_pattern == Pattern.SUITED_RUN

        return True


class StateResolver:
    @staticmethod
    def resolve_direction(
        cards: CardSet, direction: bool, revolution: bool
    ) -> Tuple[bool, bool]:
        # only supports single deck right now
        card_rank = cards.rank
        if card_rank == "Jack" and len(cards) % 2 == 1:
            direction = not direction
        elif len(cards) == 4:
            direction = not direction
            revolution = not revolution

        return direction, revolution

    @staticmethod
    def resolve_next_player(
        cards: CardSet, active_player_idx: int, players: List[Player], direction: bool
    ):
        # TODO: shortcircuit on paradox

        next_player_idx = -1
        new_trick = False

        if cards.rank == "8":
            next_player_idx = active_player_idx
            new_trick = True

        elif cards.rank == "9" and len(cards) == 2:
            next_player_idx = active_player_idx
            new_trick = True

        elif cards.rank == "6" and len(cards) == 3:
            next_player_idx = active_player_idx
            new_trick = True

        # this will change when we reintroduce jokers
        elif cards.rank == "2":
            next_player_idx = active_player_idx
            new_trick = True

        elif direction == DOWN and cards.rank == "3":
            next_player_idx = active_player_idx
            new_trick = True

        elif cards.rank == "5":
            # unclear if it loops back around and skips the current player does the trick end
            next_player_idx = active_player_idx
            for _ in range(len(cards) + 1):
                next_player_idx = StateResolver.get_next_active_player_idx(
                    next_player_idx, players
                )

            if next_player_idx == active_player_idx:
                new_trick = True

        else:
            next_player_idx = StateResolver.get_next_active_player_idx(
                active_player_idx, players
            )

        return next_player_idx, new_trick

    @staticmethod
    def get_next_active_player_idx(
        active_player_idx: int, players: List[Player]
    ) -> int:
        next_idx = active_player_idx
        n_players = len(players)

        while 1:
            next_idx = (next_idx + 1) % n_players

            player = players[next_idx]

            if not player.has_passed and not player.is_out:
                return next_idx

            if next_idx == active_player_idx:
                return next_idx

    @staticmethod
    def resolve_discards(cards: CardSet, discards: List[Card]) -> Optional[Discards]:
        rank = cards.rank

        to_forward = []
        to_pot = cards.cards[::]

        if rank == "7":
            to_forward = discards

        if rank == "10":
            to_pot += discards

        return Discards(to_pot, to_forward)

    @staticmethod
    def resolve_hands(
        hands: List[Hand],
        discards: Discards,
        active_player_idx: str,
        next_player_idx: str,
    ) -> List[Hand]:
        current_hand = hands[active_player_idx]
        next_hand = hands[next_player_idx]

        for card in discards.to_pot:
            current_hand.cards.remove(card)

        for card in discards.to_forward:
            current_hand.cards.remove(card)

        ret = [current_hand]

        if discards.to_forward:
            next_hand.cards += discards.to_forward
            ret.append(next_hand)

        return ret

    @staticmethod
    def resolve_rank(
        player: Player, players: List[Player], hand: Hand
    ) -> Optional[Player]:
        if len(hand) == 0:
            max_rank = max(player.rank for player in players)
            player.rank = max_rank + 1
            return player

        return None

    @staticmethod
    def resolve_new_trick(players: List[Player]) -> List[Player]:
        new_players = []
        for player in players:
            if player.has_passed:
                player.has_passed = False
                new_players.append(player)

        return new_players

    @staticmethod
    def resolve_skip(
        current_player: Player, prev_game_state: GameState, players: List[Player]
    ) -> Tuple[GameState, List[Hand], List[Player]]:
        current_player.has_passed = True

        next_player_idx = StateResolver.get_next_active_player_idx(
            prev_game_state.active_player_idx, players
        )
        new_trick = False
        if next_player_idx == prev_game_state.last_played_idx:
            new_trick = True
            new_players = StateResolver.resolve_new_trick(players)
        else:
            # coule get double reference if we just added it above
            new_players = [current_player]

        return (
            GameState(
                id=prev_game_state.id,
                game_id=prev_game_state.game_id,
                active_player_idx=next_player_idx,
                active_player_id=current_player.id,
                last_played_idx=prev_game_state.last_played_idx,
                _top_of_pile=prev_game_state._top_of_pile if not new_trick else [],
                pot_size=prev_game_state.pot_size,
                active_pattern=prev_game_state.active_pattern
                if not new_trick
                else Pattern.NONE,
                revolution=prev_game_state.revolution,
                direction=prev_game_state.direction
                if not new_trick
                else (UP if not prev_game_state.revolution else DOWN),
            ),
            list(),
            new_players,
        )


# TODO: need to handle new trick from discard all cards
def play_cards(
    prev_game_state: GameState,
    cards: CardSet,
    discards: List[Card],
    players: List[Player],
    hands: List[Hand],
) -> Tuple[GameState, List[Hand], List[Player]]:
    current_player = players[prev_game_state.active_player_idx]

    if not len(cards):
        return StateResolver.resolve_skip(current_player, prev_game_state, players)

    Validator.pre_validate(cards)

    infered_pattern = PatternResolver.resolve(cards, prev_game_state.top_of_pile)

    if prev_game_state.top_of_pile is not None and len(prev_game_state.top_of_pile):
        Validator.validate(
            cards,
            prev_game_state.top_of_pile,
            prev_game_state.direction,
            prev_game_state.active_pattern,
            infered_pattern,
            discards,
        )

    discards = StateResolver.resolve_discards(cards, discards)
    next_player_idx, new_trick = StateResolver.resolve_next_player(
        cards, prev_game_state.active_player_idx, players, prev_game_state.direction
    )

    new_direction, new_revolution = StateResolver.resolve_direction(
        cards, prev_game_state.direction, prev_game_state.revolution
    )
    new_active_pattern = infered_pattern

    new_hands = StateResolver.resolve_hands(
        hands, discards, prev_game_state.active_player_idx, next_player_idx
    )
    new_player = StateResolver.resolve_rank(current_player, players, new_hands[0])
    new_players = [new_player] if new_player else []

    if new_trick:
        new_players += StateResolver.resolve_new_trick(players)

    return (
        GameState(
            id=prev_game_state.id,
            game_id=prev_game_state.game_id,
            active_player_idx=next_player_idx,
            active_player_id=players[next_player_idx].id,
            last_played_idx=prev_game_state.active_player_idx,
            _top_of_pile=cards.cards if not new_trick else [],
            pot_size=prev_game_state.pot_size + len(cards),
            active_pattern=new_active_pattern if not new_trick else Pattern.NONE,
            revolution=new_revolution,
            direction=new_direction
            if not new_trick
            else (UP if not new_revolution else DOWN),
        ),
        new_hands,
        new_players,
    )
