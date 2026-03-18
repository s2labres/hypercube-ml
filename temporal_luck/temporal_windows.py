import calendar
import datetime

import math

from android_malware_detectors.datasets_utils.dates import generate_dates_in_interval


def training_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size, test_segment_size,
                            time_granularity, time_granularity_value):
    all_dates = generate_dates_in_interval(dataset_min_date, dataset_max_date, time_granularity, time_granularity_value)
    if test_segment_size >= training_segment_size:
        for index in range(math.floor((len(all_dates) - test_segment_size) / training_segment_size)):
            start_date = all_dates[index * training_segment_size]
            end_date = all_dates[(index + 1) * training_segment_size - 1]
            end_date = datetime.date(year=end_date.year, month=end_date.month,
                                     day=calendar.monthrange(end_date.year, end_date.month)[1])
            yield start_date, end_date
    else:
        for index in range(math.floor((len(all_dates) - training_segment_size) / test_segment_size)):
            start_date = all_dates[index * test_segment_size]
            end_date = all_dates[index * test_segment_size + training_segment_size - 1]
            end_date = datetime.date(year=end_date.year, month=end_date.month,
                                     day=calendar.monthrange(end_date.year, end_date.month)[1])
            yield start_date, end_date


def test_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size, test_segment_size,
                        time_granularity, time_granularity_value):
    all_dates = generate_dates_in_interval(dataset_min_date, dataset_max_date, time_granularity, time_granularity_value)
    if test_segment_size >= training_segment_size:
        for index in range(math.floor((len(all_dates) - test_segment_size) / training_segment_size)):
            start_date = all_dates[(index + 1) * training_segment_size]
            end_date = all_dates[(index + 1) * training_segment_size + test_segment_size - 1]
            end_date = datetime.date(year=end_date.year, month=end_date.month,
                                     day=calendar.monthrange(end_date.year, end_date.month)[1])
            yield start_date, end_date
    else:
        for index in range(math.floor((len(all_dates) - training_segment_size) / test_segment_size)):
            start_date = all_dates[training_segment_size + index * test_segment_size]
            end_date = all_dates[training_segment_size + (index + 1) * test_segment_size - 1]
            end_date = datetime.date(year=end_date.year, month=end_date.month,
                                     day=calendar.monthrange(end_date.year, end_date.month)[1])
            yield start_date, end_date
