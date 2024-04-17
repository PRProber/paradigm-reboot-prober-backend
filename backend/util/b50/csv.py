import csv
import io
from pathlib import Path
from typing import List

from pydantic import ValidationError

from backend import config as backend_config
from backend.model.schemas import PlayRecordInfo, PlayRecordCreate, SongLevelInfo, SongLevelCsv


def generate_csv(records: List[SongLevelCsv]):
    csv_bytes = io.StringIO()
    writer = csv.DictWriter(csv_bytes, fieldnames=['song_level_id', 'title', 'version', 'difficulty', 'level', 'score'])
    writer.writeheader()
    for level in records:
        writer.writerow(vars(level))
    return csv_bytes.getvalue()


def get_records_from_csv(filename: str = "default.csv") -> List[PlayRecordCreate]:
    records: List[PlayRecordCreate] = []
    with open(backend_config.UPLOAD_CSV_PATH + filename, 'r', encoding='utf-8-sig') as f:
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
        writer = csv.DictWriter(f, fieldnames=['song_level_id', 'title', 'version', 'difficulty', 'level', 'score'])
        writer.writeheader()
        for level in song_levels:
            writer.writerow(vars(SongLevelCsv(**level)))
        f.close()
