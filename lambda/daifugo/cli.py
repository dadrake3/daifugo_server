import json
import logging
from typing import List
from urllib.parse import urlparse

import boto3
import click
import urllib3
from daifugo.common import (get_game, get_game_state, get_hands, get_players,
                            post_mutation)
from daifugo.constants import (API_KEY, API_URL, GAME_TABLE, HAND_TABLE,
                               PLAYER_TABLE, STATE_TABLE)
from daifugo.model import Game, GameState, Player
from daifugo.mutations import (CREATE_GAME_MUTATION, HAND_SUBSCRIPTION,
                               JOIN_GAME_MUTATION, PLAY_CARDS_MUTATION,
                               START_GAME_MUTATION, STATE_SUBSCRIPTION)
from daifugo.play_cards_lambda import play_cards_handler
from gql import Client, gql
from gql.transport.appsync_auth import AppSyncApiKeyAuthentication
from gql.transport.appsync_websockets import AppSyncWebsocketsTransport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass  # Entry Point


@cli.command()
def create_game():
    http_client = urllib3.PoolManager()
    game_json = post_mutation(CREATE_GAME_MUTATION, http_client)
    game = Game.from_json(game_json)

    logger.info(f"{game.id=}")


@cli.command()
@click.argument("game_id", type=str)
@click.argument("name", type=str)
def join_game(game_id: str, name: str):
    http_client = urllib3.PoolManager()
    player_json = post_mutation(
        JOIN_GAME_MUTATION,
        http_client,
        variables=dict(game_id=game_id, player_name=name),
    )
    player = Player.from_json(player_json)
    logger.info(player)


@cli.command()
@click.argument("game_id", type=str)
def start_game(game_id: str):
    http_client = urllib3.PoolManager()
    state_json = post_mutation(
        START_GAME_MUTATION, http_client, variables=dict(game_id=game_id)
    )
    state = GameState.from_json(state_json)
    logger.info(state)


@cli.command("get-players")
@click.argument("game_id", type=str)
def get_players_cli(game_id: str):
    dynamodb = boto3.resource("dynamodb")

    game = get_game(game_id, dynamodb)

    players = []
    if game.players:
        players = get_players(game.players, dynamodb)
        players = sorted(players, key=lambda player: game.players.index(player.id))

    for player in players:
        logger.info(f"{player.id}: {player.name}")


@cli.command("get-hand")
@click.argument("player_id", type=str)
def get_hand_cli(player_id: str):
    dynamodb = boto3.resource("dynamodb")
    player = next(iter(get_players([player_id], dynamodb)))
    hand = next(iter(get_hands([player.hand_id], dynamodb)))

    for i, card in enumerate(hand.cards):
        logger.info(f"{i}, {card.rank} of {card.suit}s")


@cli.command()
@click.argument("game_id", type=str)
@click.argument("player_id", type=str)
@click.argument("cards", type=str)
@click.argument("discards", type=str)
def play_cards(game_id: str, player_id: str, cards: str, discards: str):
    dynamodb = boto3.resource("dynamodb")
    player = next(iter(get_players([player_id], dynamodb)))
    hand = next(iter(get_hands([player.hand_id], dynamodb)))

    _cards = []
    if cards:
        card_ids = list(map(int, cards.split(",")))
        _cards = list(map(hand.cards.__getitem__, card_ids))
        _cards = list(map(lambda card: card.to_json(), _cards))

    _discards = []
    if discards:
        discard_ids = list(map(int, discards.split(",")))
        _discards = list(map(hand.cards.__getitem__, discard_ids))
        _discards = list(map(lambda card: card.to_json(), _discards))

    http_client = urllib3.PoolManager()

    # state_json =play_cards_handler(event=dict(arguments=dict(game_id=game_id, player_id=player_id, cards=_cards, discards=_discards)), context={})

    state_json = post_mutation(
        PLAY_CARDS_MUTATION,
        http_client,
        variables=dict(
            game_id=game_id, player_id=player_id, cards=_cards, discards=_discards
        ),
    )
    # state = GameState.from_json(state_json)
    for key, value in state_json.items():
        logger.info(f"{key}: {value}")


@cli.command()
@click.argument("game_id", type=str)
def get_state(game_id: str):
    dynamodb = boto3.resource("dynamodb")
    game = get_game(game_id, dynamodb)
    state = get_game_state(game.state_id, dynamodb)
    logger.info(state)


@cli.command("get-game")
@click.argument("game_id", type=str)
def get_game_cli(game_id: str):
    dynamodb = boto3.resource("dynamodb")
    game = get_game(game_id, dynamodb)
    logger.info(game)


@cli.command()
@click.argument("hand_id", type=str)
def sub_to_hand(hand_id: str):
    url = API_URL
    host = str(urlparse(API_URL).netloc)
    logger.info(host)

    auth = AppSyncApiKeyAuthentication(host=host, api_key=API_KEY)
    transport = AppSyncWebsocketsTransport(url=url, auth=auth)

    client = Client(
        transport=transport,
    )

    for result in client.subscribe(
        gql(HAND_SUBSCRIPTION), variable_values=dict(id=hand_id)
    ):
        # breakpoint()
        # logger.info(result)
        for i, card in enumerate(result["updatedHand"]["cards"]):
            card = json.loads(card)
            logger.info(f"{i}, {card['rank']} of {card['suit']}s")


@cli.command()
@click.argument("game_id", type=str)
def sub_to_state(game_id: str):
    url = API_URL
    host = str(urlparse(API_URL).netloc)
    logger.info(host)

    auth = AppSyncApiKeyAuthentication(host=host, api_key=API_KEY)
    transport = AppSyncWebsocketsTransport(url=url, auth=auth)

    client = Client(
        transport=transport,
    )

    for result in client.subscribe(
        gql(STATE_SUBSCRIPTION), variable_values=dict(game_id=game_id)
    ):
        logger.info(result)


@cli.command()
@click.argument("game_id", type=str)
def delete_game(game_id: str):
    dynamodb = boto3.resource("dynamodb")

    game = get_game(game_id, dynamodb)

    players = []
    if game.players:
        players = get_players(game.players, dynamodb)

    hand_ids = [player.hand_id for player in players]
    for hand_id in hand_ids:
        dynamodb.Table(HAND_TABLE).delete_item(Key={"id": hand_id})

    for player_id in game.players:
        dynamodb.Table(PLAYER_TABLE).delete_item(Key={"id": player_id})

    if game.state_id:
        dynamodb.Table(STATE_TABLE).delete_item(Key={"id": game.state_id})

    dynamodb.Table(GAME_TABLE).delete_item(Key={"id": game.id})


if __name__ == "__main__":
    cli()
