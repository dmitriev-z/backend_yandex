# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [3.1.0] - 2019-08-30
## Added
- Custom Validator class to `/service/service_framework.py`
- `_prepare_citizens` private method to `/service/database_framework.py`

## Changed
- Data validation methods moved to Validator class
- Birthdate storing methods from `str` to `datetime.datetime`
- `get_citizen_relatives` moved to private method `_get_citizen_relatives`
- `get_import_citizens_birthdays` method from `/service/service_framework.py` reworked to operate with `datetime.datetime`
- Service tests reworked to operate with `datetime.datetime`

## [3.0.1] - 2019-08-30
## Changed
- Double quotes replaced with single quotes in string variables

## [3.0.0] - 2019-08-28
## Added
- `/tests/__init__` file for adding path to service modules to `sys.path`
- `NewType` variables for all types used in service modules
- Type hints to methods in `/service/service_api.py`, `/tests/test_service.py`, `/tests/conftest,py`
- Type hints to methods in `/service/database_framework.py` and `/service/service_framework` 
in places where they were forgotten
- Steps for removing `_id` field from data returned from database

## Changed
- Service architecture:
  - `conftest.py` and `test_service.py` moved to `/tests` folder
  - API module moved to `/service/service_api.py`
  - API requests processing logic moved to `/service/service_framework.py`
  - `db.py` module renamed to `database_framework.py` and moved to `/service/database_framework.py`
  - WSGI configuration file moved to `/service/wsgi.py`
- Documentation about service initialization in README file
- Documentation about service testing in README file

## [2.0.0] - 2019-08-28
## Added
- `get_citizens_with_relatives_dict` method to database framework
- `BirthdayFmt` variable to service
- New REST API method `get_birthdays`
- Test for new REST API method (class `TestGetBirthdays`)
- Documentation for new REST API method to README file
- `test_get_incorrect_import_citizens` test method

## Changed
- `TestGet` renamed to `TestGetCitizens`

## Removed
- Unnecessary sleep from tests
- `import time` from tests

## [1.1.1] - 2019-08-28
## Added
- `generate_10000_citizens_with_1000_relations` method to tests
- `test_patch_citizen_request_time` test method
- `test_get_citizens_request_time` test method

## Changed
- `test_big_import_request_time` test method structure
- `test_big_import_request_time` renamed to `test_import_request_time`
- `test_correct_citizens_patch` test method

## [1.1.0] - 2019-08-28
## Changed
- Request data validation algorithms

## Fixed
- `test_get_citizens`

## [1.0.6] - 2019-08-27
## Added
- Service test instructions to README file

## [1.0.5] - 2019-08-27
## Added
- Service start instructions to README file

## [1.0.4] - 2019-08-27
## Added
- Service setup instructions to README file
- qunicorn to `requirements.txt`

## [1.0.3] - 2019-08-27
## Added
- Table of contents to README file
- Additional info about service to README file
- Service control instructions to README file

## Fixed
- Typos in README file

## [1.0.2] - 2019-08-27
## Added
- Info about service to README file

### Changed
- Release format in CHANGELOG file

### Fixed
- Data of 1.0.1 release in CHANGELOG file

## [1.0.1] - 2019-08-27
### Added
- CHANGELOG file (`CHANGELOG.md`)

## [1.0.0] - 2019-08-26
### Added
- Base service program (`service.py`)
- DataBase framework to operate with MongoDB (`db.py`)
- Service tests (`test_service.py`)
- Test configuration file (`conftest.py`)
- Service WSGI application (`wsgi.py`)
- Service requirements file (`requirements.txt`)
- README file (`README.md`)
