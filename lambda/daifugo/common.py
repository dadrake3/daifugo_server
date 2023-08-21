import json
import logging
from typing import Any, List, Optional

import boto3
import urllib3

from .constants import (API_URL, GAME_STATE_TABLE, GAME_TABLE, HAND_TABLE,
                       HTTP_HEADERS, PLAYER_TABLE)
from .model import Card, Game, GameState, Hand, Player, Deck
from .mutations import UPDATE_HAND_MUTATION, UPDATE_STATE_MUTATION, UPDATE_PLAYER_MUTATION

logger = logging.getLogger(__name__)


class InvalidPlayError(ValueError):
    pass


def get_items(ids: List[str], dynamodb, table_name) -> Any:
    data = dynamodb.batch_get_item(
        RequestItems={
            table_name: {"Keys": [{"id": _id} for _id in ids], "ConsistentRead": True}
        },
        ReturnConsumedCapacity="TOTAL",
    )
    return data["Responses"][table_name]


def post_mutation(
    mutation: str, http_client: urllib3.PoolManager, variables: Optional[str] = None
):
    request_body = {"query": mutation}
    if variables:
        request_body["variables"] = variables

    response = http_client.request(
        "POST",
        API_URL,
        body=json.dumps(request_body),
        headers=HTTP_HEADERS,
    )

    return json.loads(response.data)


def get_game(game_id: str, dynamodb) -> Game:
    game_json = next(iter(get_items([game_id], dynamodb, GAME_TABLE)))
    return Game.from_json(game_json)


def get_game_state(state_id: str, dynamodb) -> GameState:
    game_json = next(iter(get_items([state_id], dynamodb, GAME_STATE_TABLE)))
    return GameState.from_json(game_json)


def get_players(player_ids: List[str], dynamodb) -> List[Player]:
    players_json = get_items(player_ids, dynamodb, PLAYER_TABLE)
    return [Player.from_json(player_json) for player_json in players_json]


def get_hands(hand_ids: List[str], dynamodb) -> List[Hand]:
    hands_json = get_items(hand_ids, dynamodb, HAND_TABLE)
    return [Hand.from_json(hand_json) for hand_json in hands_json]


def update_hand(
    hand_id: str, cards: List[Card], http_client: urllib3.PoolManager
) -> None:
    json_cards = [card.to_json() for card in cards]
    variables = {"id": hand_id, "cards": json_cards}

    post_mutation(UPDATE_HAND_MUTATION, http_client, variables)


def update_player(player: Player, http_client: urllib3.PoolManager) -> None:
    post_mutation(UPDATE_PLAYER_MUTATION, http_client, variables=dict(
        id=player.id,
        has_passed=player.has_passed,
        rank=player.rank
    ))


def update_state(state: GameState, http_client: urllib3.PoolManager) -> None:
    post_mutation(UPDATE_STATE_MUTATION, http_client, variables=dict(
        id=state.id,
        active_player_idx=state.active_player_idx,
        last_played_idx=state.last_played_idx,
        active_player_id=state.active_player_id,
        top_of_pile=state.top_of_pile,
        pot_size=state.pot_size,
        active_pattern=state.active_pattern,
        revolution=state.revolution,
        direction=state.direction
    ))


def deal_hands(n_players=5) -> List[List[Card]]:
    deck = Deck()
    deck.shuffle()

    idx = 0
    hands = [[] for _ in range(n_players)]

    while len(deck):
        hands[idx].append(deck.draw_one())
        idx = (idx + 1) % n_players

    return hands
