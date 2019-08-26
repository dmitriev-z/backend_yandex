def pytest_addoption(parser):
    parser.addoption('--service-address', action='store', default='127.0.0.1:5000')
