import collections
import copy
import datetime
import enum
import multiprocessing
import re
from typing import Any, Dict, List, Optional, Tuple, Union

import cerberus
import flask

import db

Counter = Dict[int, int]
CitizenDict = Dict[str, Any]
CitizensList = List[CitizenDict]
ValidatedCitizen = Dict[str, Union[int, str, List[int]]]
ValidatedCitizensList = List[ValidatedCitizen]
BirthdayFmt = '%d.%m.%Y'


app = flask.Flask(__name__)
data_base = db.DataBase()


class CitizenAttr(enum.Enum):
    ID = 'citizen_id'
    TOWN = 'town'
    STREET = 'street'
    BUILDING = 'building'
    APARTMENT = 'apartment'
    NAME = 'name'
    BIRTH_DATE = 'birth_date'
    GENDER = 'gender'
    RELATIVES = 'relatives'


def _validate_string(field, value, error):
    if value is None:
        error(field, 'Could not be NoneType')
    else:
        pattern = re.compile(r'[^\W_]')
        if not pattern.match(value):
            error(field, 'Must contain at least one letter or digit')


def _validate_date(field, value, error):
    try:
        date = datetime.datetime.strptime(value, BirthdayFmt).date()
    except (TypeError, ValueError):
        error(field, 'Wrong date format.')
    else:
        if date > datetime.datetime.utcnow().date():
            error(field, 'Birth date could not be more than current date.')


class CitizenValidator:
    CITIZEN_VALIDATION_SCHEMA = {
        'citizen_id': {'type': 'integer', 'min': 0, 'coerce': lambda v: None if isinstance(v, bool) else v},
        'town': {'type': 'string', 'minlength': 1, 'maxlength': 256, 'check_with': _validate_string},
        'street': {'type': 'string', 'minlength': 1, 'maxlength': 256, 'check_with': _validate_string},
        'building': {'type': 'string', 'minlength': 1, 'maxlength': 256, 'check_with': _validate_string},
        'apartment': {'type': 'integer', 'min': 0, 'coerce': lambda v: None if isinstance(v, bool) else v},
        'name': {'type': 'string', 'minlength': 1, 'maxlength': 256},
        'birth_date': {'check_with': _validate_date},
        'gender': {'type': 'string', 'allowed': ['male', 'female']},
        'relatives': {'type': 'list', 'schema': {'type': 'integer'}},
    }
    CITIZEN_VALIDATION_SCHEMA_WITHOUT_ID = copy.deepcopy(CITIZEN_VALIDATION_SCHEMA)
    VALIDATOR = cerberus.Validator(CITIZEN_VALIDATION_SCHEMA, require_all=True)

    @classmethod
    def validate_citizen(cls, citizen: Dict[str, Any]) -> Optional[Tuple[ValidatedCitizen, Counter, Counter]]:
        validated_citizen = cls.VALIDATOR.validated(citizen)
        if not validated_citizen:
            return None
        relatives = validated_citizen['relatives']
        if validated_citizen['citizen_id'] in relatives:
            return None
        return (
            validated_citizen,
            {validated_citizen['citizen_id']: len(relatives)} if relatives else {},
            {related_id: 1 for related_id in relatives},
        )


class CitizensValidator:
    @classmethod
    def validate_import_citizens(cls, citizens: CitizensList) -> Optional[ValidatedCitizensList]:
        validated_citizens_list = list()
        citizen_relatives = collections.Counter()
        related_citizens = collections.Counter()
        pool = multiprocessing.Pool(5)
        validated_citizens = [
            pool.apply_async(CitizenValidator.validate_citizen, args=(citizen,)) for citizen in citizens
        ]
        for res in validated_citizens:
            result = res.get()
            if not result:
                break
            validated_citizen, citizen_relatives_count, related_citizens_counts = result
            validated_citizens_list.append(validated_citizen)
            citizen_relatives.update(citizen_relatives_count)
            related_citizens.update(related_citizens_counts)
        pool.close()
        pool.join()
        if len(validated_citizens) != len(citizens):
            return None
        if not citizen_relatives == related_citizens:
            return None
        return validated_citizens_list


def get_import_citizens_birthdays(import_id: int):
    presents = {month: collections.defaultdict(int) for month in range(1, 13)}
    birthdays = {str(month): [] for month in range(1, 13)}
    citizens_with_relatives_dict = data_base.get_citizens_with_relatives_dict(import_id)
    citizen_ids = list(citizens_with_relatives_dict.keys())
    for citizen_id in citizen_ids:
        citizen = citizens_with_relatives_dict.get(citizen_id)
        if not citizen:
            continue
        citizen_relatives = citizen['relatives']
        citizen_birth_date = datetime.datetime.strptime(citizen['birth_date'], BirthdayFmt).date()
        for related_citizen_id in citizen_relatives:
            related_citizen = citizens_with_relatives_dict[related_citizen_id]
            related_citizen_birth_date = datetime.datetime.strptime(related_citizen['birth_date'], BirthdayFmt).date()
            related_citizen_relatives = related_citizen['relatives']
            presents[related_citizen_birth_date.month][citizen_id] += 1
            presents[citizen_birth_date.month][related_citizen_id] += 1
            related_citizen_relatives.remove(citizen_id)
            if not related_citizen_relatives:
                citizens_with_relatives_dict.pop(related_citizen_id)
    for month, citizen_presents in presents.items():
        for citizen_id, presents in citizen_presents.items():
            birthdays[str(month)].append({'citizen_id': citizen_id, 'presents': presents})
        birthdays[str(month)] = sorted(birthdays[str(month)], key=lambda c: c['citizen_id'])
    return birthdays


@app.route('/imports', methods=['POST'])
def import_citizens():
    data = flask.request.json
    if not isinstance(data, dict):
        return flask.make_response('Bad Request', 400)
    schema = {'citizens': {'type': 'list'}}
    validator = cerberus.Validator(schema, require_all=True)
    if not validator.validate(data):
        return flask.make_response('Bad Request', 400)
    validated_citizens = CitizensValidator.validate_import_citizens(data['citizens'])
    if not validated_citizens:
        return flask.make_response('Bad Request', 400)
    new_import_id = data_base.insert_citizens_to_new_import(validated_citizens)
    resp_json = {'data': {'import_id': new_import_id}}
    return flask.make_response(flask.jsonify(resp_json), 201)


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def patch_citizen(import_id: int, citizen_id: int):
    if import_id not in data_base.imports:
        return flask.make_response('Bad Request', 400)
    citizen = data_base.get_citizen(import_id, citizen_id)
    if not citizen:
        return flask.make_response('Bad Request', 400)
    data = flask.request.json
    if not data or not isinstance(data, dict):
        return flask.make_response('Bad Request', 400)
    if 'citizen_id' in data:
        return flask.make_response('Bad Request', 400)
    new_citizen = copy.deepcopy(citizen)
    new_citizen.pop('_id')
    new_citizen.update(data)
    validation_result = CitizenValidator.validate_citizen(new_citizen)
    if not validation_result:
        return flask.make_response('Bad Request', 400)
    validated_citizen, *a = validation_result
    relatives = validated_citizen.get('relatives')
    if not all(data_base.check_if_citizen_in_import(import_id, relative_id) for relative_id in relatives):
        return flask.make_response('Bad Request', 400)
    if any(relative_id == citizen_id for relative_id in relatives):
        return flask.make_response('Bad Request', 400)
    validated_citizen.pop('citizen_id')
    old_relatives = citizen['relatives']
    new_relatives = validated_citizen['relatives']
    if old_relatives != new_relatives:
        data_base.remove_citizen_from_old_relatives(import_id, citizen_id)
        data_base.update_citizen(import_id, citizen_id, validated_citizen)
        data_base.add_citizen_to_new_relatives(import_id, citizen_id)
    else:
        data_base.update_citizen(import_id, citizen_id, validated_citizen)
    updated_citizen = data_base.get_citizen(import_id, citizen_id)
    updated_citizen.pop('_id')
    resp_json = {'data': updated_citizen}
    return flask.make_response(flask.jsonify(resp_json), 200)


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_citizens(import_id: int):
    if import_id not in data_base.imports:
        return flask.make_response('Bad Request', 400)
    resp_json = {'data': data_base.get_all_import_citizens(import_id)}
    return flask.make_response(flask.jsonify(resp_json), 200)


@app.route('/imports/<int:import_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(import_id: int):
    if import_id not in data_base.imports:
        return flask.make_response('Bad Request', 400)
    resp_json = {'data': get_import_citizens_birthdays(import_id)}
    return flask.make_response(flask.jsonify(resp_json), 200)
