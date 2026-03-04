import os
from collections import defaultdict

import tqdm
from android_malware_detectors.utils import dump_json

from experiments.timestamps.experiment_2.dtw import norm_by_sha

if __name__ == '__main__':
    results_by_year = defaultdict(dict)
    for year in tqdm.tqdm(range(2021, 2024)):
        (gp_vt_dtw_distance, gp_azoo_dtw_distance, random_dtw_distance,
         gp_vt_dtw_distance_normalized, gp_azoo_dtw_distance_normalized) = norm_by_sha(
            "data/unified_gp_metadata.json", "data/apk_vt_timestamps_db.json",
            f"1-1-{year}", f"31-12-{year}", True
        )
        results_by_year[year]["malware"] = {
            "vt_first_dates": gp_vt_dtw_distance, "vt_first_dates_normalized": gp_vt_dtw_distance_normalized,
            "crawl_dates": gp_azoo_dtw_distance, "crawl_dates_normalized": gp_azoo_dtw_distance_normalized,
            "random_distribution": random_dtw_distance,
        }
        (gp_vt_dtw_distance, gp_azoo_dtw_distance, random_dtw_distance,
         gp_vt_dtw_distance_normalized, gp_azoo_dtw_distance_normalized) = norm_by_sha(
            "data/unified_gp_metadata.json", "data/apk_vt_timestamps_db.json",
            f"1-1-{year}", f"31-12-{year}", False
        )
        results_by_year[year]["goodware"] = {
            "vt_first_dates": gp_vt_dtw_distance, "vt_first_dates_normalized": gp_vt_dtw_distance_normalized,
            "crawl_dates": gp_azoo_dtw_distance, "crawl_dates_normalized": gp_azoo_dtw_distance_normalized,
            "random_distribution": random_dtw_distance,
        }

    dump_json(os.path.join("experiment_outputs/timestamps", "table_3.json"), results_by_year)
