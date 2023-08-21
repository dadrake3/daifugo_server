import urllib3

from .common import post_mutation
from .mutations import (CREATE_HAND_MUTATION, CREATE_PLAYER_MUTATION,
                        UPDATE_GAME_MUTATION)


def join_game_handler(event, context):
    """
    Creates a player and then adds them to an existing game

    TODO: assert that the game actually exists in dyanmo

    """
    game_id = event["arguments"]["game_id"]
    player_name = event["arguments"]["player_name"]

    http_client = urllib3.PoolManager()

    create_hand_response = post_mutation(CREATE_HAND_MUTATION, http_client)
    hand_id = create_hand_response["id"]

    create_player_response = post_mutation(
        CREATE_PLAYER_MUTATION,
        http_client,
        variables=dict(game_id=game_id, name=player_name, hand_id=hand_id),
    )

    player_id = create_player_response["id"]

    post_mutation(
        UPDATE_GAME_MUTATION,
        http_client,
        variables=dict(id=game_id, players=[player_id]),
    )

    return create_player_response
