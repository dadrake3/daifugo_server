import boto3
import pytest
import urllib3
from daifugo.common import get_hands, get_players, post_mutation
from daifugo.constants import GAME_TABLE, HAND_TABLE, PLAYER_TABLE, STATE_TABLE
from daifugo.join_game_lambda import join_game_handler
from daifugo.model import Game, GameState, Player
from daifugo.mutations import CREATE_GAME_MUTATION
from daifugo.play_cards_lambda import play_cards_handler
from daifugo.start_game_lambda import start_game_handler


@pytest.fixture
def event():
    return dict(
        arguments=dict(
            player_ids=["999b0e7e-92f0-43dc-b3c9-628c4beaf015"], player_name="Daryl"
        )
    )


@pytest.mark.integration
def test_play_cards_handler_e2e(
    setup_environment_vars, mocker, empty_context, dynamodb, http_client
):
    # Setup test
    game_json = post_mutation(CREATE_GAME_MUTATION, http_client)
    empty_game = Game.from_json(game_json)

    player_names = ["Daryl", "Will", "Rebers"]
    players = []
    for player_name in player_names:
        player_json = join_game_handler(
            event=dict(arguments=dict(game_id=empty_game.id, player_name=player_name)),
            context=empty_context,
        )

        players.append(Player.from_json(player_json))

    state_json = start_game_handler(
        dict(arguments=dict(game_id=empty_game.id)), empty_context
    )
    state = GameState.from_json(state_json)

    active_player = next(
        iter([player for player in players if player.id == state.active_player_id])
    )
    hand = next(iter(get_hands([active_player.hand_id], dynamodb)))

    # Run tests

    event = dict(
        arguments=dict(
            player_id=active_player.id,
            game_id=empty_game.id,
            discards=[],
            cards=[hand.cards[0].to_json()],
        )
    )
    new_state_json = play_cards_handler(event, empty_context)

    # Cleanup test
    dynamodb.Table(GAME_TABLE).delete_item(Key={"id": empty_game.id})
    dynamodb.Table(STATE_TABLE).delete_item(Key={"id": state.id})
    for player in players:
        dynamodb.Table(PLAYER_TABLE).delete_item(Key={"id": player.id})
        dynamodb.Table(HAND_TABLE).delete_item(Key={"id": player.hand_id})
