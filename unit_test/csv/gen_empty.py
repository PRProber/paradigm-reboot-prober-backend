import json

import backend.util.b50.img as b50
from pathlib import Path

import backend.util.b50.csv


def test_something():
    with open('./data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    levels = sorted(data, key=lambda x: x['level'], reverse=True)
    backend.util.b50.csv.generate_empty_csv(Path(__file__).parent, levels)


if __name__ == '__main__':
    test_something()
