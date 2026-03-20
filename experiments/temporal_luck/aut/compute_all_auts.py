import datetime

from hypercube.utils import get_model_class
from hypercube.temporal_luck.temporal_luck_evaluator import TemporalLuckEvaluator


if __name__ == '__main__':
    classifiers_list = ["DrebinSVM", "DeepDrebin", "HCC", "RAMDA", "MalScan"]
    classifiers_path_root = "trained_models/temporal_luck/motivational"
    datasets = ["APIGraph", "Transcendent"]
    datasets_paths = ["data/datasets/apigraph/apigraph_drebin.json",
                      "data/datasets/transcendent/transcendent_drebin.json",
                      "data/datasets/apigraph/apigraph_drebin.json",
                      "data/datasets/transcendent/transcendent_drebin.json",
                      "data/datasets/apigraph/apigraph_drebin.json",
                      "data/datasets/transcendent/transcendent_drebin.json",
                      "data/datasets/apigraph/apigraph_ramda.pickle",
                      "data/datasets/transcendent/transcendent_ramda.pickle",
                      "data/datasets/apigraph/apigraph_malscan.pickle",
                      "data/datasets/transcendent/transcendent_malscan.pickle"]
    meta_paths = ["data/meta_files/apigraph_meta.json", "data/meta_files/transcendent_meta.json"]
    vtts = [15, 4]
    date_types = ["vt_first_submission_date", "dex_date"]
    save_dir = "evaluation_results/temporal_luck/motivational"
    families = "data/all_families_db.json"
    start_date, end_date = datetime.date(2014, 1, 1), datetime.date(2018, 12, 31)
    training_window, test_window, time_granularity, time_granularity_value = 12, 12, "monthly", 1

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
