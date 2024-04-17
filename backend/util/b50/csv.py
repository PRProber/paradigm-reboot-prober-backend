import csv
from pathlib import Path
from typing import List

from pydantic import ValidationError

from ... import config
from ...model.schemas import PlayRecordInfo, PlayRecordCreate, SongLevelInfo


def json2csv(play_records: list[PlayRecordInfo]):
    # TODO: json to .csv file
    pass


def get_records_from_csv(filename: str = "default.csv") -> List[PlayRecordCreate]:
    records: List[PlayRecordCreate] = []
    with open(config.UPLOAD_CSV_PATH + filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                record = PlayRecordCreate(**row)
                records.append(record)
            except ValidationError as e:
                pass
    return records


def generate_empty_csv(file_path: Path, song_levels: List[SongLevelInfo]):
    with open(file_path / 'default.csv', 'w', encoding='utf-8-sig', newline="") as f:
        writer = csv.writer(f)
        headers = ['song_level_id', 'title', 'version', 'difficulty', 'level', 'score']
        writer.writerow(headers)
        for level in song_levels:
            writer.writerow([level['song_level_id'],
                             level['title'],
                             level['version'],
                             level['difficulty'],
                             level['level']])
        f.close()
