import os
import tqdm
import argparse
import datetime

from android_malware_detectors.datasets_utils.dates import generate_dates_in_interval
from android_malware_detectors.utils.io_operations import dump_pickle
from android_malware_detectors.datasets_utils.dataset_builder import get_labels_from_meta
from android_malware_detectors.datasets_utils.dataset_builder import divide_samples_by_date
from android_malware_detectors.utils.logging import LoggerManager

from experiments.utils import get_model_class
from temporal_luck.aut import average_aut
from temporal_luck.temporal_windows import training_slice_iterator, test_slice_iterator
from temporal_luck.utils import make_file_path


def evaluate_all_models(classifiers_list, classifiers_path_root, dataset_names_list, dataset_paths_list,
                        meta_file_paths_list, start_date, end_date, date_type_list, vtts_list,
                        root_output_dir, time_granularity="monthly", time_granularity_value=1,
                        training_window=12, test_window=12):
    classifiers_paths = []
    for classifier_type in classifiers_list:
        for dataset_name in dataset_names_list:
            classifiers_paths.append(os.path.join(classifiers_path_root, classifier_type, dataset_name))

    for index, classifier_type in enumerate(classifiers_list):
        start_index, end_index = (index * len(dataset_names_list),
                                  index * len(dataset_names_list) + len(dataset_names_list))
        dataset_paths = dataset_paths_list[start_index:end_index]
        iterator = zip(classifiers_paths[start_index:end_index], dataset_names_list, dataset_paths,
                       meta_file_paths_list, date_type_list, vtts_list)
        progressive_iterator = tqdm.tqdm(iterator, total=len(dataset_names_list))

        for classifier_dir, dataset_name, dataset_path, meta_file_path, date_type, vtt in progressive_iterator:
            LoggerManager.get_logger(__name__).info(f"Classifier={classifier_type} | Dataset={dataset_name}")
            output_dir = os.path.join(root_output_dir, classifier_type, dataset_name)
            os.makedirs(output_dir, exist_ok=True)
            classifier_results = evaluate_classifier(classifier_type, classifier_dir, dataset_path, meta_file_path,
                                                     start_date, end_date, date_type, vtt, output_dir)
            a_aut, std_aut = average_aut(classifier_results, "f1", start_date, end_date, time_granularity, time_granularity_value)
            print(f"A-AUT {}")


def evaluate_classifier(classifier_type, root_classifier_dir, dataset_path, meta_file_path, start_date, end_date,
                        time_granularity, time_granularity_value, train_window_length, test_window_length,
                        date_type, vtt, output_dir, skip_if_non_empty=True):
    results = {}
    training_iterator = training_slice_iterator(start_date, end_date, time_granularity, time_granularity_value,
                                                train_window_length, test_window_length)
    test_iterator = test_slice_iterator(start_date, end_date, time_granularity, time_granularity_value,
                                        train_window_length, test_window_length)
    for training_window, test_window in zip(training_iterator, test_iterator):
        LoggerManager.get_logger(__name__).info(f"Testing model trained on {training_window[0]}-{training_window[1]} "
                                                f"on range [{test_window[0]}, {test_window[1]}]")
        save_path = make_file_path(output_dir, test_window[0], test_window[1])
        os.makedirs(save_path, exist_ok=True)
        save_path = os.path.join(save_path, f"time_aware_evaluations.pickle")

        if skip_if_non_empty and os.path.exists(save_path):
            LoggerManager.get_logger(__name__).info("already computed --- skipping")
            continue
        labels_dict = get_labels_from_meta(dataset_path, vtt, test_window_length[0], test_window_length[1],
                                           date_type, meta_file_path, is_azoo_meta=False)
        print("dataset path and dates", dataset_path, test_window[0], test_window[1], date_type, meta_file_path)
        samples_by_date_dict = divide_samples_by_date(dataset_path, test_window[0], test_window[1], date_type,
                                                      time_granularity, time_granularity_value, meta_file_path)

        classifier_class = get_model_class(classifier_type)
        classifier_dir = make_file_path(root_classifier_dir, training_window[0], training_window[1])
        classifier = classifier_class(classifier_dir)
        classifier.load()

        time_aware_evaluation_results = classifier.evaluate_time_aware(dataset_path, labels_dict, samples_by_date_dict)
        dump_pickle(save_path, time_aware_evaluation_results)
        results.update(time_aware_evaluation_results)
    return results
