import json
from operator import itemgetter

import backend.util.b50 as b50
from pathlib import Path


def test_something():
    with open('./data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    levels = sorted(data, key=itemgetter('level'), reverse=True)
    b50.generate_empty_csv(Path(__file__).parent, levels)


if __name__ == '__main__':
    test_something()
