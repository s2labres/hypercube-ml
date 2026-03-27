import numpy as np
from scipy.stats import norm


def compute_margin_of_error_sampling(population_size: int, number_of_classes: int, margin_of_error: float = 0.015,
                                     confidence_level: float = 0.99):
    """
    Calculate the minimum sample size needed to represent the population of number_of_classes classes
    with a margin error and a probability higher than a confidence_level.

    Args:
    :param population_size: The size of the population from which to subsample.
    :param number_of_classes: Total number of classes in the population.
    :param margin_of_error: Margin of error.
    :param confidence_level: The confidence level (between 0 and 1).

    Returns:
    int: Minimum sample size required.
    """

    if population_size == 0:
        return 0

    numerator = 4 * (population_size - 1) * margin_of_error ** 2
    if number_of_classes == 1:
        denominator = _z_score(number_of_classes)
    else:
        denominator = _z_score((1 - (1 - confidence_level) / (number_of_classes - 1))) ** 2
    sample_size = population_size * (numerator / denominator + 1) ** -1

    return int(np.ceil(sample_size))


def _z_score(x):
    score = norm.ppf(1 - (1 - x) / 2)
    return score
