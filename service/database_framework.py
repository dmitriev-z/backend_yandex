from typing import Any, Dict, List, NewType

import pymongo

Imports = NewType('Imports', List[int])
NewImportId = NewType('NewImportId', int)
Citizen = Dict[str, Any]
Citizens = NewType('Citizens', List[Citizen])
CitizensDict = NewType('CitizensDict', Dict[int, Citizen])
CitizenRelatives = NewType('CitizenRelatives', List[int])


class DataBase:
    def __init__(self) -> None:
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client['yandexbackend']

    def __del__(self) -> None:
        self.close()

    @property
    def imports(self) -> Imports:
        return sorted(int(import_name) for import_name in self.db.list_collection_names())

    def close(self) -> None:
        self.client.close()

    def insert_citizens_to_new_import(self, citizens: Citizens) -> NewImportId:
        imports = self.imports
        new_import_id = imports[-1] + 1 if imports else 1
        new_import = self.db[f'{new_import_id}']
        new_import.insert_many(citizens)
        return new_import_id

    def get_all_import_citizens(self, import_id: int) -> Citizens:
        import_ = self.db[f'{import_id}']
        citizens = list(import_.find({}))
        for citizen in citizens:
            citizen.pop('_id')
        return sorted(citizens, key=lambda c: c['citizen_id'])

    def get_citizens_with_relatives_dict(self, import_id: int) -> CitizensDict:
        import_ = self.db[f'{import_id}']
        citizens = list(import_.find({'relatives': {'$not': {'$size': 0}}}))
        citizens_with_relatives_dict = {}
        for citizen in citizens:
            citizen.pop('_id')
        citizens = sorted(citizens, key=lambda c: len(c['relatives']))
        for citizen in citizens:
            citizens_with_relatives_dict[citizen['citizen_id']] = citizen
        return citizens_with_relatives_dict

    def get_citizen(self, import_id: int, citizen_id: int) -> Citizen:
        import_ = self.db[f'{import_id}']
        citizen = import_.find_one({'citizen_id': citizen_id})
        citizen.pop('_id')
        return citizen

    def get_citizen_relatives(self, import_id: int, citizen_id: int) -> CitizenRelatives:
        import_ = self.db[f'{import_id}']
        citizen = self.get_citizen(import_id, citizen_id)
        citizen_relatives = citizen['relatives']
        citizen_relatives = [import_.find_one({'citizen_id': related_id}) for related_id in citizen_relatives]
        for related_citizen in citizen_relatives:
            related_citizen.pop('_id')
        return citizen_relatives

    def check_if_citizen_in_import(self, import_id: int, citizen_id: int) -> bool:
        import_ = self.db[f'{import_id}']
        citizen = import_.find_one({'citizen_id': citizen_id})
        return True if citizen else False

    def update_citizen(self, import_id: int, citizen_id: int, citizen: Citizen) -> None:
        import_ = self.db[f'{import_id}']
        import_.update_one({'citizen_id': citizen_id}, {'$set': citizen})

    def remove_citizen_from_old_relatives(self, import_id: int, citizen_id: int) -> None:
        citizen_relatives = self.get_citizen_relatives(import_id, citizen_id)
        for related_citizen in citizen_relatives:
            related_citizen_relatives = related_citizen['relatives']
            related_citizen_relatives.remove(citizen_id)
            self.update_citizen(import_id, related_citizen['citizen_id'], {'relatives': related_citizen_relatives})

    def add_citizen_to_new_relatives(self, import_id: int, citizen_id: int) -> None:
        citizen_relatives = self.get_citizen_relatives(import_id, citizen_id)
        for related_citizen in citizen_relatives:
            related_citizen_relatives = related_citizen['relatives']
            related_citizen_relatives.append(citizen_id)
            self.update_citizen(import_id, related_citizen['citizen_id'], {'relatives': related_citizen_relatives})
