import json
from aiogram.types import File


def as_file(dct):
    """Decode json to File object"""
    if '_conf' in dct and '_values' in dct:
        file = File()
        file.file_id = dct['_values']['file_id']
        file.file_unique_id = dct['_values']['file_unique_id']
        file.file_size = dct['_values']['file_size']
        file.file_path = dct['_values']['file_path']
        return file
    return dct
