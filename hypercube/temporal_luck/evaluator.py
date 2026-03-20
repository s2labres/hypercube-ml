import argparse

from hypercube.utils import get_model_class
from hypercube.temporal_luck.temporal_luck_evaluator import TemporalLuckEvaluator


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

    temporal_luck_evaluator = TemporalLuckEvaluator()
    for classifier in classifiers_list:
        classifier_class = get_model_class(classifier)
        temporal_luck_evaluator.register_classifier_class(classifier, classifier_class)

    for dataset_name in datasets:
        temporal_luck_evaluator.register_dataset(dataset_name)

    for dataset_name, dataset_meta_path in zip(datasets, meta_paths):
        temporal_luck_evaluator.register_meta_path(dataset_name, dataset_meta_path)

    for dataset_name, vtt in zip(datasets, vtts):
        temporal_luck_evaluator.register_vtt(dataset_name, vtt)

    for dataset_name, date_type in zip(datasets, date_types):
        temporal_luck_evaluator.register_date_type(dataset_name, date_type)

    for classifier_index, classifier in enumerate(classifiers_list):
        datasets_paths_for_classifier = datasets_paths[
            classifier_index * len(datasets):(classifier_index + 1) * len(datasets)
        ]
        for dataset_index, dataset_name in enumerate(datasets):
            temporal_luck_evaluator.register_dataset_for_classifier(
                dataset_name, classifier, datasets_paths_for_classifier[dataset_index]
            )

    temporal_luck_evaluator.evaluate_all(classifiers_path_root, start_date, end_date, save_dir,
                                         time_granularity, time_granularity_value,
                                         training_window, test_window)
