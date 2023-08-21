import boto3
import pytest
import urllib3
from daifugo.common import get_game, get_hands, post_mutation
from daifugo.constants import GAME_TABLE, HAND_TABLE, PLAYER_TABLE
from daifugo.join_game_lambda import join_game_handler
from daifugo.model import Game, Player


@pytest.mark.integration
def test_join_game_handler_e2e(
    setup_environment_vars, mocker, empty_context, empty_game, dynamodb
):
    event = dict(arguments=dict(game_id=empty_game.id, player_name="Daryl"))

    player_json = join_game_handler(event, empty_context)
    player = Player.from_json(player_json)

    hand = next(iter(get_hands([player.hand_id], dynamodb)))
    new_game = get_game(empty_game.id, dynamodb)

    assert new_game.id == empty_game.id
    assert new_game.players == [player.id]
    assert new_game.joinable == True
    assert hand.id == player.hand_id
    assert len(hand) == 0

    # cleanup test
    dynamodb.Table(GAME_TABLE).delete_item(Key={"id": empty_game.id})
    dynamodb.Table(PLAYER_TABLE).delete_item(Key={"id": player.id})
    dynamodb.Table(HAND_TABLE).delete_item(Key={"id": hand.id})
