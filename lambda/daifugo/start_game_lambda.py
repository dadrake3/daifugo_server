import json
import logging

import boto3
import urllib3

from .common import deal_hands, get_game, get_players, update_hand

logger = logging.getLogger(__name__)


def start_game_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    http_client = urllib3.PoolManager()

    game_id = event["arguments"]["game_id"]
    game = get_game(game_id, dynamodb)

    player_ids = game["players"]
    n_players = len(player_ids)
    players = get_players(player_ids, dynamodb)

    hand_ids = [player["hand_id"] for player in players]
    hands = deal_hands(n_players)

    for cards, hand_id in zip(hands, hand_ids):
        response = update_hand(hand_id, cards, http_client)
        logger.info(json.loads(response.data))

    # TODO: create initial game state


if __name__ == "__main__":
    event = {"arguments": {"game_id": "3c61be0e-fbde-43e5-9b4a-6955a7156e88"}}
    start_game_handler(event, None)
