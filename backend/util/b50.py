# TODO: Implement b50 table generation functions

from typing import List, Type, Tuple
from ..model.entities import PlayRecord


def json2img(play_records: Tuple[List[Type[PlayRecord]], List[Type[PlayRecord]]]):
    # TODO: json to .jpg/.png/...
    pass


def json2csv(play_records: Tuple[List[Type[PlayRecord]], List[Type[PlayRecord]]]):
    # TODO: json to .csv file
    pass


def csv2json(username: str):
    # TODO: .csv file to json
    pass


def generate_empty_csv():
    # TODO: generate an empty .csv file
    pass
