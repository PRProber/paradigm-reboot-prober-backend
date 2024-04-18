import unittest
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        with open('rating/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        b35, b15 = 0, 0
        for record in data['records']:
            if record['song_level']['b15']:
                b15 += record['rating']
            else:
                b35 += record['rating']
        print((b35 + b15)/5000, (b35)/3500, (b15)/1500)
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
