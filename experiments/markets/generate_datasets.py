import os
import random

import tqdm
from android_malware_detectors.datasets_utils.androzoo_utils import load_androzoo_info_by_keys
from android_malware_detectors.utils import dump_json

from experiments.markets.dataset_configurations import get_amounts_to_sample


def generate_all_datasets(azoo_csv, vtt=2):
    configs = ["gp", "aa", "even", "prop", "gpaa", "aagp"]
    azoo_dict = load_androzoo_info_by_keys(azoo_csv, keys=["vt_detection", "markets"], crawl_date_present=True)
    chinese_malware, gp_malware = get_available_malware(azoo_dict, vtt)
    chinese_goodware, gp_goodware = get_available_goodware(azoo_dict)
    for config in tqdm.tqdm(configs, desc="Configs"):
        for run_number in tqdm.tqdm(range(1, 6), desc=f"Runs for {config}", leave=False):
            chinese_malware_copy, chinese_goodware_copy = chinese_malware.copy(), chinese_goodware.copy()
            gp_malware_copy, gp_goodware_copy = gp_malware.copy(), gp_goodware.copy()
            random.seed(run_number)
            create_dataset(config, gp_goodware_copy, gp_malware_copy,
                           chinese_goodware_copy, chinese_malware_copy,
                           run_number)


def create_dataset(dataset_configuration, gp_goodware, gp_malware, aa_goodware, aa_malware, run_number=1):
    (train_goodware_gp, train_goodware_aa, train_malware_gp, train_malware_aa,
     test_goodware_gp, test_goodware_aa, test_malware_gp, test_malware_aa) = get_amounts_to_sample(
        dataset_configuration
    )

    train_shas = randomly_sample_and_pop(gp_goodware, train_goodware_gp)
    train_shas += randomly_sample_and_pop(aa_goodware, train_goodware_aa)
    train_shas += randomly_sample_and_pop(gp_malware, train_malware_gp)
    train_shas += randomly_sample_and_pop(aa_malware, train_malware_aa)

    test_shas = randomly_sample_and_pop(gp_goodware, test_goodware_gp)
    test_shas += randomly_sample_and_pop(aa_goodware, test_goodware_aa)
    test_shas += randomly_sample_and_pop(gp_malware, test_malware_gp)
    test_shas += randomly_sample_and_pop(aa_malware, test_malware_aa)

    base_path = f"data/app_market_experiment/shas/{dataset_configuration}/"
    os.makedirs(base_path, exist_ok=True)
    train_file_path = os.path.join(base_path, f"train_{run_number}.json")
    dump_json(train_file_path, train_shas)
    test_file_path = os.path.join(base_path, f"test_{run_number}.json")
    dump_json(test_file_path, test_shas)


def get_available_malware(azoo_dict, vtt):
    chinese_malware, gp_malware = [], []
    for sha, entry in azoo_dict.items():
        if entry["vt_detection"] and int(entry["vt_detection"]) >= vtt:
            if "google" in entry["markets"]:
                gp_malware.append(sha)
            if "anzhi" in entry["markets"] or "appchina" in entry["markets"]:
                chinese_malware.append(sha)
    return chinese_malware, gp_malware


def get_available_goodware(azoo_dict):
    chinese_goodware, gp_goodware = [], []
    for sha, entry in azoo_dict.items():
        if entry["vt_detection"] == '0':
            if "google" in entry["markets"]:
                gp_goodware.append(sha)
            if "anzhi" in entry["markets"] or "appchina" in entry["markets"]:
                chinese_goodware.append(sha)
    return chinese_goodware, gp_goodware


def randomly_sample_and_pop(hash_list, n):
    if n == 0:
        return []
    if n > len(hash_list):
        raise ValueError("n is greater than the number of items in the list.")
    selected = random.sample(hash_list, n)
    for item in selected:
        hash_list.remove(item)
    return selected


if __name__ == "__main__":
    azoo_csv_path = "data/latest_with-added-date.csv"
    generate_all_datasets(azoo_csv_path)
