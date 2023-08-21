import boto3
import pytest
import urllib3
from daifugo.common import get_players
from daifugo.play_cards_lambda import play_cards_handler


@pytest.fixture
def event():
    return dict(
        arguments=dict(
            player_ids=["999b0e7e-92f0-43dc-b3c9-628c4beaf015"], player_name="Daryl"
        )
    )


# def test_test(event):
#     http_client = urllib3.PoolManager()
#     dynamodb = boto3.resource("dynamodb")

#     player = get_players(event["arguments"]["player_ids"], dynamodb)
#     breakpoint()
