import unittest
from datetime import date

from temporal_luck.temporal_windows import training_slice_iterator, test_slice_iterator


class TemporalWindowsTests(unittest.TestCase):
    def test_training_slice_iterator(self):
        dataset_min_date, dataset_max_date = date(2020, 1, 1), date(2023, 12, 31)
        training_segment_size_1, test_segment_size_1 = 12, 12
        training_segment_size_2, test_segment_size_2 = 12, 15
        training_segment_size_3, test_segment_size_3 = 12, 6
        training_segment_size_4, test_segment_size_4 = 12, 5

        slices_1, slices_2, slices_3, slices_4 = [], [], [], []

        for date_pair in training_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_1,
                                                 test_segment_size_1, "monthly", 1):
            slices_1.append(date_pair)
        for date_pair in training_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_2,
                                                 test_segment_size_2, "monthly", 1):
            slices_2.append(date_pair)
        for date_pair in training_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_3,
                                                 test_segment_size_3, "monthly", 1):
            slices_3.append(date_pair)
        for date_pair in training_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_4,
                                                 test_segment_size_4, "monthly", 1):
            slices_4.append(date_pair)

        self.assertEqual(slices_1, [(date(2020, 1, 1), date(2020, 12, 31)),
                                    (date(2021, 1, 1), date(2021, 12, 31)),
                                    (date(2022, 1, 1), date(2022, 12, 31))])
        self.assertEqual(slices_2, [(date(2020, 1, 1), date(2020, 12, 31)),
                                    (date(2021, 1, 1), date(2021, 12, 31))])
        self.assertEqual(slices_3, [(date(2020, 1, 1), date(2020, 12, 31)),
                                    (date(2020, 7, 1), date(2021, 6, 30)),
                                    (date(2021, 1, 1), date(2021, 12, 31)),
                                    (date(2021, 7, 1), date(2022, 6, 30)),
                                    (date(2022, 1, 1), date(2022, 12, 31)),
                                    (date(2022, 7, 1), date(2023, 6, 30)),])
        self.assertEqual(slices_4, [(date(2020, 1, 1), date(2020, 12, 31)),
                                    (date(2020, 6, 1), date(2021, 5, 31)),
                                    (date(2020, 11, 1), date(2021, 10, 31)),
                                    (date(2021, 4, 1), date(2022, 3, 31)),
                                    (date(2021, 9, 1), date(2022, 8, 31)),
                                    (date(2022, 2, 1), date(2023, 1, 31)),
                                    (date(2022, 7, 1), date(2023, 6, 30)),])

    def test_test_slice_iterator(self):
        dataset_min_date, dataset_max_date = date(2020, 1, 1), date(2023, 12, 31)
        training_segment_size_1, test_segment_size_1 = 12, 12
        training_segment_size_2, test_segment_size_2 = 12, 15
        training_segment_size_3, test_segment_size_3 = 12, 6
        training_segment_size_4, test_segment_size_4 = 12, 5

        slices_1, slices_2, slices_3, slices_4 = [], [], [], []

        for date_pair in test_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_1,
                                             test_segment_size_1, "monthly", 1):
            slices_1.append(date_pair)
        for date_pair in test_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_2,
                                             test_segment_size_2, "monthly", 1):
            slices_2.append(date_pair)
        for date_pair in test_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_3,
                                             test_segment_size_3, "monthly", 1):
            slices_3.append(date_pair)
        for date_pair in test_slice_iterator(dataset_min_date, dataset_max_date, training_segment_size_4,
                                             test_segment_size_4, "monthly", 1):
            slices_4.append(date_pair)

        self.assertEqual(slices_1, [(date(2021, 1, 1), date(2021, 12, 31)),
                                    (date(2022, 1, 1), date(2022, 12, 31)),
                                    (date(2023, 1, 1), date(2023, 12, 31))])
        self.assertEqual(slices_2, [(date(2021, 1, 1), date(2022, 3, 31)),
                                    (date(2022, 1, 1), date(2023, 3, 31)),])
        self.assertEqual(slices_3, [(date(2021, 1, 1), date(2021, 6, 30)),
                                    (date(2021, 7, 1), date(2021, 12, 31)),
                                    (date(2022, 1, 1), date(2022, 6, 30)),
                                    (date(2022, 7, 1), date(2022, 12, 31)),
                                    (date(2023, 1, 1), date(2023, 6, 30)),
                                    (date(2023, 7, 1), date(2023, 12, 31))])
        self.assertEqual(slices_4, [(date(2021, 1, 1), date(2021, 5, 31)),
                                    (date(2021, 6, 1), date(2021, 10, 31)),
                                    (date(2021, 11, 1), date(2022, 3, 31)),
                                    (date(2022, 4, 1), date(2022, 8, 31)),
                                    (date(2022, 9, 1), date(2023, 1, 31)),
                                    (date(2023, 2, 1), date(2023, 6, 30)),
                                    (date(2023, 7, 1), date(2023, 11, 30)),])
