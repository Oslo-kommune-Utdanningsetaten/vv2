import os
import sys
from dotenv import load_dotenv
from pyexcel_xlsx import get_data


script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

import django
from django.db import connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from mastery import models


def objects_from_sheet(sheet, field_map):
    objects = []
    field_names = sheet[0]
    for row in sheet[1:]:
        obj = {}
        for index, field_value in enumerate(row):
            field_name = field_names[index]
            if field_name in field_map:
                mapped_field = field_map[field_name]
                obj[mapped_field] = field_value
        if bool(obj):
            objects.append(obj)
    return objects


def run_import():
    excel_file_path = os.path.join(script_dir, 'data', 'data_for_import.xlsx')
    excel_file_sheets = get_data(excel_file_path)

    # Sheet "Goal"
    if 'Goal' in excel_file_sheets:
        sheet = excel_file_sheets['Goal']
        field_map = {
            'id': 'id',
            'title': 'title',
            'student_feide_id': 'student_feide_id',
        }
        goal_dicts = objects_from_sheet(sheet, field_map=field_map)
        results = []
        for goal_dict in goal_dicts:
            student = models.User.objects.filter(feide_id__exact=goal_dict['student_feide_id']).first()
            defaults = {}
            for k, v in goal_dict.items():
                if k == 'id':
                    continue
                elif k == 'student_feide_id':
                    defaults['student'] = student
                else:
                    defaults[k] = v
            goal, created = models.Goal.objects.get_or_create(id=goal_dict['id'], defaults=defaults)
            results.append({'object': goal, 'created': created})
        print("Goals imported:", len(results))


    # Sheet "Observation"
    if 'Observation' in excel_file_sheets:
        sheet = excel_file_sheets['Observation']
        field_map = {
            'id': 'id',
            'mastery_value': 'mastery_value',
            'mastery_description': 'mastery_description',
            'feedforward': 'feedforward',
            'student_feide_id': 'student_feide_id',
            'observed_at': 'observed_at',
            'goal_id': 'goal_id',
            'observer_feide_id': 'observer_feide_id',
        }
        observation_dicts = objects_from_sheet(sheet, field_map=field_map)
        results = []
        for observation_dict in observation_dicts:
            student = models.User.objects.filter(feide_id__exact=observation_dict['student_feide_id']).first()
            observer = models.User.objects.filter(feide_id__exact=observation_dict['observer_feide_id']).first()
            goal = models.Goal.objects.filter(id=observation_dict['goal_id']).first()
            defaults = {}
            for k, v in observation_dict.items():
                if k == 'id':
                    continue
                elif k == 'student_feide_id':
                    defaults['student'] = student
                elif k == 'observer_feide_id':
                    defaults['observer'] = observer
                elif k == 'goal_id':
                    defaults['goal'] = goal
                else:
                    defaults[k] = v
            observation, created = models.Observation.objects.get_or_create(id=observation_dict['id'], defaults=defaults)
            results.append({'object': observation, 'created': created})
        print("Observations imported:", len(results))

    print("Excel import all done")

if __name__ == '__main__':
    run_import()
