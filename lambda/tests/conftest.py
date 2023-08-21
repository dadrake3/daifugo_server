import os
import pytest
import subprocess

@pytest.fixture
def setup_api_key_from_tf(mocker):
    ret = subprocess.check_output(["terraform", "output", "appsync_api_key"])
    api_key = ret.decode().strip().replace("\"", "")

    headers = {
        "Content-Type": "application/graphql",
        "x-api-key": api_key,
        "cache-control": "no-cache",
    }

    mocker.patch("daifugo.common.HTTP_HEADERS", headers)


@pytest.fixture
def setup_api_url_from_tf(mocker):
    ret = subprocess.check_output(["terraform", "output", "appsync_api_endpoint"])
    url = ret.decode().split("\"GRAPHQL\" = ")[1].split("\n")[0].replace("\"", "")

    mocker.patch("daifugo.common.API_URL", url)


@pytest.fixture
def setup_environment_vars(setup_api_key_from_tf, setup_api_url_from_tf):
    pass
