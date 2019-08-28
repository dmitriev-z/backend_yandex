from _pytest.config import argparsing


def pytest_addoption(parser: argparsing.Parser):
    parser.addoption('--service-address', action='store', default='127.0.0.1:5000')
