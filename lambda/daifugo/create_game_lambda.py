import logging

import boto3
from daifugo.common import generate_unique_game_id
from daifugo.constants import GAME_TABLE
from daifugo.model import Game

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_game_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    game_id = generate_unique_game_id(dynamodb)

    logger.info(game_id)

    game = Game(game_id, "", True, [])

    table = dynamodb.Table(GAME_TABLE)
    response = table.put_item(Item={**game.__dict__})

    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    assert status_code == 200, status_code

    return game.__dict__
