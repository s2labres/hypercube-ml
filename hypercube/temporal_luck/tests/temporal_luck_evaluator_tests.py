import os
import unittest
from datetime import date
from unittest import mock
from unittest.mock import call

from android_malware_detectors.detectors.base.base_detector import BaseDetector

from hypercube.temporal_luck.temporal_luck_evaluator import TemporalLuckEvaluator


class FakeHCC:
    def __init__(self, _):
        pass

    def train(self):
        pass

    def save(self):
        pass


class FakeLogger:
    def info(self):
        pass


class FakeClassifier1(BaseDetector):
    def _train_preprocessing(self, dataset_dict, labels_dict, *args, **kwargs):
        pass

    def _test_preprocessing(self, dataset_dict, *args, **kwargs):
        pass

    def _train_classifier(self, dataset, labels, *args, **kwargs):
        pass

    def _predict(self, dataset, *args, **kwargs):
        pass


class FakeClassifier2(BaseDetector):
    def _train_preprocessing(self, dataset_dict, labels_dict, *args, **kwargs):
        pass

    def _test_preprocessing(self, dataset_dict, *args, **kwargs):
        pass

    def _train_classifier(self, dataset, labels, *args, **kwargs):
        pass

    def _predict(self, dataset, *args, **kwargs):
        pass


class FakeClassifier3(BaseDetector):
    def _train_preprocessing(self, dataset_dict, labels_dict, *args, **kwargs):
        pass

    def _test_preprocessing(self, dataset_dict, *args, **kwargs):
        pass

    def _train_classifier(self, dataset, labels, *args, **kwargs):
        pass

    def _predict(self, dataset, *args, **kwargs):
        pass


class TemporalLuckEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classifiers_list = ["FakeClassifier1", "FakeClassifier2"]
        cls.dataset_names = ["fake_dataset_1", "fake_dataset_2"]
        cls.meta_files_paths_list = ["fake_dataset_1_meta", "fake_dataset_2_meta"]
        cls.dataset_paths_list = ["fake_dataset_1_classifier_1_feats", "fake_dataset_2_classifier_1_feats",
                                  "fake_dataset_1_classifier_2_feats", "fake_dataset_2_classifier_2_feats"]
        cls.vtts = [4, 15]
        cls.date_types = ["dex_date", "vtt_date"]
        cls.families = "fake_family_dict"

        cls.temporal_luck_evaluator = TemporalLuckEvaluator()
        for classifier, classifier_class in zip(cls.classifiers_list,
                                                [FakeClassifier1, FakeClassifier2, FakeClassifier3]):
            cls.temporal_luck_evaluator.register_classifier_class(classifier, classifier_class)

        for dataset_name in cls.dataset_names:
            cls.temporal_luck_evaluator.register_dataset(dataset_name)

        for dataset_name, dataset_meta_path in zip(cls.dataset_names, cls.meta_files_paths_list):
            cls.temporal_luck_evaluator.register_meta_path(dataset_name, dataset_meta_path)

        for dataset_name, vtt in zip(cls.dataset_names, cls.vtts):
            cls.temporal_luck_evaluator.register_vtt(dataset_name, vtt)

        for dataset_name, date_type in zip(cls.dataset_names, cls.date_types):
            cls.temporal_luck_evaluator.register_date_type(dataset_name, date_type)

        cls.temporal_luck_evaluator.register_dataset_for_classifier(
            cls.dataset_names[0], cls.classifiers_list[0], cls.dataset_paths_list[0]
        )
        cls.temporal_luck_evaluator.register_dataset_for_classifier(
            cls.dataset_names[1], cls.classifiers_list[0], cls.dataset_paths_list[1]
        )
        cls.temporal_luck_evaluator.register_dataset_for_classifier(
            cls.dataset_names[0], cls.classifiers_list[1], cls.dataset_paths_list[2]
        )
        cls.temporal_luck_evaluator.register_dataset_for_classifier(
            cls.dataset_names[1], cls.classifiers_list[1], cls.dataset_paths_list[3]
        )

    def test_train_all_classifiers(self):
        save_dir = "root_fake_save_dir"
        families = "fake_family_dict"
        dataset_min_date, dataset_max_date = date(2020, 1, 1), date(2023, 12, 31)
        training_window_length, test_window_length, time_granularity, time_granularity_value = 12, 12, "monthly", 1

        with (mock.patch.object(self.temporal_luck_evaluator, "train_classifier") as train_classifier_mock,
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.os.makedirs") as make_dirs_mock):
            self.temporal_luck_evaluator.train_all(dataset_min_date, dataset_max_date, training_window_length,
                                                   test_window_length, time_granularity, time_granularity_value,
                                                   save_dir, families, False)

        expected_train_classifier_calls = [
            call("FakeClassifier1", "fake_dataset_1", dataset_min_date, dataset_max_date, training_window_length,
                 test_window_length, time_granularity, time_granularity_value,
                 os.path.join(save_dir, "FakeClassifier1"), families, False),
            call("FakeClassifier1", "fake_dataset_2", dataset_min_date, dataset_max_date, training_window_length,
                 test_window_length, time_granularity, time_granularity_value,
                 os.path.join(save_dir, "FakeClassifier1"), families, False),
            call("FakeClassifier2", "fake_dataset_1", dataset_min_date, dataset_max_date, training_window_length,
                 test_window_length, time_granularity, time_granularity_value,
                 os.path.join(save_dir, "FakeClassifier2"), families, False),
            call("FakeClassifier2", "fake_dataset_2", dataset_min_date, dataset_max_date, training_window_length,
                 test_window_length, time_granularity, time_granularity_value,
                 os.path.join(save_dir, "FakeClassifier2"), families, False)
        ]

        train_classifier_mock.assert_has_calls(expected_train_classifier_calls)
        make_dirs_mock.assert_has_calls([call("root_fake_save_dir/FakeClassifier1", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier1", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier2", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier2", exist_ok=True),],)
        self.assertEqual(train_classifier_mock.call_count, 4)

    def test_train_classifier(self):
        dataset_min_date, dataset_max_date = date(2020, 1, 1), date(2023, 12, 31)
        training_window_length, test_window_length, time_granularity, time_granularity_value = 12, 12, "monthly", 1
        root_model_save_path = "fake_save_dir"
        families = "fake_family_dict"

        fake_labels = [{"fake_1": 1, "fake_2": 0}, {"fake_3": 2, "fake_4": 1}]
        fake_shas = [["fake_1", "fake_2"], ["fake_3", "fake_4"]]

        with (mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.get_labels_from_meta",
                         side_effect=fake_labels),
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.get_shas_in_time_frame",
                         side_effect=fake_shas),
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.os.makedirs") as make_dirs_mock,
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.os.listdir",
                         side_effect=[[], [], [1]]) as make_dirs_mock,
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.LoggerManager.get_logger",
                         return_value=FakeLogger()),
              mock.patch.object(FakeLogger, "info") as info_mock):
            with (mock.patch.object(FakeClassifier1, "train") as train_method_mock,
                  mock.patch.object(FakeClassifier1, "save") as save_method_mock):
                self.temporal_luck_evaluator.train_classifier(
                    self.classifiers_list[0], self.dataset_names[0], dataset_min_date, dataset_max_date,
                    training_window_length, test_window_length, time_granularity, time_granularity_value,
                    root_model_save_path, families, False
                )

        expected_train_method_calls = [
            call(self.dataset_paths_list[0], fake_labels[0], samples_hashes_list=fake_shas[0],
                 family_dict_path=families, compact_data=False),
            call(self.dataset_paths_list[0], fake_labels[1], samples_hashes_list=fake_shas[1],
                 family_dict_path=families, compact_data=False)
        ]
        expected_makedirs_calls = [call(f"fake_save_dir/{self.dataset_names[0]}/2020-01-01-2020-12-31"),
                                   call(f"fake_save_dir/{self.dataset_names[0]}/2021-01-01-2021-12-31")]

        train_method_mock.assert_has_calls(expected_train_method_calls, any_order=False)
        make_dirs_mock.assert_has_calls(expected_makedirs_calls, any_order=False)
        info_mock.assert_called_once_with("already trained --- skipping")
        self.assertEqual(save_method_mock.call_count, 2)

    def test_evaluate_all(self):
        classifiers_dir_path = "fake_classifiers_dir"
        save_dir = "root_fake_save_dir"
        dataset_min_date, dataset_max_date = date(2020, 1, 1), date(2023, 12, 31)
        training_window_length, test_window_length, time_granularity, time_granularity_value = 12, 12, "monthly", 1

        with (mock.patch.object(self.temporal_luck_evaluator, "evaluate_classifier",
                                side_effect=[{"a": 1}, {"b": 2}, {"c": 3}, {"d": 4}]) as evaluate_classifier_mock,
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.os.makedirs") as make_dirs_mock,
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.average_aut",
                         side_effect=[(0.5, 0.01), (0.16, 0.03), (0.8, 0.02), (0.0, 0.01)]) as average_aut_mock,
              mock.patch("hypercube.temporal_luck.temporal_luck_evaluator.print") as print_mock):
            self.temporal_luck_evaluator.evaluate_all(
                classifiers_dir_path, dataset_min_date, dataset_max_date, save_dir,
                time_granularity, time_granularity_value, training_window_length, test_window_length
            )

        expected_evaluate_classifier_calls = [
            call("FakeClassifier1", "fake_classifiers_dir", "fake_dataset_1", dataset_min_date, dataset_max_date,
                 time_granularity, time_granularity_value, training_window_length, test_window_length,
                 os.path.join(save_dir, "FakeClassifier1"),),
            call("FakeClassifier1", "fake_classifiers_dir", "fake_dataset_2", dataset_min_date, dataset_max_date,
                 time_granularity, time_granularity_value, training_window_length, test_window_length,
                 os.path.join(save_dir, "FakeClassifier1"),),
            call("FakeClassifier2", "fake_classifiers_dir", "fake_dataset_1", dataset_min_date, dataset_max_date,
                 time_granularity, time_granularity_value, training_window_length, test_window_length,
                 os.path.join(save_dir, "FakeClassifier2"),),
            call("FakeClassifier2", "fake_classifiers_dir", "fake_dataset_2", dataset_min_date, dataset_max_date,
                 time_granularity, time_granularity_value, training_window_length, test_window_length,
                 os.path.join(save_dir, "FakeClassifier2"),)
        ]

        evaluate_classifier_mock.assert_has_calls(expected_evaluate_classifier_calls, any_order=True)
        make_dirs_mock.assert_has_calls([call("root_fake_save_dir/FakeClassifier1", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier1", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier2", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier2", exist_ok=True), ],
                                        any_order=True)
        average_aut_mock.assert_has_calls(
            [call({"a": 1}, "f1", dataset_min_date, dataset_max_date, time_granularity, time_granularity_value),
             call({"b": 2}, "f1", dataset_min_date, dataset_max_date, time_granularity, time_granularity_value),
             call({"c": 3}, "f1", dataset_min_date, dataset_max_date, time_granularity, time_granularity_value),
             call({"d": 4}, "f1", dataset_min_date, dataset_max_date, time_granularity, time_granularity_value)],
            any_order=True
        )
        print_mock.assert_has_calls([
            call(f"Classifier: FakeClassifier1 - Dataset: fake_dataset_1 - [{dataset_min_date}-{dataset_max_date}]"
                 f"A-AUT 0.5 (0.01)"),
            call(f"Classifier: FakeClassifier1 - Dataset: fake_dataset_2 - [{dataset_min_date}-{dataset_max_date}]"
                 f"A-AUT 0.16 (0.03)"),
            call(f"Classifier: FakeClassifier2 - Dataset: fake_dataset_1 - [{dataset_min_date}-{dataset_max_date}]"
                 f"A-AUT 0.8 (0.02)"),
            call(f"Classifier: FakeClassifier2 - Dataset: fake_dataset_2 - [{dataset_min_date}-{dataset_max_date}]"
                 f"A-AUT 0.0 (0.01)"),
        ])
        self.assertEqual(evaluate_classifier_mock.call_count, 4)
