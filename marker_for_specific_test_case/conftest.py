# content of conftest.py

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--TC",
        action="store",
        metavar="NAME",
        help="only run tests matching the environment NAME.",
    )


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers", "testcase(name): mark test to run only on named environment"
    )


def pytest_runtest_setup(item):
    envnames = [mark.args[0] for mark in item.iter_markers(name="testcase")]
    if envnames:
        if item.config.getoption("--TC") not in envnames:
            pytest.skip("test requires env in {!r}".format(envnames))