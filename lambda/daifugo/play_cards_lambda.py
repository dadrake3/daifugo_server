import os
from typing import List

import boto3
import urllib3

from .common import (get_game, get_game_state, get_hands, get_players,
                    update_hand, update_player, update_state)
from .daifugo import play_cards
from .model import Card, CardSet, Discards, Hand, Player


def play_cards_handler(event, context):
    # need to add skip handling
    # need to add logic about removing players with empty hands

    player_id = event["argument"]["player_id"]
    game_id = event["arguments"]["game_id"]
    cards = CardSet(
        [Card.from_json(card_json) for card_json in event["arguments"]["cards"]]
    )
    discards = [
        Card.from_json(card_json) for card_json in event["arguments"]["discards"]
    ]

    http_client = urllib3.PoolManager()
    dynamodb = boto3.resource("dynamodb")

    game = get_game(game_id, dynamodb)
    players = get_players(game.players, dynamodb)
    hands = get_hands([player.hand_id for player in players], dynamodb)
    prev_game_state = get_game_state(game.state_id, dynamodb)

    assert (
        players[prev_game_state.active_player_idx].id == player_id
    ), "Incorrect player"

    next_game_state, new_hands, new_players = play_cards(
        prev_game_state, cards, discards, players, hands
    )
    for hand in new_hands:
        update_hand(hand.id, hand.cards, http_client)

    for player in new_players:
        update_player(player, http_client)

    update_state(next_game_state, http_client)

    return next_game_state.to_json()
