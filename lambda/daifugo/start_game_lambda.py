import json
import logging

import boto3
import urllib3

from .common import (
    deal_hands,
    get_game,
    get_players,
    update_hand,
    post_mutation,
    get_starting_hand,
)
from .mutations import CREATE_STATE_MUTATION
from .model import GameState

logger = logging.getLogger(__name__)


def start_game_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    http_client = urllib3.PoolManager()

    game_id = event["arguments"]["game_id"]
    game = get_game(game_id, dynamodb)

    player_ids = game.players
    n_players = len(player_ids)
    players = get_players(player_ids, dynamodb)

    hand_ids = [player.hand_id for player in players]
    hands = deal_hands(n_players)

    for cards, hand_id in zip(hands, hand_ids):
        hand = update_hand(hand_id, cards, http_client)
        logger.info(hand.cards)

    # TODO: create initial game state
    starting_player_idx = get_starting_hand(hands)
    starting_player_id = game.players[starting_player_idx]

    state_json = post_mutation(
        CREATE_STATE_MUTATION,
        http_client,
        variables=dict(
            game_id=game_id,
            active_player_id=starting_player_id,
            active_player_idx=starting_player_idx,
        ),
    )
    return state_json
