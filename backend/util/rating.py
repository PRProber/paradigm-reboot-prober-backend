bounds = [900000, 930000, 950000, 970000, 980000, 990000]
rewards = [3, 1, 1, 1, 1, 1]


def single_rating(level: float, score: int) -> float:
    """
    Calculate the rating of a single chart.
    :param level: the float level of the chart. e.g. 16.4
    :param score: the score of a play record. e.g. 1008900
    :return: the (avg) rating.
    """
    # Reference: https://www.bilibili.com/read/cv29433852
    global bounds, rewards
    rating: float = 0

    score = min(score, 1010000)

    if score >= 1000000:
        rating = level + 2 * (score - 1000000) / 30000
    else:
        for bound, reward in zip(bounds, rewards):
            rating += reward if score >= bound else 0
        rating += level * ((score / 1000000) ** 1.5) - 0.9

    rating = max(.0, rating)

    int_rating: int = int(rating * 1000)
    return int_rating
