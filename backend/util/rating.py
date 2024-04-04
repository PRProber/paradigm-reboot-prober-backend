bounds = [900000, 930000, 950000, 970000, 980000, 990000]
rewards = [0.06, 0.02, 0.02, 0.02, 0.02, 0.02]


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

    if score >= 1000000:
        rating = 0.2 * (level + 2 * (score - 1000000) / 30000)
    else:
        for bound, reward in zip(bounds, rewards):
            rating += reward if score >= bound else 0
        rating += 0.2 * (level * ((score / 1000000) ** 1.5) - 0.9)

    int_rating: int = int(rating * 10000)
    if int_rating % 2 != 0:
        int_rating -= 1

    rating = int_rating / 10000

    return rating
