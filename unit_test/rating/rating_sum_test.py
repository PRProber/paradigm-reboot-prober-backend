import unittest
import csv
from backend.prprober.util import single_rating


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_something():
        with open('rating/data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for record in reader:
                rt = single_rating(float(record['level']), int(record['score']))
                if rt != int(record['rating']):
                    print(f"diff level={record['level']}, score={record['score']}, gt_rating={record['rating']}, rating={rt}")


if __name__ == '__main__':
    unittest.main()
