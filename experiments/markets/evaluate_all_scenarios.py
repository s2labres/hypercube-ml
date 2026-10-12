import os
import pickle
from argparse import ArgumentParser

import tqdm
from android_malware_detectors.detectors.drebin.deepdrebin import DeepDrebin
from android_malware_detectors.detectors.drebin.svm_detector import DrebinSVM
from android_malware_detectors.detectors.ramda.detector import RAMDADetector
from android_malware_detectors.detectors.malscan.malscan_rf import MalScanRF
from android_malware_detectors.detectors.hcc.hcc_drebin_detector import HCCDrebinDetector
from android_malware_detectors.datasets_utils.dataset_builder import get_labels_from_meta
from android_malware_detectors.utils import load_json


def evaluate_all(classifiers_list, azoo_dict, root_output_dir):
    experiments_list = ['gp_gp', 'gp_aa', 'gp_even', 'gp_prop',
                        'aa_aa', 'aa_gp', 'aa_even', 'aa_prop',
                        'even_gp', 'even_aa', 'even_even',
                        'prop_gp', 'prop_aa', 'prop_prop',
                        'gpaa_gpaa', 'gpaa_aagp',
                        'aagp_gpaa', 'aagp_aagp']

    for index, classifier_type in enumerate(classifiers_list):
        for experiment_config in experiments_list:
            print(f"Classifier={classifier_type} | Experiment={experiment_config}")
            output_dir = os.path.join(root_output_dir, f"exp/{experiment_config}")
            evaluate(classifier_type, azoo_dict, experiment_config, output_dir)


def evaluate(classifier_type, azoo_dict, experiment_config, output_dir):
    for run_number in tqdm.tqdm(range(1, 6)):
        print('#' * 20)
        print(f"Classifier {classifier_type} | Config {experiment_config} | Run {run_number}")
        print('#' * 20)

        train_config = experiment_config.split('_')[0]
        test_config = experiment_config.split('_')[1]

        base_path = "data/app_markets/shas"
        train_file = os.path.join(base_path, train_config, f"train_{run_number}.json")
        test_file = os.path.join(base_path, test_config, f"test_{run_number}.json")
        training_shas, testing_shas = load_json(train_file), load_json(test_file)

        base_feature_path = 'data/app_markets/datasets'
        train_dataset_path, test_dataset_path, labels_dict_train, labels_dict_test = get_dataset_and_labels(
            classifier_type, azoo_dict, base_feature_path, train_config, test_config
        )
        training_shas = check_if_sha_in_dict(labels_dict_train, training_shas)
        testing_shas = check_if_sha_in_dict(labels_dict_test, testing_shas)
        evaluate_classifier(run_number, classifier_type, train_dataset_path, test_dataset_path,
                            training_shas, testing_shas, labels_dict_train, labels_dict_test,
                            os.path.join(output_dir, str(run_number)))


def evaluate_classifier(run_number, classifier_type, train_dataset_path, test_dataset_path,
                        training_shas, testing_shas, labels_dict_train, labels_dict_test, output_dir):
    mod_output_dir = os.path.join(output_dir, classifier_type.lower())
    os.makedirs(mod_output_dir, exist_ok=True)
    if classifier_type == "DrebinSVM":
        detector = DrebinSVM(mod_output_dir)
    elif classifier_type == "DeepDrebin":
        detector = DeepDrebin(mod_output_dir)
    elif classifier_type == "MalScan":
        detector = MalScanRF(mod_output_dir)
    elif classifier_type == "RAMDA":
        detector = RAMDADetector(mod_output_dir)
    elif classifier_type == "HCC":
        detector = HCCDrebinDetector(mod_output_dir)
    else:
        raise ValueError(f"classifier {classifier_type} not supported")

    if classifier_type == "HCC":
        family_dict_json = 'data/all_families_db.json'
        detector.train(train_dataset_path, labels_dict_train, training_shas,
                       family_dict_path=family_dict_json, epochs=5)
    else:
        detector.train(train_dataset_path, labels_dict_train, training_shas)
    evaluation_results = detector.evaluate(test_dataset_path, labels_dict_test, testing_shas)
    save_path = os.path.join(mod_output_dir, f'performance_{run_number}.pkl')
    with open(save_path, 'wb') as f:
        pickle.dump(evaluation_results, f)


def get_dataset_and_labels(classifier_type, azoo_dict, base_feature_path, train_config, test_config, vtt=4):
    start_date, end_date, date_type = "1-1-1800", "1-1-2500", "dex_date"

    if classifier_type in ["DrebinSVM", "DeepDrebin", "HCC"]:
        train_dataset_path = os.path.join(base_feature_path, f'{train_config}/train_compressed_drebin.json')
        test_dataset_path = os.path.join(base_feature_path, f'{test_config}/test_compressed_drebin.json')
    elif classifier_type == "MalScan":
        train_dataset_path = os.path.join(base_feature_path, f'{train_config}/train_compressed_malscan.pickle')
        test_dataset_path = os.path.join(base_feature_path, f'{test_config}/test_compressed_malscan.pickle')
    elif classifier_type == "RAMDA":
        train_dataset_path = os.path.join(base_feature_path, f'{train_config}/train_compressed_ramda.pickle')
        test_dataset_path = os.path.join(base_feature_path, f'{test_config}/test_compressed_ramda.pickle')
    else:
        raise ValueError(f"Unknown classifier type: {classifier_type}")

    labels_dict_train = get_labels_from_meta(train_dataset_path, vtt, start_date, end_date,
                                             date_type, azoo_dict, is_azoo_meta=True)
    labels_dict_test = get_labels_from_meta(test_dataset_path, vtt, start_date, end_date,
                                            date_type, azoo_dict, is_azoo_meta=True)
    return train_dataset_path, test_dataset_path, labels_dict_train, labels_dict_test


def check_if_sha_in_dict(label_dict, hashes):
    output = []
    for sha in hashes:
        sha = sha.lower()
        label = label_dict.get(sha)
        if label is not None:
            output.append(sha)
    return output


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument("models_list", nargs='+', choices=["DrebinSVM", "DeepDrebin", "RAMDA", "MalScan", "HCC"])
    args = argument_parser.parse_args()
    _root_output_dir = "evaluation_results/app_markets/"
    os.makedirs(_root_output_dir, exist_ok=True)
    _azoo_dict = "/home/mario/data/android/latest-with-added-13-april-2026.csv"
    evaluate_all(args.models_list, _azoo_dict, _root_output_dir)
