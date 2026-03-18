import os
import unittest
from datetime import date
from unittest import mock
from unittest.mock import call

from temporal_luck.trainer import train_classifier, train_all_classifiers


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


class TrainerTests(unittest.TestCase):
    def test_train_all_classifiers(self):
        classifiers_list = ["FakeClassifier1", "FakeClassifier2"]
        dataset_names = ["FakeDataset1", "FakeDataset2"]
        dataset_paths_list = ["fake_dataset_1_classifier_1_feats", "fake_dataset_2_classifier_1_feats",
                              "fake_dataset_1_classifier_2_feats", "fake_dataset_2_classifier_2_feats"]
        meta_files_paths_list = ["fake_dataset_1_meta", "fake_dataset_2_meta"]
        vtts = [4, 15]
        dataset_min_date, dataset_max_date = date(2020, 1, 1), date(2023, 12, 31)
        training_window_length, test_window_length, time_granularity, time_granularity_value = 12, 12, "monthly", 1
        date_types = ["dex_date", "vtt_date"]
        save_dir = "root_fake_save_dir"
        families = "fake_family_dict"

        with (mock.patch("temporal_luck.trainer.train_classifier") as train_classifier_mock,
              mock.patch("temporal_luck.trainer.os.makedirs") as make_dirs_mock):
            train_all_classifiers(classifiers_list, dataset_names, dataset_paths_list, meta_files_paths_list, vtts,
                                  dataset_min_date, dataset_max_date, training_window_length, test_window_length,
                                  time_granularity, time_granularity_value, date_types, save_dir, families, False)

        expected_train_classifier_calls = [
            call("FakeClassifier1", "fake_dataset_1_classifier_1_feats", "fake_dataset_1_meta", 4,
                 dataset_min_date, dataset_max_date, training_window_length, test_window_length, time_granularity,
                 time_granularity_value, "dex_date", os.path.join(save_dir, "FakeClassifier1", "FakeDataset1"),
                 families, False),
            call("FakeClassifier1", "fake_dataset_2_classifier_1_feats", "fake_dataset_2_meta", 15,
                 dataset_min_date, dataset_max_date, training_window_length, test_window_length, time_granularity,
                 time_granularity_value, "vtt_date", os.path.join(save_dir, "FakeClassifier1", "FakeDataset2"),
                 families, False),
            call("FakeClassifier2", "fake_dataset_1_classifier_2_feats", "fake_dataset_1_meta", 4,
                 dataset_min_date, dataset_max_date, training_window_length, test_window_length, time_granularity,
                 time_granularity_value, "dex_date", os.path.join(save_dir, "FakeClassifier2", "FakeDataset1"),
                 families, False),
            call("FakeClassifier2", "fake_dataset_2_classifier_2_feats", "fake_dataset_2_meta", 15,
                 dataset_min_date, dataset_max_date, training_window_length, test_window_length, time_granularity,
                 time_granularity_value, "vtt_date", os.path.join(save_dir, "FakeClassifier2", "FakeDataset2"),
                 families, False)
        ]

        train_classifier_mock.assert_has_calls(expected_train_classifier_calls)
        make_dirs_mock.assert_has_calls([call("root_fake_save_dir/FakeClassifier1/FakeDataset1", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier1/FakeDataset2", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier2/FakeDataset1", exist_ok=True),
                                         call("root_fake_save_dir/FakeClassifier2/FakeDataset2", exist_ok=True),])
        self.assertEqual(train_classifier_mock.call_count, 4)

    def test_train_classifier(self):
        classifier, dataset_path, meta_file_path, vtt = "HCC", "fake_dataset_path", "fake_meta_path", 15
        dataset_min_date, dataset_max_date = date(2020, 1, 1), date(2023, 12, 31)
        training_window_length, test_window_length, time_granularity, time_granularity_value = 12, 12, "monthly", 1
        root_model_save_path = "fake_save_dir"
        families = "fake_family_dict"

        fake_labels = [{"fake_1": 1, "fake_2": 0}, {"fake_3": 2, "fake_4": 1}]
        fake_shas = [["fake_1", "fake_2"], ["fake_3", "fake_4"]]

        with (mock.patch("temporal_luck.trainer.get_labels_from_meta", side_effect=fake_labels),
              mock.patch("temporal_luck.trainer.get_shas_in_time_frame", side_effect=fake_shas),
              mock.patch("temporal_luck.trainer.get_model_class", return_value=FakeHCC),
              mock.patch("temporal_luck.trainer.os.makedirs") as make_dirs_mock,
              mock.patch("temporal_luck.trainer.os.listdir", side_effect=[[], [], [1]]) as make_dirs_mock,
              mock.patch("temporal_luck.trainer.LoggerManager.get_logger", return_value=FakeLogger()),
              mock.patch.object(FakeLogger, "info") as info_mock):
            with (mock.patch.object(FakeHCC, "train") as train_method_mock,
                  mock.patch.object(FakeHCC, "save") as save_method_mock):
                train_classifier(classifier, dataset_path, meta_file_path, vtt, dataset_min_date, dataset_max_date,
                                 training_window_length, test_window_length, time_granularity, time_granularity_value,
                                 "dex_date", root_model_save_path, families, False)

        expected_train_method_calls = [
            call(dataset_path, fake_labels[0], samples_hashes_list=fake_shas[0],
                 family_dict_path=families, compact_data=False),
            call(dataset_path, fake_labels[1], samples_hashes_list=fake_shas[1],
                 family_dict_path=families, compact_data=False)
        ]
        expected_makedirs_calls = [call("fake_save_dir/2020"), call("fake_save_dir/2021")]

        train_method_mock.assert_has_calls(expected_train_method_calls, any_order=False)
        make_dirs_mock.assert_has_calls(expected_makedirs_calls, any_order=False)
        info_mock.assert_called_once_with("already trained --- skipping")
        self.assertEqual(save_method_mock.call_count, 2)
