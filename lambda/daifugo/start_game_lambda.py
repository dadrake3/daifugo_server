import logging

import boto3
import urllib3

from .common import (deal_hands, get_game, get_players, get_starting_hand,
                     post_mutation, update_hand)
from .mutations import CREATE_STATE_MUTATION, UPDATE_GAME_MUTATION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_game_handler(event, context):
    # TODO: add logic so only the creator of the game can start it

    logger.info(event)

    dynamodb = boto3.resource("dynamodb")
    http_client = urllib3.PoolManager()

    game_id = event["arguments"]["game_id"]
    game = get_game(game_id, dynamodb)

    player_ids = game.players
    n_players = len(player_ids)
    players = get_players(player_ids, dynamodb)

    hand_ids = [player.hand_id for player in players]
    hands = deal_hands(n_players, n_jokers=0)

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

    update_game_json = post_mutation(
        UPDATE_GAME_MUTATION,
        http_client,
        variables=dict(id=game_id, joinable=False, state_id=state_json["id"]),
    )

    return state_json
