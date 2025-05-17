import re
import logging

from PIL import Image
from thefuzz import fuzz
from paddleocr import PaddleOCR, draw_ocr


logging.disable(logging.DEBUG)
ch_ocr = PaddleOCR(use_angle_cls=True, lang="ch")
jp_ocr = PaddleOCR(use_angle_cls=True, lang="japan")


def _ocr_result_display(result, img_path: str, output_name):
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    texts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, texts, scores)
    im_show = Image.fromarray(im_show)
    im_show.save(output_name)


def _concentrate_string(result, threshold=0.8):
    result_str = ''
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            text, score = line[1]
            if score > threshold:
                result_str += text + ' '
    return result_str


def extract_record_info(img_path: str,
                        song_titles: list[str],
                        difficulties: list[str],
                        threshold: int = 75) -> dict:
    """
    Given a screenshot of a record, list of available song titles and difficulties, extract the corresponding record
    information. The result dictionary is like ``{"title": (str, dist), "difficulty": (str, dist), "score": int}``
    :param threshold: Levenshtein Distance threshold
    :param difficulties: list of difficulties
    :param song_titles: list of available song titles
    :param img_path: the path of screenshot
    :return: A dictionary contains record information. Keys: ``'title'``, ``'difficulty'``, ``'score'``
    """

    ch, jp = ch_ocr.ocr(img_path, cls=True), jp_ocr.ocr(img_path, cls=True)
    ch_str, jp_str = _concentrate_string(ch), _concentrate_string(jp)
    result = {"title": ('', threshold), "difficulty": ('', threshold), "score": int}

    for title in song_titles:
        _, title_score = result['title']
        ch_score = fuzz.partial_token_sort_ratio(title, ch_str)
        jp_score = fuzz.partial_token_sort_ratio(title, jp_str)
        if max(ch_score, jp_score) > threshold and max(ch_score, jp_score) > title_score:
            result['title'] = (title, max(ch_score, jp_score))

    for difficulty in difficulties:
        _, diff_score = result['difficulty']
        score = fuzz.partial_token_sort_ratio(difficulty, ch_str)
        if score > threshold and score > diff_score:
            result['difficulty'] = (difficulty, score)

    # TODO: Strengthen robustness
    score = re.findall('[0-9]{7}', ch_str)[0]
    result['score'] = int(score)

    return result
