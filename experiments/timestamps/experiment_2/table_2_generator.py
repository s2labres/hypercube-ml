import os
from collections import defaultdict

import numpy as np
import tqdm
from android_malware_detectors.utils import load_json, dump_json
from android_malware_detectors.datasets_utils.dates import parse_date
from sklearn.metrics.pairwise import cosine_similarity

from experiments.timestamps.experiment_2.distribution_encoder import make_monthly_distribution_by_sha


def norm_by_sha(gp_path, vt_date_path, start_date, end_date, malware):
    gp_dict, vt_date_dict, start_date, end_date = _preprocess_inputs(gp_path, vt_date_path, start_date, end_date)
    gp_distribution = make_monthly_distribution_by_sha(gp_dict, start_date, end_date, malware=malware,
                                                       vt_date_dict=vt_date_dict, use_vt=False, use_crawl_date=False)
    vt_distribution = make_monthly_distribution_by_sha(gp_dict, start_date, end_date, malware=malware,
                                                       vt_date_dict=vt_date_dict, use_vt=True, use_crawl_date=False)
    azoo_distribution = make_monthly_distribution_by_sha(gp_dict, start_date, end_date, malware=malware,
                                                         vt_date_dict=vt_date_dict, use_vt=False, use_crawl_date=True)

    gp_vt_norms = compute_cosine_similarity(gp_distribution, vt_distribution)
    gp_azoo_norms = compute_cosine_similarity(gp_distribution, azoo_distribution)
    return gp_vt_norms, gp_azoo_norms


def _preprocess_inputs(gp_path, vt_date_path, start_date, end_date):
    start_date, end_date = parse_date(start_date), parse_date(end_date)
    vt_date_dict = load_json(vt_date_path)
    gp_dict = {h: e for h, e in load_json(gp_path).items()
               if start_date <= parse_date(e.get("gp_date", "1-1-1990"), day=1) <= end_date
               and start_date <= parse_date(e.get("crawl_date", "1-1-1990"), day=1) <= end_date
               and h.lower() in vt_date_dict}

    return gp_dict, vt_date_dict, start_date, end_date


def compute_cosine_similarity(vector_1, vector_2):
    cosine_similarities = []
    for month_1, month_2 in zip(vector_1, vector_2):
        cosine_similarities.append(cosine_similarity(month_1.reshape(1, -1), month_2.reshape(1, -1)))
    return np.mean(cosine_similarities), np.std(cosine_similarities)


if __name__ == '__main__':
    results_by_year = defaultdict(dict)
    for year in tqdm.tqdm(range(2021, 2024)):
        _gp_vt_norms, _gp_azoo_norms = norm_by_sha("data/unified_gp_metadata.json", "data/apk_vt_timestamps_db.json",
                                                   f"1-1-{year}", f"31-12-{year}", True)
        results_by_year[year]["malware"] = _gp_vt_norms, _gp_azoo_norms
        _gp_vt_norms, _gp_azoo_norms = norm_by_sha("data/unified_gp_metadata.json", "data/apk_vt_timestamps_db.json",
                                                   f"1-1-{year}", f"31-12-{year}", False)
        results_by_year[year]["goodware"] = _gp_vt_norms, _gp_azoo_norms

    dump_json(os.path.join("experiment_outputs/timestamps", "table_2.json"), results_by_year)
