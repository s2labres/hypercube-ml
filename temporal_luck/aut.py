import logging
from typing import Union
from datetime import date, datetime

import numpy as np
from android_malware_detectors.datasets_utils.dates import generate_dates_in_interval


logging.basicConfig(level=logging.WARNING)


def aut(results_by_date: dict[date, dict[str, float]], metric: str) -> float:
    """
    :param results_by_date: a dictionary containing performance metric per time unit.
            Example 1: {date(2021, 1, 1): {"f1": 0.97}, date(2021, 2, 1): {"f1": 0.87}}
            Example 2 {date(2021, 1, 1): {"f1": 0.97, "accuracy": 0.99},
                       date(2021, 2, 1): {"f1": 0.87, "accuracy": 0.99}}
    :param metric: metric to use. It must appear in the results_by_date inner dictionaries.
    """
    results_array = []

    for _date in sorted(results_by_date):
        score = results_by_date[_date][metric]
        results_array.append(score)

    results_array = np.asarray(results_array)
    return np.trapezoid(results_array) / (results_array.shape[0] - 1)


def average_aut(results_by_date: dict[date, dict[str, float]], metric: str, start_date: Union[date, datetime],
                end_date: Union[date, datetime], time_granularity="monthly", time_steps=12) -> tuple[float, float]:
    aut_list = []
    all_dates_in_interval = generate_dates_in_interval(start_date, end_date, time_granularity, time_steps)
    for date_index in range(len(all_dates_in_interval - 1)):
        window_start, window_end = all_dates_in_interval[date_index], all_dates_in_interval[date_index + 1]
        all_dates_in_window = [_date for _date in results_by_date if window_start <= _date <= window_end]
        results_in_window = {_date: results_by_date[_date] for _date in all_dates_in_window}
        aut_list.append(aut(results_in_window, metric))

    aut_list = np.asarray(aut_list)
    return np.mean(aut_list), np.std(aut_list)
