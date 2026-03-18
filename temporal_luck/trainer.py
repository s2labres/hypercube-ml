import os
import argparse

from android_malware_detectors.datasets_utils.dates import parse_date

from experiments.utils import get_model_class

import tqdm
from android_malware_detectors.datasets_utils.dataset_builder import get_labels_from_meta, get_shas_in_time_frame
from android_malware_detectors.utils import LoggerManager

from temporal_luck.temporal_windows import training_slice_iterator


def train_all_classifiers(classifiers_list, dataset_names, dataset_paths_list, meta_file_paths_list, vtts,
                          start_date, end_date, training_window_length, test_window_length, time_granularity,
                          time_granularity_value, date_types, save_dir, families, compact_data):
    for index, classifier_type in enumerate(classifiers_list):
        dataset_index = index * len(dataset_names)
        dataset_paths = dataset_paths_list[dataset_index:dataset_index + len(dataset_names)]
        iterator = zip(dataset_names, dataset_paths, meta_file_paths_list, vtts, date_types)
        progressive_iterator = tqdm.tqdm(iterator, total=len(classifiers_list))
        for dataset_name, dataset_path, meta_file_path, vtt, date_type in progressive_iterator:
            model_save_dir = os.path.join(save_dir, classifier_type, dataset_name)
            os.makedirs(model_save_dir, exist_ok=True)
            train_classifier(classifier_type, dataset_path, meta_file_path, vtt, start_date, end_date,
                             training_window_length, test_window_length, time_granularity,
                             time_granularity_value, date_type, model_save_dir, families, compact_data)


def train_classifier(classifier_type, dataset_path, meta_file_path, vtt, dataset_min_date, dataset_max_date,
                     training_window_length, test_window_length, time_granularity, time_granularity_value,
                     date_type, root_model_save_path, families, compact_data):
    model_class = get_model_class(classifier_type)

    for start_date, end_date in training_slice_iterator(dataset_min_date, dataset_max_date, training_window_length,
                                                        test_window_length, time_granularity, time_granularity_value):
        model_save_path = os.path.join(root_model_save_path, f"{start_date.year}")
        os.makedirs(model_save_path, exist_ok=True)
        if len(os.listdir(model_save_path)) > 0:
            LoggerManager().get_logger(__name__).info("already trained --- skipping")
            continue
        model = model_class(model_save_path)

        labels = get_labels_from_meta(dataset_path, vtt, start_date, end_date, date_type, meta_file_path)
        samples_hashes_list = get_shas_in_time_frame(dataset_path, start_date, end_date, date_type, meta_file_path)

        model.train(dataset_path, labels, samples_hashes_list=samples_hashes_list,
                    family_dict_path=families, compact_data=compact_data)
        model.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("classifiers_list", nargs='+', choices=["DrebinSVM", "DeepDrebin", "RAMDA", "MalScan", "HCC"],
                        help="The list of classifiers to train.")
    parser.add_argument("--datasets", nargs='+', required=True,
                        help="The list of dataset names that will be used for training.")
    parser.add_argument("--datasets-paths", nargs='+', required=True,
                        help="The list of dataset paths that will be used for training. Entries should be ordered "
                             "by classifier type and dataset name. Namely, if your classifiers_list is "
                             "DrebinSVM and MalScan while your datasets are Transcendent and APIGraph, then you should "
                             "provide: path_to_Transcendent_drebin_feats_dataset, path_to_APIGraph_drebin_feats_dataset"
                             ", path_to_Transcendent_malscan_feats_dataset, path_to_APIGraph_malscan_feats_dataset.")
    parser.add_argument("--meta-paths", nargs='+', required=True,
                        help="The list of meta paths that will be used for training,"
                             " one per dataset name (in the same order).")
    parser.add_argument("--vtts", type=int, required=True, nargs='+',
                        help="The list of VTT values that will be used for training,"
                             " one per dataset name (in the same order).")
    parser.add_argument("--date-types", choices=["dex_date", "vt_first_submission_date", "gp_date"],
                        required=True, nargs='+', help="The list of date types that will be used for training,"
                        " one per dataset name (in the same order).")
    parser.add_argument("--start-date", type=str,
                        help="The start date you want to use. Several date formats are supported.")
    parser.add_argument("--end-date", type=str,
                        help="The end date you want to use. Several date formats are supported.")
    parser.add_argument("--training-window", type=int, default=12,
                        help="The number of months each training split should be composed of.")
    parser.add_argument("--test-window", type=int, default=12,
                        help="The number of months each test split should be composed of.")
    parser.add_argument("--time-granularity", type=str, choices=["daily", "monthly", "yearly"], default="monthly",
                        help="The time granularity in your evaluation. It supports splitting the dataset into"
                             " daily, monthly or yearly slots.")
    parser.add_argument("--time-granularity-value", type=int, default=1,
                        help="How many days/months/years to include in each slot.")
    parser.add_argument("--families", default="data/all_families_db.json",
                        help="Path to a json containing the family name for each malware sample. "
                             "Only needed for some classifiers (e.g., HCC).")
    parser.add_argument("--save-dir", default="trained_models/temporal_luck/motivational",
                        help="Path to the root directory where to save all trained models.")
    parser.add_argument("--compact-data", default=False, action="store_true",
                        help="set to true if using not compacted data with malscan")
    args = parser.parse_args()

    assert (len(args.datasets) * len(args.classifiers_list)) == len(args.datasets_paths)
    assert len(args.meta_paths) == len(args.vtts) == len(args.date_types) == len(args.datasets)

    train_all_classifiers(args.classifiers_list, args.datasets, args.datasets_paths, args.meta_paths,
                          args.vtts, parse_date(args.start_date), parse_date(args.end_date), args.training_window,
                          args.test_window, args.time_granularity, args.time_granularity_value, args.date_types,
                          args.save_dir, args.families, args.compact_data)
