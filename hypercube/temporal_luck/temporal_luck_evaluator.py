import os
from collections import defaultdict

from android_malware_detectors.datasets_utils import get_labels_from_meta, get_shas_in_time_frame, \
    divide_samples_by_date
from android_malware_detectors.detectors.base.base_detector import BaseDetector
from android_malware_detectors.utils import LoggerManager, dump_pickle, load_pickle

from hypercube.temporal_luck.aut import average_aut
from hypercube.temporal_luck.temporal_windows import training_slice_iterator, test_slice_iterator
from hypercube.temporal_luck.utils import make_file_path


class TemporalLuckEvaluator:
    def __init__(self):
        self.classifiers = set()
        self.classifiers_objects = {}
        self.classifiers_classes = {}
        self.datasets = set()
        self.datasets_meta_path = {}
        self.datasets_vtt = {}
        self.datasets_date_type = {}
        self.classifier_to_dataset = defaultdict(dict)

    def register_dataset(self, dataset_name: str):
        """
        :param dataset_name: the name of the dataset.

        Register a dataset name.
        """
        self.datasets.add(dataset_name)

    def register_meta_path(self, dataset_name: str, meta_path: str):
        """
        :param dataset_name: the name of the dataset.
        :param meta_path: the path of the meta file for dataset_name.

        Register the meta path to be used for dataset_name.
        """
        if dataset_name not in self.datasets:
            raise KeyError(f"Dataset {dataset_name} not registered. "
                           f"You need to call register_dataset){dataset_name} first")
        self.datasets_meta_path[dataset_name] = meta_path

    def register_vtt(self, dataset_name: str, vtt: int):
        """
        :param dataset_name: the name of the dataset.
        :param vtt: the vtt for dataset_name.

        Register the VTT value to be used for dataset_name
        """
        if dataset_name not in self.datasets:
            raise KeyError(f"Dataset {dataset_name} not registered. "
                           f"You need to call register_dataset){dataset_name} first")
        self.datasets_vtt[dataset_name] = vtt

    def register_date_type(self, dataset_name: str, date_type: str):
        """
        :param dataset_name: the name of the dataset.
        :param date_type: the key in the meta_file for accessing samples' timestamps.

        Register the meta path to be used for dataset_name
        """
        if dataset_name not in self.datasets:
            raise KeyError(f"Dataset {dataset_name} not registered. "
                           f"You need to call register_dataset){dataset_name} first")
        self.datasets_date_type[dataset_name] = date_type

    def register_classifier_object(self, classifier_name: str, classifier_object: BaseDetector):
        """
        :param classifier_name: the name of the classifier.
        :param classifier_object: the classifier object, it needs to extend BaseDetector or expose a similar interface.

        Register a classifier to be used in the evaluation
        """
        if not hasattr(classifier_object, "train"):
            raise NotImplementedError(f"Classifier {classifier_name} doesn't have a train method")
        if not hasattr(classifier_object, "evaluate_time_aware"):
            raise NotImplementedError(f"Classifier {classifier_name} doesn't have a evaluate_time_aware method")
        self.classifiers.add(classifier_name)
        self.classifiers_objects[classifier_name] = classifier_object

    def register_classifier_class(self, classifier_name: str, classifier_class):
        """
        :param classifier_name: the name of the classifier
        :param classifier_class: the classifier class, it needs to extend BaseDetector or expose a similar interface

        Register a classifier to be used in the evaluation
        """
        if not hasattr(classifier_class, "train"):
            raise NotImplementedError(f"Classifier {classifier_name} doesn't have a train method")
        if not hasattr(classifier_class, "evaluate_time_aware"):
            raise NotImplementedError(f"Classifier {classifier_name} doesn't have a evaluate_time_aware method")
        self.classifiers.add(classifier_name)
        self.classifiers_classes[classifier_name] = classifier_class

    def register_dataset_for_classifier(self, dataset_name: str, classifier_name: str, dataset_path: str):
        """
        :param dataset_name: the name of the dataset
        :param classifier_name: the name of the classifier
        :param dataset_path: the path of the dataset containing the features required by classifier_name
        """
        if dataset_name not in self.datasets:
            raise KeyError(f"Dataset {dataset_name} not registered. "
                           f"You need to call register_dataset){dataset_name} first")
        if dataset_name not in self.datasets:
            raise KeyError(f"Dataset {dataset_name} not registered. "
                           f"You need to call register_dataset){dataset_name} first")
        self.classifier_to_dataset[classifier_name][dataset_name] = dataset_path

    def train_all(self, dataset_min_date, dataset_max_date, training_window_length, test_window_length,
                  time_granularity, time_granularity_value, save_dir, families=None, compact_data=False):
        """
        Trains all registered classifiers across all registered datasets in a time window rolling manner.
        Make sure to register one dataset path for each classifier/dataset pair.

        :param dataset_min_date: earliest date in the dataset you want to perform a temporal luck evaluation over
        :param dataset_max_date: latest date in the dataset you want to perform a temporal luck evaluation over
                                    (includes latest test date available).
        :param training_window_length: how many years/months/days in each training splits in the evaluation
        :param test_window_length: how many years/months/days in each testing splits in the evaluation
        :param time_granularity: can be set to "monthly" "yearly" or "daily". Specifies the time granularity in the
                                    evaluation.
        :param time_granularity_value: how many days/months/years in each time slot.
        :param save_dir: path to directory where to save the trained models. It will create a structure like:
                            save_dir/ClassifierName/DatasetName/Date1...DateK
        :param families: path to a JSON with family name for each malware sample. Used only for some classifiers
                            such as HCC.
        :param compact_data: whether the data is provided in a compact/sparse way. Currently used for MalScan.
        """
        for classifier_name in sorted(self.classifiers):
            for dataset_name in sorted(self.classifier_to_dataset[classifier_name]):
                model_save_dir = os.path.join(save_dir, classifier_name)
                os.makedirs(model_save_dir, exist_ok=True)
                self.train_classifier(classifier_name, dataset_name, dataset_min_date, dataset_max_date,
                                      training_window_length, test_window_length, time_granularity,
                                      time_granularity_value, model_save_dir, families, compact_data)
        return save_dir

    def train_classifier(self, classifier_name, dataset_name, dataset_min_date, dataset_max_date,
                         training_window_length, test_window_length, time_granularity, time_granularity_value,
                         root_model_save_path, families=None, compact_data=False):
        """
        Trains an individual classifier across all registered datasets in a time window rolling manner.

        :param classifier_name: the name of the classifier. It must be registered.
        :param dataset_name: the name of the dataset. It must be registered.
        :param dataset_min_date: earliest date in the dataset you want to perform a temporal luck evaluation over
        :param dataset_max_date: latest date in the dataset you want to perform a temporal luck evaluation over
                                    (includes latest test date available).
        :param training_window_length: how many years/months/days in each training splits in the evaluation
        :param test_window_length: how many years/months/days in each testing splits in the evaluation
        :param time_granularity: can be set to "monthly" "yearly" or "daily".
        :param time_granularity_value: how many days/months/years in each time slot.
        :param root_model_save_path: path to directory where to save the trained models. It will create a structure
                                            root_model_save_path/DatasetName/Date1...DateK.
        :param families:  path to a JSON with family name for each malware sample. Used only for some classifiers
                            such as HCC.
        :param compact_data: whether the data is provided in a compact/sparse way. Currently used for MalScan.

        """
        for start_date, end_date in training_slice_iterator(dataset_min_date, dataset_max_date, training_window_length,
                                                            test_window_length, time_granularity,
                                                            time_granularity_value):
            model_save_path = os.path.join(root_model_save_path, dataset_name)
            model_save_path = make_file_path(model_save_path, start_date, end_date)
            os.makedirs(model_save_path, exist_ok=True)
            if len(os.listdir(model_save_path)) > 0:
                LoggerManager().get_logger(__name__).info("already trained --- skipping")
                continue
            model = self.classifiers_classes[classifier_name](model_save_path)

            dataset_path = self.classifier_to_dataset[classifier_name][dataset_name]
            date_type = self.datasets_date_type[dataset_name]
            meta_file_path = self.datasets_meta_path[dataset_name]
            labels = get_labels_from_meta(dataset_path, self.datasets_vtt[dataset_name],
                                          start_date, end_date,  date_type, meta_file_path)
            samples_hashes_list = get_shas_in_time_frame(dataset_path, start_date, end_date, date_type, meta_file_path)

            model.train(dataset_path, labels, samples_hashes_list=samples_hashes_list,
                        family_dict_path=families, compact_data=compact_data)
            model.save()

    def evaluate_all(self, classifiers_dir_path, start_date, end_date, results_save_dir,
                     time_granularity="monthly", time_granularity_value=1,
                     training_window=12, test_window=12):
        """
        Evaluate all models in classifiers_dir_path in a time window rolling manner.
        This directory should be the one passed as save_dir to the train_all method.

        time_granularity, time_granularity_value, training_window, and test_window must be set to the same values
        used in training.

        :param classifiers_dir_path: path to directory where the trained models are saved. It should have a structure
                                        such as ClassifierName/DatasetName/Date1...DateK
        :param start_date: the earliest date in the dataset you want to perform a temporal luck evaluation over.
        :param end_date: latest date in the dataset you want to perform a temporal luck evaluation over.
                            (includes latest test date available).
        :param results_save_dir: path to directory where to save the results.
        :param time_granularity: can be set to "monthly" "yearly" or "daily".
        :param time_granularity_value: how many days/months/years in each time slot.
        :param training_window: how many years/months/days in each training splits in the evaluation.
        :param test_window: how many years/months/days in each testing splits in the evaluation.
        """
        for classifier_name in sorted(self.classifiers):
            for dataset_name in sorted(self.datasets):
                LoggerManager.get_logger(__name__).info(f"Classifier={classifier_name} | Dataset={dataset_name}")
                output_dir = os.path.join(results_save_dir, classifier_name)
                os.makedirs(output_dir, exist_ok=True)
                classifier_results = self.evaluate_classifier(classifier_name, classifiers_dir_path, dataset_name,
                                                              start_date, end_date, time_granularity,
                                                              time_granularity_value, training_window,
                                                              test_window, output_dir)
                a_aut, std_aut = average_aut(classifier_results, "f1", start_date, end_date,
                                             time_granularity, test_window)
                print(f"Classifier: {classifier_name} - Dataset: {dataset_name} - [{start_date}-{end_date}]"
                      f"A-AUT {a_aut} ({std_aut})")

    def evaluate_classifier(self, classifier_name, classifier_dir_path, dataset_name, start_date, end_date,
                            time_granularity, time_granularity_value, train_window_length, test_window_length,
                            output_dir, skip_if_non_empty=True):
        results = {}
        training_iterator = training_slice_iterator(start_date, end_date, train_window_length, test_window_length,
                                                    time_granularity, time_granularity_value)
        test_iterator = test_slice_iterator(start_date, end_date, train_window_length, test_window_length,
                                            time_granularity, time_granularity_value)
        for training_window, test_window in zip(training_iterator, test_iterator):
            LoggerManager.get_logger(__name__).info(
                f"Testing model trained on {training_window[0]}-{training_window[1]} "
                f"on range [{test_window[0]}, {test_window[1]}]")
            save_path = os.path.join(output_dir, dataset_name)
            save_path = make_file_path(save_path, test_window[0], test_window[1])
            os.makedirs(save_path, exist_ok=True)
            save_path = os.path.join(save_path, f"time_aware_evaluations.pickle")

            if skip_if_non_empty and os.path.exists(save_path):
                LoggerManager.get_logger(__name__).info("already computed --- skipping")
                results.update(load_pickle(save_path))
                continue

            dataset_path = self.classifier_to_dataset[classifier_name][dataset_name]
            date_type = self.datasets_date_type[dataset_name]
            meta_file_path = self.datasets_meta_path[dataset_name]
            labels_dict = get_labels_from_meta(dataset_path, self.datasets_vtt[dataset_name],
                                               test_window[0], test_window[1], date_type,
                                               meta_file_path, is_azoo_meta=False)
            print("dataset path and dates", dataset_path, test_window[0], test_window[1], date_type, meta_file_path)
            samples_by_date_dict = divide_samples_by_date(dataset_path, test_window[0], test_window[1], date_type,
                                                          time_granularity, time_granularity_value, meta_file_path)

            classifier_class = self.classifiers_classes[classifier_name]
            classifier_dir = os.path.join(classifier_dir_path, classifier_name, dataset_name)
            classifier_dir = make_file_path(classifier_dir, training_window[0], training_window[1])
            classifier = classifier_class(classifier_dir)
            classifier.load()

            time_aware_evaluation_results = classifier.evaluate_time_aware(
                dataset_path, labels_dict, samples_by_date_dict
            )
            dump_pickle(save_path, time_aware_evaluation_results)
            results.update(time_aware_evaluation_results)
        return results
