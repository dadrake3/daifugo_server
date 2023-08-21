import pytest
from daifugo.join_game_lambda import join_game_handler
from daifugo.start_game_lambda import start_game_handler
from daifugo.common import post_mutation, get_game, get_hands, get_starting_hand
from daifugo.constants import GAME_TABLE, PLAYER_TABLE, HAND_TABLE, STATE_TABLE
from daifugo.model import Game, Player, GameState
import boto3
import urllib3


@pytest.fixture
def event():
    return dict(
        arguments=dict(
            game_id="df500644-dc25-456e-afd7-7241a554320a", player_name="Daryl"
        )
    )


@pytest.mark.integration
def test_start_game_handler_e2e(
    setup_environment_vars, mocker, empty_context, empty_game, dynamodb
):
    player_names = ["Daryl", "Will", "Rebers"]
    players = []
    for player_name in player_names:
        event = dict(arguments=dict(game_id=empty_game.id, player_name=player_name))

        player_json = join_game_handler(event, empty_context)
        players.append(Player.from_json(player_json))

    event = dict(arguments=dict(game_id=empty_game.id))

    state_json = start_game_handler(event, empty_context)
    state = GameState.from_json(state_json)

    hands = get_hands([player.hand_id for player in players], dynamodb)

    assert {hand.id for hand in hands} == {player.hand_id for player in players}

    # cleanup test
    dynamodb.Table(GAME_TABLE).delete_item(Key={"id": empty_game.id})
    dynamodb.Table(STATE_TABLE).delete_item(Key={"id": state.id})
    for player in players:
        dynamodb.Table(PLAYER_TABLE).delete_item(Key={"id": player.id})
        dynamodb.Table(HAND_TABLE).delete_item(Key={"id": player.hand_id})
