import pytest
from daifugo.join_game_lambda import join_game_handler


@pytest.fixture
def event():
    return dict(arguments=dict(game_id="8fc165a3-71bc-4576-80c9-138066100c32", player_name="Daryl"))


@pytest.fixture
def context():
    return {}


@pytest.mark.integration
def test_join_game_handler(setup_environment_vars, mocker, event, context):
    ret = join_game_handler(event, context)
    breakpoint()