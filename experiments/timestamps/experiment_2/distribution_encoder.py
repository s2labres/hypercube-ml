import random
from collections import defaultdict

import numpy as np
from jsonlines import jsonlines
from android_malware_detectors.datasets_utils.dates import parse_date, generate_dates_in_interval_monthly


def get_malware_families_in_period(malware_db, gp_dict, start_year, end_year=None):
    if end_year is None:
        malware_families = get_malware_families_in_year(malware_db, gp_dict, start_year)
        return sorted(malware_families)
    malware_families = set()
    for year in range(start_year, end_year + 1):
        malware_families.update(get_malware_families_in_year(malware_db, gp_dict, year))
    return sorted(malware_families)


def get_malware_families_in_year(malware_db, gp_dict, year):
    families_in_year = set()
    for h, entry in gp_dict.items():
        if int(entry.get("vt_detection", -1) or -1) >= 2:
            if (parse_date(entry.get("gp_date", "1-1-1990")).year == year
                    and parse_date(entry.get("crawl_date", "1-1-1990")).year == year):
                family = malware_db.get(h.lower())
                if family:
                    families_in_year.add(family)
    return families_in_year


def make_monthly_malware_distribution(malware_families, malware_db, gp_dict, start_date, end_date,
                                      vt_date_dict=None, use_vt=False, use_crawl_date=False):
    all_dates = generate_dates_in_interval_monthly(start_date, end_date)
    distribution = []
    for _date in all_dates:
        malware_families_present = defaultdict(int)
        for malware, entry in gp_dict.items():
            if _check_date(_date, malware, entry, vt_date_dict, use_vt=use_vt, use_crawl_date=use_crawl_date):
                family = malware_db.get(malware)
                if family:
                    malware_families_present[family] += 1
        month_distribution = [malware_families_present.get(family, 0) for family in malware_families]
        distribution.append(month_distribution)

    return np.asarray(distribution)


def make_monthly_goodware_distribution(gp_meta_data_path, gp_dict, start_date, end_date,
                                       vt_date_dict, use_vt=False, use_crawl_date=False):
    goodware_package_names, all_packages = _get_package_names_dict(gp_meta_data_path, gp_dict, vt_date_dict,
                                                                   start_date, end_date)
    all_dates = generate_dates_in_interval_monthly(start_date, end_date)
    distribution = []
    for _date in all_dates:
        package_names_present = defaultdict(int)
        for goodware, entry in gp_dict.items():
            if _check_date(_date, goodware, entry, vt_date_dict, use_vt, use_crawl_date):
                package_name = goodware_package_names.get(goodware)
                if package_name:
                    package_names_present[package_name] += 1
        month_distribution = [package_names_present.get(package_name, 0) for package_name in all_packages]
        distribution.append(month_distribution)

    return np.asarray(distribution)


def make_monthly_distribution_by_sha(gp_dict, start_date, end_date, vt_date_dict, malware=False,
                                     use_vt=False, use_crawl_date=False):
    all_shas = sorted({h for h, e in gp_dict.items() if (malware and int(e.get("vt_detection", -1) or -1) >= 2)
                       or (not malware and int(e.get("vt_detection", -1) or -1) == 0)})
    all_dates = generate_dates_in_interval_monthly(start_date, end_date)
    if use_crawl_date:
        all_shas_and_date = [(sha, parse_date(gp_dict[sha]["crawl_date"], day=1)) for sha in all_shas]
    elif use_vt:
        all_shas_and_date = [(sha, parse_date(vt_date_dict[sha.lower()], day=1))
                             for sha in all_shas if sha.lower() in vt_date_dict]
        print(f"not found in vt_dict {len(all_shas) - len(all_shas_and_date)}")
    else:
        all_shas_and_date = [(sha, parse_date(gp_dict[sha]["gp_date"], day=1)) for sha in all_shas]

    distribution = []
    for _date in all_dates:
        month_distribution = []
        for sha, sample_date in all_shas_and_date:
            if _date == sample_date:
                month_distribution.append(1)
            else:
                month_distribution.append(0)
        distribution.append(month_distribution)

    return np.asarray(distribution)


def _get_package_names_dict(gp_meta_data_path, gp_dict, vt_dict, start_date, end_date):
    start_date, end_date = parse_date(start_date, day=1), parse_date(end_date, day=1)
    hash_to_package, all_packages = {}, set()
    with jsonlines.open(gp_meta_data_path) as reader:
        for line in reader:
            if "sha256s" in line["related_apks_in_AZ_info"]:
                package_name = line["pkg_name"]
                for sha in line["related_apks_in_AZ_info"]["sha256s"]:
                    if sha.lower() in vt_dict and int(gp_dict.get(sha.lower(), {}).get("vt_detection", -1) or -1) == 0:
                        gp_date = parse_date(gp_dict.get(sha.lower(), {}).get("gp_date", "1-1-1990"), day=1)
                        if start_date <= gp_date <= end_date:
                            hash_to_package[sha.lower()] = package_name
                            all_packages.add(package_name)

    return hash_to_package, sorted(all_packages)


def make_semi_random_distribution(vector_1):
    random_distribution = np.zeros_like(vector_1)
    for index, month in enumerate(vector_1[:-1]):
        for sha_index, value in enumerate(month):
            if value == 1:
                random_index = random.randint(index + 1, random_distribution.shape[0] - 1)
                random_distribution[random_index, sha_index] = 1
    for index, element in enumerate(vector_1[-1]):
        if element == 1 and random.random() < 0.5:
            random_distribution[-1][index] = 1

    return random_distribution


def _check_date(_date, sample_hash, gp_entry, vt_date_dict, use_vt, use_crawl_date):
    if use_crawl_date:
        return parse_date(gp_entry.get("crawl_date", "1-1-1990"), day=1) == _date
    if use_vt:
        return parse_date(vt_date_dict.get(sample_hash, "1-1-1990"), day=1) == _date

    return parse_date(gp_entry.get("gp_date", "1-1-1990"), day=1) == _date

