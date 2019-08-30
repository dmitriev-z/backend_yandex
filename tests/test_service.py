import collections
import copy
import datetime
import numpy
from typing import Any, Dict, Optional

import pytest
import requests
from _pytest import config
from _pytest import fixtures

from service import database_framework
from service import service_framework

CORRECT_CITIZENS_DATA = {
    'citizens': [
        {
            'citizen_id': 1,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к7стр5',
            'apartment': 7,
            'name': 'Иванов Иван Иванович',
            'birth_date': '26.12.1986',
            'gender': 'male',
            'relatives': [2],
        },
        {
            'citizen_id': 2,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к7стр5',
            'apartment': 7,
            'name': 'Иванов Сергей Иванович',
            'birth_date': '01.04.1997',
            'gender': 'male',
            'relatives': [1],
        },
        {
            'citizen_id': 3,
            'town': 'Керчь',
            'street': 'Иосифа Бродского',
            'building': '2',
            'apartment': 11,
            'name': 'Романова Мария Леонидовна',
            'birth_date': '23.11.1986',
            'gender': 'female',
            'relatives': []
        },
    ]
}
CORRECT_CITIZEN_DATA = {'citizens': [copy.deepcopy(CORRECT_CITIZENS_DATA['citizens'][0])]}
CORRECT_CITIZEN_DATA['citizens'][0]['relatives'] = []
CITIZEN_ATTRS = [
        service_framework.CitizenAttr.ID,
        service_framework.CitizenAttr.TOWN,
        service_framework.CitizenAttr.STREET,
        service_framework.CitizenAttr.BUILDING,
        service_framework.CitizenAttr.APARTMENT,
        service_framework.CitizenAttr.NAME,
        service_framework.CitizenAttr.BIRTH_DATE,
        service_framework.CitizenAttr.GENDER,
        service_framework.CitizenAttr.RELATIVES,
    ]
CITIZEN_ATTRS_WITHOUT_ID = copy.deepcopy(CITIZEN_ATTRS)
CITIZEN_ATTRS_WITHOUT_ID.remove(service_framework.CitizenAttr.ID)


def prepare_citizens(citizens: database_framework.Citizens) -> database_framework.Citizens:
    for citizen in citizens:
        citizen['birth_date'] = datetime.datetime.strptime(citizen['birth_date'], database_framework.BirthDateFmt)
    return citizens


def calculate_citizen_age(current_date: datetime.date, citizen_birth_date: datetime.date) -> int:
    citizen_birth_date_passed = (
            (current_date.month, current_date.day) < (citizen_birth_date.month, citizen_birth_date.day)
    )
    return current_date.year - citizen_birth_date.year - citizen_birth_date_passed


@pytest.fixture()
def database(request: fixtures.FixtureRequest) -> database_framework.DataBase:
    database = database_framework.DataBase()

    def database_teardown():
        for collection in database.imports:
            database.db.drop_collection(f'{collection}')
        database.close()
    request.addfinalizer(database_teardown)
    return database


@pytest.fixture()
def service_address(pytestconfig: config.Config) -> str:
    return pytestconfig.getoption('service_address')


def generate_10000_citizens_with_1000_relations() -> Dict[str, service_framework.Citizen]:
    test_data = {'citizens': []}
    for i in range(1, 10001):
        citizen = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'][0])
        citizen['citizen_id'] = i
        test_data['citizens'].append(citizen)
    for i in range(0, 2000, 2):
        test_data['citizens'][i]['relatives'] = [i + 2]
        test_data['citizens'][i + 1]['relatives'] = [i + 1]
    return test_data


class TestImport:
    @pytest.mark.parametrize(
        'data',
        [
            None,
            {},
            [],
            1,
            True,
            [{}],
            [1],
            [True],
            [''],
            {'citizens': []},
            {'citizens': {}},
            {'citizens': 1},
            {'citizens': ''},
            {'citizens': None},
            {'citizens': True},
        ],
        ids=[
            'no data',
            'empty data (dict)',
            'empty data (list)',
            'list with dict',
            'list with number',
            'list with boolean',
            'list with string',
            'int data',
            'boolean data',
            'empty list "citizens"',
            'dict "citizens"',
            'number "citizens"',
            'string "citizens"',
            'null "citizens"',
            'boolean "citizens"',
        ],
    )
    def test_incorrect_request_data(
            self,
            service_address: str,
            database: database_framework.DataBase,
            data: Optional[dict],
    ) -> None:
        if data is None:
            r = requests.post(f'http://{service_address}/imports')
        else:
            r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'attr',
        CITIZEN_ATTRS,
        ids=[
            'citizen without "citizen_id"',
            'citizen without "town"',
            'citizen without "street"',
            'citizen without "building"',
            'citizen without "apartment"',
            'citizen without "name"',
            'citizen without "birth_date"',
            'citizen without "gender"',
            'citizen without "relatives"',
        ],
    )
    def test_import_citizen_without_attr(
            self,
            service_address: str,
            database: database_framework.DataBase,
            attr: service_framework.CitizenAttr,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0].pop(attr.value)

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'attr',
        CITIZEN_ATTRS,
        ids=[
            'citizen with null "citizen_id"',
            'citizen with null "town"',
            'citizen with null "street"',
            'citizen with null "building"',
            'citizen with null "apartment"',
            'citizen with null "name"',
            'citizen with null "birth_date"',
            'citizen with null "gender"',
            'citizen with null "relatives"',
        ],
    )
    def test_import_citizen_with_null_attr(
            self,
            service_address: str,
            database: database_framework.DataBase,
            attr: service_framework.CitizenAttr,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][attr.value] = None

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    def test_import_citizen_with_external_attr(
            self,
            service_address: str,
            database: database_framework.DataBase,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0]['external_attr'] = 'external'

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'citizen_id',
        [
            -100,
            15.5,
            '',
            True,
            list(),
            dict(),
        ],
        ids=[
            'citizen with "citizen_id" negative',
            'citizen with "citizen_id" float',
            'citizen with "citizen_id" string',
            'citizen with "citizen_id" boolean',
            'citizen with "citizen_id" list',
            'citizen with "citizen_id" dict',
        ]
    )
    def test_import_citizen_with_incorrect_id(
            self,
            service_address: str,
            database: database_framework.DataBase,
            citizen_id: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.ID.value] = citizen_id

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'town',
        [
            100,
            15.5,
            '',
            ' ',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'citizen with "town" int',
            'citizen with "town" float',
            'citizen with "town" empty string',
            'citizen with "town" string with no letter or digit',
            'citizen with "town" string longer than 256',
            'citizen with "town" boolean',
            'citizen with "town" list',
            'citizen with "town" dict',
        ]
    )
    def test_import_citizen_with_incorrect_town(
            self,
            service_address: str,
            database: database_framework.DataBase,
            town: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.TOWN.value] = town

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'street',
        [
            100,
            15.5,
            '',
            ' ',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'citizen with "street" int',
            'citizen with "street" float',
            'citizen with "street" empty string',
            'citizen with "street" string with no letter or digit',
            'citizen with "street" string longer than 256',
            'citizen with "street" boolean',
            'citizen with "street" list',
            'citizen with "street" dict',
        ]
    )
    def test_import_citizen_with_incorrect_street(
            self,
            service_address: str,
            database: database_framework.DataBase,
            street: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.STREET.value] = street

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'building',
        [
            100,
            15.5,
            '',
            ' ',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'citizen with "building" int',
            'citizen with "building" float',
            'citizen with "building" empty string',
            'citizen with "building" string with no letter or digit',
            'citizen with "building" string longer than 256',
            'citizen with "building" boolean',
            'citizen with "building" list',
            'citizen with "building" dict',
        ]
    )
    def test_import_citizen_with_incorrect_building(
            self,
            service_address: str,
            database: database_framework.DataBase,
            building: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.BUILDING.value] = building

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'apartment',
        [
            -100,
            15.5,
            '',
            True,
            list(),
            dict(),
        ],
        ids=[
            'citizen with "apartment" negative',
            'citizen with "apartment" float',
            'citizen with "apartment" string',
            'citizen with "apartment" boolean',
            'citizen with "apartment" list',
            'citizen with "apartment" dict',
        ]
    )
    def test_import_citizen_with_incorrect_apartment(
            self,
            service_address: str,
            database: database_framework.DataBase,
            apartment: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.APARTMENT.value] = apartment

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'name',
        [
            100,
            15.5,
            '',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'citizen with "name" int',
            'citizen with "name" float',
            'citizen with "name" empty string',
            'citizen with "name" string longer than 256',
            'citizen with "name" boolean',
            'citizen with "name" list',
            'citizen with "name" dict',
        ]
    )
    def test_import_citizen_with_incorrect_name(
            self,
            service_address: str,
            database: database_framework.DataBase,
            name: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.NAME.value] = name

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'birth_date',
        [
            100,
            15.5,
            '',
            True,
            list(),
            dict(),
            '31.02.1999',
            (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%d.%m.$Y'),
        ],
        ids=[
            'citizen with "birth_date" integer',
            'citizen with "birth_date" float',
            'citizen with "birth_date" empty string',
            'citizen with "birth_date" boolean',
            'citizen with "birth_date" list',
            'citizen with "birth_date" dict',
            'citizen with "birth_date" wrong date',
            'citizen with "birth_date" date more than current',
        ]
    )
    def test_import_citizen_with_incorrect_birth_date(
            self,
            service_address: str,
            database: database_framework.DataBase,
            birth_date: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.BIRTH_DATE.value] = birth_date

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'gender',
        [
            100,
            15.5,
            '',
            True,
            list(),
            dict(),
            'mala',
        ],
        ids=[
            'citizen with "gender" int',
            'citizen with "gender" float',
            'citizen with "gender" empty string',
            'citizen with "gender" boolean',
            'citizen with "gender" list',
            'citizen with "gender" dict',
            'citizen with "gender" not allowed'
        ]
    )
    def test_import_citizen_with_incorrect_gender(
            self,
            service_address: str,
            database: database_framework.DataBase,
            gender: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.GENDER.value] = gender

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'relatives',
        [
            100,
            15.5,
            '',
            True,
            dict(),
            [1.5],
            [''],
            [True],
            [{}],
            [None],
            [1],
            [2],
        ],
        ids=[
            'citizen with "relatives" int',
            'citizen with "relatives" float',
            'citizen with "relatives" string',
            'citizen with "relatives" boolean',
            'citizen with "relatives" dict',
            'citizen with "relatives" list of floats',
            'citizen with "relatives" list of strings',
            'citizen with "relatives" list of booleans',
            'citizen with "relatives" list of dicts',
            'citizen with "relatives" list of nulls',
            'citizen with "relatives" to himself',
            'citizen with "relatives" to non-existing citizen',
        ]
    )
    def test_import_citizen_with_incorrect_relatives(
            self,
            service_address: str,
            database: database_framework.DataBase,
            relatives: Any,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZEN_DATA)
        data['citizens'][0][service_framework.CitizenAttr.RELATIVES.value] = relatives

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    def test_import_citizen_with_relative_to_citizen_who_not_in_relatives_with_him(
            self,
            service_address: str,
            database: database_framework.DataBase,
    ) -> None:
        data = copy.deepcopy(CORRECT_CITIZENS_DATA)
        data['citizens'][1]['relatives'].pop()

        r = requests.post(f'http://{service_address}/imports', json=data)

        assert r.status_code == 400
        assert database.imports == []

    @pytest.mark.parametrize(
        'citizens',
        [copy.deepcopy(CORRECT_CITIZEN_DATA), copy.deepcopy(CORRECT_CITIZENS_DATA)],
        ids=['single citizen', 'two citizens'],
    )
    def test_import_correct_citizens(
            self,
            service_address: str,
            database: database_framework.DataBase,
            citizens: Dict[str, service_framework.Citizens],
    ) -> None:
        r = requests.post(f'http://{service_address}/imports', json=citizens)

        expected_json = {'data': {'import_id': 1}}

        assert r.status_code == 201
        assert r.json() == expected_json
        assert database.imports == [1]

        expected_data = sorted(citizens['citizens'], key=lambda citizen: citizen['citizen_id'])

        assert database.get_all_import_citizens(1) == expected_data

    def test_import_several_citizens(self, service_address: str, database: database_framework.DataBase, ) -> None:
        imports = list()
        for i in range(1, 6):
            imports.append(i)

            r = requests.post(f'http://{service_address}/imports', json=CORRECT_CITIZEN_DATA)

            expected_json = {'data': {'import_id': i}}

            assert r.status_code == 201
            assert r.json() == expected_json
            assert database.imports == imports

    def test_import_request_time(self, service_address: str, database: database_framework.DataBase) -> None:
        request_time = datetime.datetime.utcnow()
        r = requests.post(f'http://{service_address}/imports', json=generate_10000_citizens_with_1000_relations())
        response_time = datetime.datetime.utcnow()
        eval_time = (response_time - request_time).total_seconds()

        assert r.status_code == 201
        assert eval_time <= 10.0


class TestPatch:
    @pytest.mark.parametrize(
        'data',
        [
            None,
            {},
            [],
            1,
            True,
            [{}],
            [1],
            [True],
            [''],
        ],
        ids=[
            'no data',
            'empty data (dict)',
            'empty data (list)',
            'number data',
            'boolean data',
            'list with dict',
            'list with number',
            'list with boolean',
            'list with string',
        ],
    )
    def test_incorrect_request_data(
            self,
            service_address: str,
            database: database_framework.DataBase,
            data: Optional[dict],
    ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        if data is None:
            r = requests.patch(f'http://{service_address}/imports/1/citizens/1')
        else:
            r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json=data)

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    def test_patch_citizen_id(self, service_address: str, database: database_framework.DataBase, ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'citizen_id': 2})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'attr',
        CITIZEN_ATTRS_WITHOUT_ID,
        ids=[
            'citizen with null "town"',
            'citizen with null "street"',
            'citizen with null "building"',
            'citizen with null "apartment"',
            'citizen with null "name"',
            'citizen with null "birth_date"',
            'citizen with null "gender"',
            'citizen with null "relatives"',
        ],
    )
    def test_patch_null_attr(
            self,
            service_address: str,
            database: database_framework.DataBase,
            attr: service_framework.CitizenAttr,
    ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={attr.value: None})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    def test_patch_external_attr(self, service_address: str, database: database_framework.DataBase, ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'external': 'external'})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'town',
        [
            100,
            15.5,
            '',
            ' ',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'patch "town" int',
            'patch "town" float',
            'patch "town" empty string',
            'patch "town" string with no letter or digit',
            'patch "town" string longer than 256',
            'patch "town" boolean',
            'patch "town" list',
            'patch "town" dict',
        ]
    )
    def test_patch_incorrect_town(self, service_address: str, database: database_framework.DataBase, town: Any) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'town': town})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'street',
        [
            100,
            15.5,
            '',
            ' ',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'patch "street" int',
            'patch "street" float',
            'patch "street" empty string',
            'patch "street" string with no letter or digit',
            'patch "street" string longer than 256',
            'patch "street" boolean',
            'patch "street" list',
            'patch "street" dict',
        ]
    )
    def test_patch_incorrect_street(
            self,
            service_address: str,
            database: database_framework.DataBase,
            street: Any,
    ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'street': street})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'building',
        [
            100,
            15.5,
            '',
            ' ',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'patch "building" int',
            'patch "building" float',
            'patch "building" empty string',
            'patch "building" string with no letter or digit',
            'patch "building" string longer than 256',
            'patch "building" boolean',
            'patch "building" list',
            'patch "building" dict',
        ]
    )
    def test_patch_incorrect_building(
            self,
            service_address: str,
            database: database_framework.DataBase,
            building: Any,
    ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'building': building})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'apartment',
        [
            -100,
            15.5,
            '',
            True,
            list(),
            dict(),
        ],
        ids=[
            'patch "apartment" negative',
            'patch "apartment" float',
            'patch "apartment" string',
            'patch "apartment" boolean',
            'patch "apartment" list',
            'patch "apartment" dict',
        ]
    )
    def test_patch_apartment(self, service_address: str, database: database_framework.DataBase, apartment: Any) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'apartment': apartment})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'name',
        [
            100,
            15.5,
            '',
            '' * 257,
            True,
            list(),
            dict(),
        ],
        ids=[
            'patch "name" int',
            'patch "name" float',
            'patch "name" empty string',
            'patch "name" string longer than 256',
            'patch "name" boolean',
            'patch "name" list',
            'patch "name" dict',
        ]
    )
    def test_patch_incorrect_name(self, service_address: str, database: database_framework.DataBase, name: Any) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'name': name})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'birth_date',
        [
            100,
            15.5,
            '',
            True,
            list(),
            dict(),
            '31.02.1999',
            (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%d.%m.$Y'),
        ],
        ids=[
            'patch "birth_date" integer',
            'patch "birth_date" float',
            'patch "birth_date" empty string',
            'patch "birth_date" boolean',
            'patch "birth_date" list',
            'patch "birth_date" dict',
            'patch "birth_date" wrong date',
            'patch "birth_date" date more than current',
        ]
    )
    def test_patch_incorrect_birth_date(
            self,
            service_address: str,
            database: database_framework.DataBase,
            birth_date: Any,
    ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'birth_date': birth_date})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'gender',
        [
            100,
            15.5,
            '',
            True,
            list(),
            dict(),
            'mala',
        ],
        ids=[
            'patch "gender" int',
            'patch "gender" float',
            'patch "gender" empty string',
            'patch "gender" boolean',
            'patch "gender" list',
            'patch "gender" dict',
            'patch "gender" not allowed'
        ]
    )
    def test_patch_incorrect_gender(
            self,
            service_address: str,
            database: database_framework.DataBase,
            gender: Any,
    ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'gender': gender})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    @pytest.mark.parametrize(
        'relatives',
        [
            100,
            15.5,
            '',
            True,
            dict(),
            [1.5],
            [''],
            [True],
            [{}],
            [None],
            [1],
            [2],
        ],
        ids=[
            'patch "relatives" int',
            'patch "relatives" float',
            'patch "relatives" string',
            'patch "relatives" boolean',
            'patch "relatives" dict',
            'patch "relatives" list of floats',
            'patch "relatives" list of strings',
            'patch "relatives" list of booleans',
            'patch "relatives" list of dicts',
            'patch "relatives" list of nulls',
            'patch "relatives" to himself',
            'patch "relatives" to non-existing citizen',
        ]
    )
    def test_patch_incorrect_relatives(
            self,
            service_address: str,
            database: database_framework.DataBase,
            relatives: Any,
    ) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json={'relatives': relatives})

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    def test_patch_non_existing_citizen(self, service_address: str, database: database_framework.DataBase) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZEN_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        data = {
            'street': 'Пушкина',
        }
        r = requests.patch(f'http://{service_address}/imports/1/citizens/2', json=data)

        assert r.status_code == 400
        assert sorted(citizens, key=lambda c: c['citizen_id']) == database.get_all_import_citizens(1)

    def test_correct_citizens_patch(self, service_address: str, database: database_framework.DataBase) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZENS_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        data = {
            'name': 'Иванова Мария Леонидовна',
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к7стр5',
            'apartment': 7,
            'relatives': [1],
        }
        r = requests.patch(f'http://{service_address}/imports/1/citizens/3', json=data)

        assert r.status_code == 200

        expected_json = {
            'data': {
                'citizen_id': 3,
                'town': 'Москва',
                'street': 'Льва Толстого',
                'building': '16к7стр5',
                'apartment': 7,
                'name': 'Иванова Мария Леонидовна',
                'birth_date': '23.11.1986',
                'gender': 'female',
                'relatives': [1],
            }
        }

        assert r.json() == expected_json

        expected_citizens = copy.deepcopy(CORRECT_CITIZENS_DATA['citizens'])
        expected_citizens[2].update(expected_json['data'])
        expected_citizens[0]['relatives'].append(3)

        assert database.get_all_import_citizens(1) == sorted(expected_citizens, key=lambda c: c['citizen_id'])

        data = {'relatives': []}
        r = requests.patch(f'http://{service_address}/imports/1/citizens/3', json=data)

        assert r.status_code == 200

        expected_json = {
            'data': {
                'citizen_id': 3,
                'town': 'Москва',
                'street': 'Льва Толстого',
                'building': '16к7стр5',
                'apartment': 7,
                'name': 'Иванова Мария Леонидовна',
                'birth_date': '23.11.1986',
                'gender': 'female',
                'relatives': [],
            }
        }

        assert r.json() == expected_json

        expected_citizens[2].update(expected_json['data'])
        expected_citizens[0]['relatives'].remove(3)

        assert database.get_all_import_citizens(1) == sorted(expected_citizens, key=lambda c: c['citizen_id'])

    def test_patch_citizen_request_time(self, service_address: str, database: database_framework.DataBase) -> None:
        citizens = copy.deepcopy(generate_10000_citizens_with_1000_relations()['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(citizens))

        data = {
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к7стр5',
            'apartment': 7,
            'name': 'Иванов Иван Иванович',
            'birth_date': '26.12.1986',
            'gender': 'male',
            'relatives': [3],
        }
        request_time = datetime.datetime.now()
        r = requests.patch(f'http://{service_address}/imports/1/citizens/1', json=data)
        response_time = datetime.datetime.now()
        eval_time = (response_time - request_time).total_seconds()

        assert r.status_code == 200
        assert eval_time <= 10.0


class TestGetCitizens:
    def test_get_incorrect_import_citizens(self, service_address: str, database: database_framework.DataBase) -> None:
        r = requests.get(f'http://{service_address}/imports/1/citizens')
        assert r.status_code == 400

    def test_get_citizens(self, service_address: str, database: database_framework.DataBase) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZENS_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(copy.deepcopy(citizens)))

        r = requests.get(f'http://{service_address}/imports/1/citizens')

        assert r.status_code == 200

        expected_json = {'data': citizens}

        assert r.json() == expected_json

    def test_get_citizens_request_time(self, service_address: str, database: database_framework.DataBase) -> None:
        citizens = copy.deepcopy(generate_10000_citizens_with_1000_relations()['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(citizens))

        request_time = datetime.datetime.utcnow()
        r = requests.get(f'http://{service_address}/imports/1/citizens')
        response_time = datetime.datetime.utcnow()
        eval_time = (response_time - request_time).total_seconds()

        assert r.status_code == 200
        assert eval_time <= 10.0


class TestGetBirthdays:
    def test_get_incorrect_import_birthdays(self, service_address: str, database: database_framework.DataBase) -> None:
        r = requests.get(f'http://{service_address}/imports/1/citizens/birthdays')
        assert r.status_code == 400

    def test_get_birthdays(self, service_address: str, database: database_framework.DataBase) -> None:
        citizens = copy.deepcopy(CORRECT_CITIZENS_DATA['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(citizens))

        r = requests.get(f'http://{service_address}/imports/1/citizens/birthdays')

        assert r.status_code == 200

        expected_birthdays = {
            '1': [],
            '2': [],
            '3': [],
            '4': [{'citizen_id': 1, 'presents': 1}],
            '5': [],
            '6': [],
            '7': [],
            '8': [],
            '9': [],
            '10': [],
            '11': [],
            '12': [{'citizen_id': 2, 'presents': 1}],
        }
        expected_json = {'data': expected_birthdays}

        assert r.json() == expected_json

    def test_get_birthdays_request_time(self, service_address: str, database: database_framework.DataBase) -> None:
        citizens = copy.deepcopy(generate_10000_citizens_with_1000_relations()['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(citizens))

        request_time = datetime.datetime.utcnow()
        r = requests.get(f'http://{service_address}/imports/1/citizens/birthdays')
        response_time = datetime.datetime.utcnow()
        eval_time = (response_time - request_time).total_seconds()

        assert r.status_code == 200
        assert eval_time <= 10.0


class TestGetTownsPercentileAgeStats:
    def test_get_incorrect_import_towns_percentile_age_stats(
            self,
            service_address: str,
            database: database_framework.DataBase,
    ) -> None:
        r = requests.get(f'http://{service_address}/imports/1/towns/stat/percentile/age')
        assert r.status_code == 400

    def test_get_towns_percentile_age_stats(self, service_address: str, database: database_framework.DataBase) -> None:
        current_date = datetime.datetime.utcnow()

        citizens = copy.deepcopy(CORRECT_CITIZENS_DATA['citizens'])
        citizens = prepare_citizens(citizens)
        database.insert_citizens_to_new_import(citizens)

        r = requests.get(f'http://{service_address}/imports/1/towns/stat/percentile/age')
        assert r.status_code == 200

        towns_age_stats = collections.defaultdict(list)
        for citizen in citizens:
            towns_age_stats[citizen['town']].append(
                calculate_citizen_age(current_date.date(), citizen['birth_date'].date())
            )

        percentiles = [50, 75, 99]
        expected_towns_percentile_age_stats = list()
        for town, ages in towns_age_stats.items():
            town_percentile_age_stats = {'town': town}
            ages_array = numpy.array(ages)
            for percentile in percentiles:
                town_percentile_age_stats.update(
                    {f'p{percentile}': round(numpy.percentile(ages_array, percentile, interpolation='linear'), 2)}
                )
            expected_towns_percentile_age_stats.append(town_percentile_age_stats)
        expected_json = {'data': expected_towns_percentile_age_stats}

        assert r.json() == expected_json

    def test_get_towns_percentile_age_stats_request_time(
            self,
            service_address: str,
            database: database_framework.DataBase,
    ) -> None:
        citizens = copy.deepcopy(generate_10000_citizens_with_1000_relations()['citizens'])
        database.insert_citizens_to_new_import(prepare_citizens(citizens))

        request_time = datetime.datetime.utcnow()
        r = requests.get(f'http://{service_address}/imports/1/towns/stat/percentile/age')
        response_time = datetime.datetime.utcnow()
        eval_time = (response_time - request_time).total_seconds()

        assert r.status_code == 200
        assert eval_time <= 10.0
