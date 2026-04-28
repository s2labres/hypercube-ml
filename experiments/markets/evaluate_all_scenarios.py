import os
import json
import pickle

import tqdm
from android_malware_detectors.datasets_utils.androzoo_utils import load_androzoo_info_by_keys
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
    for run_number in range(1, 6):
        print('#' * 20)
        print(f"Classifier {classifier_type} | Config {experiment_config} | Run {run_number}")
        print('#' * 20)

        train_config = experiment_config.split('_')[0]
        test_config = experiment_config.split('_')[1]

        base_path = "data/app_markets/shas"
        train_file = os.path.join(base_path, train_config, "train_{run_number}.json")
        test_file = os.path.join(base_path, test_config, "test_{run_number}.json")
        training_shas, testing_shas = load_json(train_file), load_json(test_file)

        base_feature_path = 'data/datasets/app_markets/'
        train_dataset_path, test_dataset_path, labels_dict_train, labels_dict_test = get_dataset_and_labels(classifier_type, azoo_dict, base_feature_path, train_config, test_config)
        if classifier_type == "Drebin":

            training_shas = check_if_sha_in_dict(labels_dict_train, training_shas)
            testing_shas = check_if_sha_in_dict(labels_dict_test, testing_shas)

            mod_output_dir = os.path.join(output_dir, f'drebin')
            os.makedirs(mod_output_dir, exist_ok=True)

            drebin_svm = DrebinSVM(mod_output_dir)
            drebin_svm.train(train_dataset_path, labels_dict_train, training_shas)

            evaluation_results = drebin_svm.evaluate(test_dataset_path, labels_dict_test, testing_shas)
            save_path = os.path.join(mod_output_dir, f'performance_{run_number}.pkl')
            with open(save_path, 'wb') as f:
                pickle.dump(evaluation_results, f)

        elif classifier_type == "DeepDrebin":
            train_dataset_path = os.path.join(base_feature_path, f'{train_config}/train_compressed_drebin.json')
            test_dataset_path = os.path.join(base_feature_path, f'{test_config}/test_compressed_drebin.json')

            labels_dict_train = get_labels_from_meta(
                train_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            labels_dict_test = get_labels_from_meta(
                test_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            training_shas = check_if_sha_in_dict(labels_dict_train, training_shas)
            testing_shas = check_if_sha_in_dict(labels_dict_test, testing_shas)

            mod_output_dir = os.path.join(output_dir, f'deepdrebin')
            os.makedirs(mod_output_dir, exist_ok=True)

            deep_drebin = DeepDrebin(mod_output_dir)
            deep_drebin.train(train_dataset_path, labels_dict_train, training_shas)

            evaluation_results = deep_drebin.evaluate(test_dataset_path, labels_dict_test, testing_shas)
            save_path = os.path.join(mod_output_dir, f'performance_{run_number}.pkl')
            with open(save_path, 'wb') as f:
                pickle.dump(evaluation_results, f)

        elif classifier_type == "Malscan":

            labels_dict_train = get_labels_from_meta(
                train_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            labels_dict_test = get_labels_from_meta(
                test_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            training_shas = check_if_sha_in_dict(labels_dict_train, training_shas)
            testing_shas = check_if_sha_in_dict(labels_dict_test, testing_shas)

            mod_output_dir = os.path.join(output_dir, f'malscan')
            os.makedirs(mod_output_dir, exist_ok=True)

            malscan = MalScanRF(mod_output_dir)
            malscan.train(train_dataset_path, labels_dict_train, training_shas)

            evaluation_results = malscan.evaluate(test_dataset_path, labels_dict_test, testing_shas)
            save_path = os.path.join(mod_output_dir, f'performance_{run_number}.pkl')
            with open(save_path, 'wb') as f:
                pickle.dump(evaluation_results, f)

        elif classifier_type == "RAMDA":


            labels_dict_train = get_labels_from_meta(
                train_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            labels_dict_test = get_labels_from_meta(
                test_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            training_shas = check_if_sha_in_dict(labels_dict_train, training_shas)
            testing_shas = check_if_sha_in_dict(labels_dict_test, testing_shas)

            mod_output_dir = os.path.join(output_dir, f'ramda')
            os.makedirs(mod_output_dir, exist_ok=True)

            ramda_detector = RAMDADetector(mod_output_dir)
            ramda_detector.train(train_dataset_path, labels_dict_train, training_shas)

            evaluation_results = ramda_detector.evaluate(test_dataset_path, labels_dict_test, testing_shas)
            save_path = os.path.join(mod_output_dir, f'performance_{run_number}.pkl')
            with open(save_path, 'wb') as f:
                pickle.dump(evaluation_results, f)

        elif classifier_type == "HCC":
            train_dataset_path = os.path.join(base_feature_path, f'{train_config}/train_compressed_drebin.json')
            test_dataset_path = os.path.join(base_feature_path, f'{test_config}/test_compressed_drebin.json')

            labels_dict_train = get_labels_from_meta(
                train_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            labels_dict_test = get_labels_from_meta(
                test_dataset_path, vt_threshold, start_date, end_date, date_type, meta_file_path)

            training_shas = check_if_sha_in_dict(labels_dict_train, training_shas)
            testing_shas = check_if_sha_in_dict(labels_dict_test, testing_shas)

            mod_output_dir = os.path.join(output_dir, f'hcc')
            os.makedirs(mod_output_dir, exist_ok=True)

            family_dict_json = '/mnt/rds/metadata/all_families_db.json'
            hcc_detector = HCCDrebinDetector(mod_output_dir)
            hcc_detector.train(train_dataset_path, labels_dict_train, training_shas, family_dict_path=family_dict_json,
                               epochs=5)

            evaluation_results = hcc_detector.evaluate(test_dataset_path, labels_dict_test, testing_shas)
            save_path = os.path.join(mod_output_dir, f'performance_{run_number}.pkl')
            with open(save_path, 'wb') as f:
                pickle.dump(evaluation_results, f)
        else:
            raise ValueError(f"classifier {classifier_type} not supported")


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
    for hash in hashes:
        hash = hash.lower()
        result = label_dict.get(hash)

        if result != None:
            output.append(hash)

    return output


if __name__ == '__main__':
    _classifiers_list = ['HCC']
    _azoo_dict = load_androzoo_info_by_keys("data/latest_with-added-date.csv", keys=["vt_detection", "dex_date"])
    _root_output_dir = "evaluation_results/app_markets/"
    os.makedirs(_root_output_dir, exist_ok=True)

    evaluate_all(_classifiers_list, _azoo_dict, _root_output_dir)
