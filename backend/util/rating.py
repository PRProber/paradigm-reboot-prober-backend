bounds = [900000, 930000, 950000, 970000, 980000, 990000]
rewards = [3, 1, 1, 1, 1, 1]

EPS = 0.00002


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
        if score <= 1009000:
            rating = 10 * (level + 2 * (score - 1000000) / 30000)
        else:
            rating = 10 * level + 6 + 4 * (score - 1009000) / 1000
    else:
        for bound, reward in zip(bounds, rewards):
            rating += reward if score >= bound else 0
        rating += 10 * (level * ((score / 1000000) ** 1.5) - 0.9)

    rating = max(.0, rating)

    int_rating: int = int(rating * 100 + EPS)
    return int_rating
