import unittest
import json

from backend.model.schemas import PlayRecordInfo
import backend.util.b50.img as b50


class MyTestCase(unittest.TestCase):
    def test_something(self):
        with open('b50image/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        records = [PlayRecordInfo.model_validate(record) for record in data]
        b50.generate_b50_img(records, None)
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
