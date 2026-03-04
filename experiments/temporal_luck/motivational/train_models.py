import os
import argparse
from datetime import date

from experiments.utils import get_model_class

import tqdm
from android_malware_detectors.datasets_utils.dataset_builder import get_labels_from_meta, get_shas_in_time_frame
from android_malware_detectors.utils import LoggerManager


def train_all_models(classifiers_list, dataset_names, dataset_paths_list, meta_file_paths_list, vtts,
                     start_year, end_year, date_types, save_dir, families):
    for index, classifier_type in enumerate(classifiers_list):
        dataset_index = index * len(dataset_names)
        dataset_paths = dataset_paths_list[dataset_index:dataset_index + len(dataset_names)]
        iterator = zip(dataset_names, dataset_paths, meta_file_paths_list, vtts, date_types)
        progressive_iterator = tqdm.tqdm(iterator, total=len(classifiers_list))
        for dataset_name, dataset_path, meta_file_path, vtt, date_type in progressive_iterator:
            model_save_dir = os.path.join(save_dir, classifier_type, dataset_name)
            os.makedirs(model_save_dir, exist_ok=True)
            train_model(classifier_type, dataset_path, meta_file_path, vtt,
                        start_year, end_year, date_type, model_save_dir,
                        families)


def train_model(classifier_type, dataset_path, meta_file_path, vtt, start_year, end_year,
                date_type, root_model_save_path, families):
    model_class = get_model_class(classifier_type)

    for year in range(start_year, end_year):
        model_save_path = os.path.join(root_model_save_path, f"{year}")
        os.makedirs(model_save_path, exist_ok=True)
        if len(os.listdir(model_save_path)) > 0:
            LoggerManager().get_logger(__name__).info("already trained --- skipping")
            continue
        model = model_class(model_save_path)

        start_date = date(day=1, month=1, year=year)
        end_date = date(day=31, month=12, year=year)
        labels = get_labels_from_meta(dataset_path, vtt, start_date, end_date, date_type, meta_file_path)
        samples_hashes_list = get_shas_in_time_frame(dataset_path, start_date, end_date, date_type, meta_file_path)

        model.train(dataset_path, labels, samples_hashes_list=samples_hashes_list, family_dict_path=families)
        model.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("classifiers_list", nargs='+', choices=["DrebinSVM", "DeepDrebin", "RAMDA", "MalScan", "HCC"])
    parser.add_argument("--datasets", nargs='+', required=True)
    parser.add_argument("--datasets-paths", nargs='+', required=True)
    parser.add_argument("--meta-paths", nargs='+', required=True)
    parser.add_argument("--vtts", type=int, required=True, nargs='+')
    parser.add_argument("--date-types", choices=["dex_date", "vt_first_submission_date", "gp_date"],
                        required=True, nargs='+')
    parser.add_argument("--start-year", type=int, default=2014)
    parser.add_argument("--end-year", type=int, default=2018)
    parser.add_argument("--families")
    parser.add_argument("--save-dir")
    args = parser.parse_args()

    assert (len(args.datasets) * len(args.classifiers_list)) == len(args.datasets_paths)
    assert len(args.meta_paths) == len(args.vtts) == len(args.date_types) == len(args.datasets)

    train_all_models(args.classifiers_list, args.datasets, args.datasets_paths, args.meta_paths,
                     args.vtts, args.start_year, args.end_year, args.date_types,
                     args.save_dir, args.families)
