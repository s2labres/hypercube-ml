from dtw import dtw
from android_malware_detectors.utils.io_operations import load_json
from android_malware_detectors.datasets_utils.dates import parse_date

from experiments.timestamps.experiment_2.distribution_encoder import (make_monthly_distribution_by_sha,
                                                                      make_semi_random_distribution)


def norm_by_sha(gp_path, vt_date_path, start_date, end_date, malware):
    gp_dict, vt_date_dict, start_date, end_date = _preprocess_inputs(gp_path, vt_date_path, start_date, end_date)

    gp_distribution = make_monthly_distribution_by_sha(gp_dict, start_date, end_date, malware=malware,
                                                       vt_date_dict=vt_date_dict, use_vt=False, use_crawl_date=False)
    vt_distribution = make_monthly_distribution_by_sha(gp_dict, start_date, end_date, malware=malware,
                                                       vt_date_dict=vt_date_dict, use_vt=True, use_crawl_date=False)
    azoo_distribution = make_monthly_distribution_by_sha(gp_dict, start_date, end_date, malware=malware,
                                                         vt_date_dict=vt_date_dict, use_vt=False, use_crawl_date=True)

    gp_vt_distance = dtw(gp_distribution, vt_distribution).normalizedDistance
    gp_azoo_distance = dtw(gp_distribution, azoo_distribution).normalizedDistance
    random_norms = dtw(gp_distribution, make_semi_random_distribution(gp_distribution)).normalizedDistance

    gp_vt_distance_normalized = gp_vt_distance / random_norms
    gp_azoo_distance_normalized = gp_azoo_distance / random_norms

    return gp_vt_distance, gp_azoo_distance, random_norms, gp_vt_distance_normalized, gp_azoo_distance_normalized


def _preprocess_inputs(gp_path, vt_date_path, start_date, end_date):
    start_date, end_date = parse_date(start_date), parse_date(end_date)
    vt_date_dict = load_json(vt_date_path)
    gp_dict = {h: e for h, e in load_json(gp_path).items()
               if h.lower() in vt_date_dict
               and start_date <= parse_date(e.get("gp_date", "1-1-1990"), day=1) <= end_date
               and start_date <= parse_date(e.get("crawl_date", "1-1-1990"), day=1) <= end_date}

    return gp_dict, vt_date_dict, start_date, end_date
