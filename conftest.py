import pytest


def pytest_addoption(parser):
    parser.addoption("--username", action="store", default="GitHub username")
    parser.addoption(
        "--token", action="store", default="GitHub API personal access token"
    )


@pytest.fixture(scope="session")
def username(request):
    name_value = request.config.option.username
    if name_value is None:
        pytest.skip()
    return name_value


@pytest.fixture(scope="session")
def token(request):
    name_value = request.config.option.token
    if name_value is None:
        pytest.skip()
    return name_value
