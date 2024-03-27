def single_rating(level: float, acc: float) -> float:
    """
    Calculate the rating of a single chart.
    :param level: the float level of the chart. e.g. 16.4
    :param acc: the accuracy (percentage) of a play record. e.g. 100.89
    :return: the (avg) rating.
    """
    # TODO: Apply the formula.
    # Reference: https://www.bilibili.com/read/cv29433852
    rating: float

    bounds = [0.9, 0.93, 0.95, 0.97, 0.98, 0.99, 1]
    rewards = [0.06, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02]

    reward_rating: float = 0
    for i, bound in enumerate(bounds):
        if acc >= bound:
            reward_rating += rewards[i]

    if acc > 1:
        rating = 0.2 * (level + 200.0 * (acc - 1.0) / 3.0)
    else:
        rating = 0.2 * (level * (acc ** 1.5) - 0.9) + reward_rating

    int_rating: int = int(rating * 10000)
    if int_rating % 2 != 0:
        int_rating -= 1

    rating = int_rating / 10000

    return rating
