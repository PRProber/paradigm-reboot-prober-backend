import unittest
import os

import backend.util.ocr as ocr


class OCRSimpleTestCase(unittest.TestCase):
    song_titles: list[str] = ['桜花怨雷', 'CO5M1C R4ILR0AD', 'REDRAVE',
                              'キミとボクへの葬送歌', '今天不是明天 (feat. 兰音Reine)', 'クリムゾン帝王']
    difficulties: list[str] = ['DETECTED', 'INVADED', 'MASSIVE']
    score: dict[str, int] = {
        '桜花怨雷': 997307,
        '今天不是明天 (feat. 兰音Reine)': 1009576,
        'CO5M1C R4ILR0AD': 1007983,
        'REDRAVE': 1008528,
        'キミとボクへの葬送歌': 1005532,
        'クリムゾン帝王': 1005140
    }
    test_img_root: str = 'ocr/test_img/'

    def test_something(self):
        images = os.listdir(OCRSimpleTestCase.test_img_root)
        for img in images:
            result = ocr.extract_record_info(OCRSimpleTestCase.test_img_root + img,
                                             song_titles=OCRSimpleTestCase.song_titles,
                                             difficulties=OCRSimpleTestCase.difficulties)
            print(result)
            self.assertEqual(OCRSimpleTestCase.score[result['title'][0]], result['score'])


if __name__ == '__main__':
    unittest.main()
