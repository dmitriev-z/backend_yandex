import collections
import copy
import datetime
import enum
import multiprocessing
import re
from typing import Any, Callable, Dict, List, NewType, Optional, Tuple, Union

import cerberus

from service import database_framework

Counter = NewType('Counter', Dict[int, int])
Citizen = NewType('CitizenDict', Dict[str, Any])
Citizens = NewType('CitizensList', List[Citizen])
ValidatedCitizen = NewType('ValidatedCitizen', Dict[str, Union[int, str, List[int]]])
ValidatedCitizens = NewType('ValidatedCitizensList', List[ValidatedCitizen])
NewImportId = NewType('NewImportId', int)
PatchedCitizen = NewType('PatchedCitizen', Citizen)
ImportCitizensBirthdays = NewType('ImportCitizensBirthdays', Dict[str, List[Dict[str, int]]])

BirthdayFmt = '%d.%m.%Y'


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


def _validate_string(field: str, value: Any, error: Callable[..., Any]) -> Optional[Callable[..., Any]]:
    if value is None:
        error(field, 'Could not be NoneType')
    else:
        pattern = re.compile(r'[^\W_]')
        if not pattern.match(value):
            error(field, 'Must contain at least one letter or digit')


def _validate_date(field: str, value: Any, error: Callable[..., Any]) -> Optional[Callable[..., Any]]:
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
    def validate_import_citizens(cls, citizens: Citizens) -> Optional[ValidatedCitizens]:
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


class Service:
    def __init__(self) -> None:
        self.database = database_framework.DataBase()

    def import_citizens(self, request_json: Any) -> Optional[NewImportId]:
        if not isinstance(request_json, dict):
            return None
        schema = {'citizens': {'type': 'list'}}
        validator = cerberus.Validator(schema, require_all=True)
        if not validator.validate(request_json):
            return None
        citizens = request_json['citizens']
        validated_citizens = CitizensValidator.validate_import_citizens(citizens)
        if not validated_citizens:
            return None
        new_import_id = self.database.insert_citizens_to_new_import(validated_citizens)
        return new_import_id

    def patch_import_citizen(self, import_id: int, citizen_id: int, request_json: Any) -> Optional[PatchedCitizen]:
        if import_id not in self.database.imports:
            return None
        if not self.database.check_if_citizen_in_import(import_id, citizen_id):
            return None
        if not request_json or not isinstance(request_json, dict):
            return None
        if 'citizen_id' in request_json:
            return None
        citizen = self.database.get_citizen(import_id, citizen_id)
        patched_citizen = copy.deepcopy(citizen)
        patched_citizen.update(request_json)
        validation_result = CitizenValidator.validate_citizen(patched_citizen)
        if not validation_result:
            return None
        patched_citizen, *a = validation_result
        patched_citizen_relatives = patched_citizen['relatives']
        if not all(
                self.database.check_if_citizen_in_import(import_id, relative_id)
                for relative_id in patched_citizen_relatives
        ):
            return None
        if any(relative_id == citizen_id for relative_id in patched_citizen_relatives):
            return None
        old_relatives = citizen['relatives']
        new_relatives = patched_citizen['relatives']
        if old_relatives != new_relatives:
            self.database.remove_citizen_from_old_relatives(import_id, citizen_id)
            self.database.update_citizen(import_id, citizen_id, patched_citizen)
            self.database.add_citizen_to_new_relatives(import_id, citizen_id)
        else:
            self.database.update_citizen(import_id, citizen_id, patched_citizen)
        return patched_citizen

    def get_import_citizens(self, import_id: int) -> Optional[Citizens]:
        if import_id not in self.database.imports:
            return None
        return self.database.get_all_import_citizens(import_id)

    def get_import_citizens_birthdays(self, import_id: int) -> Optional[ImportCitizensBirthdays]:
        if import_id not in self.database.imports:
            return None
        presents = {month: collections.defaultdict(int) for month in range(1, 13)}
        birthdays = {str(month): [] for month in range(1, 13)}
        citizens_with_relatives_dict = self.database.get_citizens_with_relatives_dict(import_id)
        citizen_ids = list(citizens_with_relatives_dict.keys())
        for citizen_id in citizen_ids:
            citizen = citizens_with_relatives_dict.get(citizen_id)
            if not citizen:
                continue
            citizen_relatives = citizen['relatives']
            citizen_birth_date = datetime.datetime.strptime(citizen['birth_date'], BirthdayFmt).date()
            for related_citizen_id in citizen_relatives:
                related_citizen = citizens_with_relatives_dict[related_citizen_id]
                related_citizen_birth_date = datetime.datetime.strptime(related_citizen['birth_date'],
                                                                        BirthdayFmt).date()
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
