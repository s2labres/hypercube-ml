import math
import unittest
from datetime import date

from hypercube.temporal_luck.aut import aut, average_aut


class AUTTests(unittest.TestCase):
    def test_aut(self):
        results_dict = {
            date(2021, 1, 1): {"f1": 0.7, "accuracy": 0.8}, date(2021, 2, 1): {"f1": 0.6, "accuracy": 0.7},
            date(2021, 3, 1): {"f1": 0.5, "accuracy": 0.6}, date(2021, 4, 1): {"f1": 0.4, "accuracy": 0.5},
            date(2021, 5, 1): {"f1": 0.3, "accuracy": 0.4}, date(2021, 6, 1): {"f1": 0.2, "accuracy": 0.3},
        }
        self.assertEqual(float(f"{aut(results_dict, metric="f1"): .2f}"), 0.45)
        self.assertEqual(float(f"{aut(results_dict, metric="accuracy"): .2f}"), 0.55)

    def test_average_aut(self):
        results_dict = {
            date(2021, 1, 1): {"f1": 0.7, "accuracy": 0.8}, date(2021, 2, 1): {"f1": 0.6, "accuracy": 0.7},
            date(2021, 3, 1): {"f1": 0.5, "accuracy": 0.6}, date(2021, 4, 1): {"f1": 0.4, "accuracy": 0.5},
            date(2021, 5, 1): {"f1": 0.3, "accuracy": 0.4}, date(2021, 6, 1): {"f1": 0.2, "accuracy": 0.3},
            date(2021, 7, 1): {"f1": 0.4, "accuracy": 0.4}, date(2021, 8, 1): {"f1": 0.3, "accuracy": 0.3},
            date(2021, 9, 1): {"f1": 0.3, "accuracy": 0.4}, date(2021, 10, 1): {"f1": 0.2, "accuracy": 0.3},
            date(2021, 11, 1): {"f1": 0.5, "accuracy": 0.4}, date(2021, 12, 1): {"f1": 0.2, "accuracy": 0.3},
        }
        start_date = date(2021, 1, 1)
        end_date = date(2021, 12, 31)

        avg_aut_f1_1, std_aut_f1_1 = average_aut(results_dict, metric="f1", start_date=start_date,
                                                 end_date=end_date, time_steps=3)
        avg_aut_f1_2, std_aut_f1_2 = average_aut(results_dict, metric="f1", start_date=start_date,
                                                 end_date=end_date, time_steps=6)
        avg_aut_accuracy_1, std_aut_accuracy_1 = average_aut(results_dict, metric="accuracy", start_date=start_date,
                                                             end_date=end_date, time_steps=6)

        self.assertTrue(math.isclose(float(f"{avg_aut_f1_1: .2f}"), 0.38, rel_tol=0.1))
        self.assertTrue(math.isclose(float(f"{std_aut_f1_1: .2f}"), 0.13, rel_tol=0.1))
        self.assertTrue(math.isclose(float(f"{avg_aut_f1_2: .2f}"), 0.38, rel_tol=0.1))
        self.assertTrue(math.isclose(float(f"{std_aut_f1_2: .2f}"), 0.07, rel_tol=0.1))
        self.assertTrue(math.isclose(float(f"{avg_aut_accuracy_1: .2f}"), 0.45, rel_tol=0.1))
        self.assertTrue(math.isclose(float(f"{std_aut_accuracy_1: .2f}"), 0.1, rel_tol=0.1))


if __name__ == '__main__':
    unittest.main()
