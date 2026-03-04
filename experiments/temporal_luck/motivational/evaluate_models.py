import os
import tqdm
import argparse
import datetime

from android_malware_detectors.utils.io_operations import dump_pickle
from android_malware_detectors.datasets_utils.dataset_builder import get_labels_from_meta
from android_malware_detectors.datasets_utils.dataset_builder import divide_samples_by_date
from android_malware_detectors.utils.logging import LoggerManager

from experiments.utils import get_model_class


def evaluate_all_models(classifiers_list, classifiers_path_root, dataset_names_list, dataset_paths_list,
                        meta_file_paths_list, start_year, end_year, date_type_list,
                        vtts_list, root_output_dir):
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
            evaluate_dataset_by_year(classifier_type, classifier_dir, dataset_path, meta_file_path,
                                     start_year, end_year, date_type, vtt, output_dir)


def evaluate_dataset_by_year(classifier_type, root_classifier_dir, dataset_path, meta_file_path, start_year, end_year,
                             date_type, vtt, output_dir, skip_if_non_empty=True):
    for year in range(start_year, end_year + 1):
        LoggerManager.get_logger(__name__).info(f"Testing model trained on {year} "
                                                f"on range [{year + 1}, {end_year + 1}]")

        save_path = os.path.join(output_dir, str(year))
        os.makedirs(save_path, exist_ok=True)
        save_path = os.path.join(save_path, f"time_aware_evaluations.pickle")

        if skip_if_non_empty and os.path.exists(save_path):
            LoggerManager.get_logger(__name__).info("already computed --- skipping")
            continue

        start_date = datetime.date(day=1, month=1, year=year + 1)
        end_date = datetime.date(day=31, month=12, year=end_year + 1)
        labels_dict = get_labels_from_meta(dataset_path, vtt, start_date, end_date,
                                           date_type, meta_file_path, is_azoo_meta=False)
        print("dataset path and dates", dataset_path, start_date, end_date, date_type, meta_file_path)
        samples_by_date_dict = divide_samples_by_date(dataset_path, start_date, end_date, date_type,
                                                      "monthly", 1, meta_file_path)

        classifier_class = get_model_class(classifier_type)
        classifier_dir = os.path.join(root_classifier_dir, str(year))
        classifier = classifier_class(classifier_dir)
        classifier.load()

        time_aware_evaluation_results = classifier.evaluate_time_aware(dataset_path, labels_dict, samples_by_date_dict)
        dump_pickle(time_aware_evaluation_results, save_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("classifiers_list", nargs="+", choices=["DrebinSVM", "Malscan", "RAMDA", "DeepDrebin", "HCC"])
    parser.add_argument("--classifiers-path", required=True)
    parser.add_argument("--datasets", nargs="+")
    parser.add_argument("--datasets-paths", nargs="+")
    parser.add_argument("--meta-paths", nargs="+")
    parser.add_argument("--date-types", nargs="+")
    parser.add_argument("--start-year", type=int, default=2014)
    parser.add_argument("--end-year", type=int, default=2017)
    parser.add_argument("--vtts", nargs="+", type=int, default=[15, 4])
    parser.add_argument("--root-output-dir", default="evaluation_results/temporal_luck")
    args = parser.parse_args()

    assert (len(args.classifiers_list) * len(args.datasets)) == len(args.datasets_paths)
    assert len(args.meta_paths) == len(args.vtts) == len(args.date_types)

    os.makedirs(args.root_output_dir, exist_ok=True)

    evaluate_all_models(args.classifiers_list, args.classifiers_path, args.datasets, args.datasets_paths,
                        args.meta_paths, args.start_year, args.end_year, args.date_types,
                        args.vtts, args.root_output_dir)
