from collections import defaultdict

from android_malware_detectors.utils import load_json

from experiments.family_overlap.overlap_computer import compute_all_overlaps
from experiments.family_overlap.plotter import plot


def compute_family_overlaps(meta_files_by_group, families_db_file, is_azoo, date_type):
    meta_files_by_group = filter_out_goodware(meta_files_by_group)
    overlaps_by_group, stds_by_group = {}, {}
    for group, meta_files in meta_files_by_group.items():
        print("GROUP", group)
        _date_type = date_type
        if isinstance(date_type, dict):
            _date_type = date_type[group]
        average_overlaps_by_year, std = compute_all_overlaps(meta_files, families_db_file, is_azoo, _date_type)
        overlaps_by_group[group] = average_overlaps_by_year
        stds_by_group[group] = std
    return overlaps_by_group, stds_by_group


def plot_family_overlaps(overlaps_by_group, stds_by_group, save_path, colors=None, hatches=None, order=None):
    if colors is None:
        colors = ["#2E4057", "#98B6B1", "#FBDCE2", "#B24C63", "#C1666B"]
    if hatches is None:
        hatches = [None] * 10
    results_list, std_list, labels_list, colors_list, years_list = [], [], [], [], []
    if order is None:
        iterator = overlaps_by_group.items()
    else:
        iterator = [(group, overlaps_by_group[group]) for group in order]
    for group, overlaps_by_year in iterator:
        results_list.append(get_overlaps_sorted(overlaps_by_year))
        std_list.append(get_overlaps_sorted(stds_by_group[group]))
        labels_list.append(f"$\mathcal{{D}}_{group}$")
        years_list = sorted(list(overlaps_by_year))
    plot(results_list, std_list, labels_list, colors, hatches, years_list, save_path)


def filter_out_goodware(meta_files_dict):
    filtered_out_metas = defaultdict(list)
    for group, meta_files in meta_files_dict.items():
        for meta_file in meta_files:
            meta = load_json(meta_file)
            if isinstance(meta, list):
                meta = {e["sha256"].lower(): e for e in meta}
            new_meta = {h: e for h, e in meta.items() if e.get("vt_detection") and int(e["vt_detection"]) > 0}
            filtered_out_metas[group].append(new_meta)
    return filtered_out_metas


def get_overlaps_sorted(overlaps_by_year):
    overlap_tuples = [(year, overlap) for year, overlap in overlaps_by_year.items()]
    overlap_tuples.sort(key=lambda x: x[0])
    print(overlap_tuples)
    overlap_list = [t[1] for t in overlap_tuples]
    return overlap_list
