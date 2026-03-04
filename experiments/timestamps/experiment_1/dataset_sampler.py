import os
import random
import argparse
import datetime
from collections import defaultdict
from datetime import date, timedelta

import tqdm

from android_malware_detectors.utils.io_operations import dump_json, load_json
from android_malware_detectors.datasets_utils.dates import get_year, parse_date
from android_malware_detectors.datasets_utils.androzoo_utils import load_androzoo_info_by_keys


def sample_new_malware_datasets(meta_file_path, azoo_csv_path, output_dir, num_datasets, vtt, emulate_transcendent):
    malware_count_by_month = get_malware_count_by_month_year(meta_file_path)
    az_dict = load_androzoo_info_by_keys(
        azoo_csv_path, keys=["vt_detection", "dex_date", "added", "vt_scan_date"],
        output_dir="../", crawl_date_present=True
    )
    malware_by_month = get_available_malware_by_month_year(az_dict, vtt, emulate_transcendent)
    for dataset_index in tqdm.tqdm(range(num_datasets)):
        current_date = date(day=1, month=1, year=2014)
        current_dataset = []
        while current_date.year <= 2018:
            month_year = get_month_year(current_date)
            malware = sample_malware_by_month(malware_by_month, month_year, malware_count_by_month)
            current_dataset.extend(malware)
            current_date += timedelta(31)
            current_date = date(year=current_date.year, month=current_date.month, day=1)
        datasets_file_path = os.path.join(output_dir, f"meta_{dataset_index + 1}.json")
        meta_file = make_meta_file(current_dataset, az_dict)
        dump_json(datasets_file_path, current_dataset)


def sample_malware_by_month(hashes_by_mont_year, month_year, malware_count_by_month_year):
    sample_size = malware_count_by_month_year[month_year]
    if len(hashes_by_mont_year[month_year]) < sample_size:
        print(f"ERROR in {month_year}: available {len(hashes_by_mont_year[month_year])} requested {sample_size}")
        sample_size = len(hashes_by_mont_year[month_year])
    return random.sample(hashes_by_mont_year[month_year], sample_size)


def get_malware_count_by_month_year(meta_file):
    meta_info_list = load_json(meta_file)
    malware_by_month = defaultdict(int)

    for entry in meta_info_list:
        month_year = get_month_year(entry["dex_date"])
        vt_detection = int(entry["vt_detection"])
        if vt_detection >= 4:
            malware_by_month[month_year] += 1

    return malware_by_month


def get_available_malware_by_month_year(az_dict, vtt, emulate_transcendent):
    malware_by_month = defaultdict(list)
    for sha, entry in az_dict.items():
        if emulate_transcendent:
            emulate_transcendent_sampling(sha, entry, malware_by_month, vtt)
        else:
            dex_date = parse_date(entry["dex_date"])
            if 2014 <= dex_date.year <= 2018:
                malware_by_month[get_month_year(dex_date)].append(sha)

    return malware_by_month


def emulate_transcendent_sampling(sha, azoo_entry, malware_by_month, vtt):
    if azoo_entry.get("vt_scan_date"):
        dex_date = azoo_entry["dex_date"]
        if dex_date:
            if check_malware_existed_in_tesseract(azoo_entry, vtt):
                month_year = get_month_year(dex_date)
                malware_by_month[month_year].append(sha)
            elif check_malware_existed_in_intriguing_properties(azoo_entry, vtt):
                month_year = get_month_year(dex_date)
                malware_by_month[month_year].append(sha)


def check_malware_existed_in_tesseract(azoo_entry, vtt):
    vt_detection = int(azoo_entry.get("vt_detection", 0))
    return (vt_detection >= vtt and 2014 <= get_year(azoo_entry["dex_date"]) <= 2016 and
            parse_date(azoo_entry["added"]) <= datetime.date(2017, 4, 8) and
            parse_date(azoo_entry["vt_scan_date"]) <= datetime.date(2017, 4, 8))


def check_malware_existed_in_intriguing_properties(azoo_entry, vtt):
    vt_detection = int(azoo_entry.get("vt_detection", 0))
    return (vt_detection >= vtt and 2017 <= get_year(azoo_entry["dex_date"]) <= 2018 and
            parse_date(azoo_entry["added"]) <= datetime.date(2019, 1, 12) and
            parse_date(azoo_entry["vt_scan_date"]) <= datetime.date(2019, 1, 12))


def get_month_year(date_object):
    datetime_object = parse_date(date_object)
    return f"{datetime_object.year}-{datetime_object.month}"


def make_meta_file(current_dataset, az_dict):
    meta = {}
    for sha_256 in current_dataset:
        entry = az_dict[sha_256.lower()]
        meta[sha_256.lower()] = {"dex_date": entry["dex_date"], "vt_detection": entry["vt_detection"]}
    return meta


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-datasets", type=int, default=3)
    parser.add_argument("--vtt", type=int, default=4)
    args = parser.parse_args()

    _num_datasets = args.num_datasets
    _azoo_csv_path = "./data/latest_with-added-date.csv"
    _meta_file_path = "./data/meta_files/transcend_meta.json"

    _output_dir = f"./data/timestamps/experiment_1/transcend_emulation"
    os.makedirs(_output_dir, exist_ok=True)
    sample_new_malware_datasets(_meta_file_path, _azoo_csv_path, _output_dir, _num_datasets, args.vtt, True)

    _output_dir = f"./data/timestamps/experiment_1/transcend_sampled_today"
    os.makedirs(_output_dir, exist_ok=True)
    sample_new_malware_datasets(_meta_file_path, _azoo_csv_path, _output_dir, _num_datasets, args.vtt, False)
