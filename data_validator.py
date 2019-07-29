import os
from datetime import datetime

import jsonschema
from bson import json_util
from jsonschema import ValidationError


class DataValidator(object):
    def __init__(self):
        import_schema_path = os.path.join(os.path.dirname(__file__), 'schemas', 'import_schema.json')
        with open(import_schema_path) as f:
            self.import_schema = json_util.loads(f.read())

    def validate_import(self, import_data: dict):
        jsonschema.validate(import_data, self.import_schema)

        citizen_ids = {citizen['citizen_id'] for citizen in import_data['citizens']}
        if len(citizen_ids) != len(import_data['citizens']):
            raise ValidationError('Citizens ids are not unique')

        citizen_relatives = {citizen['citizen_id']: set(citizen['relatives']) for citizen in import_data['citizens']}
        for citizen in import_data['citizens']:
            citizen_id = citizen['citizen_id']
            relatives = citizen_relatives[citizen_id]

            if citizen_id in relatives:
                raise ValidationError('Citizen can not be relative to himself')
            for relative_id in relatives:
                if relative_id not in citizen_ids:
                    raise ValidationError('Citizen relative does not exists')
                if citizen_id not in citizen_relatives[relative_id]:
                    raise ValidationError('Citizen relatives are not duplex')

            try:
                citizen['birth_date'] = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
            except ValueError as e:
                raise ValidationError('Citizen\'s birth_date format is incorrect: ' + str(e))