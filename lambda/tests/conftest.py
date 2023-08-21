import os
import subprocess

import pytest
import urllib3
from daifugo.model import Game
from daifugo.common import post_mutation
from daifugo.mutations import CREATE_GAME_MUTATION
import boto3


@pytest.fixture
def setup_api_key_from_tf(mocker):
    ret = subprocess.check_output(["terraform", "output", "appsync_api_key"])
    api_key = ret.decode().strip().replace('"', "")

    headers = {
        "Content-Type": "application/graphql",
        "x-api-key": api_key,
        "cache-control": "no-cache",
    }

    mocker.patch("daifugo.common.HTTP_HEADERS", headers)


@pytest.fixture
def setup_api_url_from_tf(mocker):
    ret = subprocess.check_output(["terraform", "output", "appsync_api_endpoint"])
    url = ret.decode().split('"GRAPHQL" = ')[1].split("\n")[0].replace('"', "")

    mocker.patch("daifugo.common.API_URL", url)


@pytest.fixture
def setup_environment_vars(setup_api_key_from_tf, setup_api_url_from_tf):
    pass


@pytest.fixture
def http_client():
    return urllib3.PoolManager()


@pytest.fixture
def empty_game(http_client):
    game_json = post_mutation(CREATE_GAME_MUTATION, http_client)

    return Game.from_json(game_json)


@pytest.fixture
def dynamodb():
    return boto3.resource("dynamodb")


@pytest.fixture
def empty_context():
    return {}
