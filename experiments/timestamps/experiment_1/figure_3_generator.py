from experiments.family_overlap.plot_family_overlap import compute_family_overlaps, plot_family_overlaps


if __name__ == '__main__':
    _save_path = "experiment_outputs/timestamps/figure_3.svg"
    _families_db_file = "data/all_families_db.json"
    _date_type = "dex_date"
    _meta_files_by_group = {
        "T": ["data/meta_files/transcend_meta.json"],
        "{T}^{2019}": ["data/timestamps/experiment_1/transcend_emulation/meta_1.json",
                       "data/timestamps/experiment_1/transcend_emulation/meta_2.json",
                       "data/timestamps/experiment_1/transcend_emulation/meta_3.json",
                       "data/timestamps/experiment_1/transcend_emulation/meta_4.json",
                       "data/timestamps/experiment_1/transcend_emulation/meta_5.json"],
        "{T}^{2025}": ["data/timestamps/experiment_1/transcend_sampled_today/meta_1.json",
                       "data/timestamps/experiment_1/transcend_sampled_today/meta_2.json",
                       "data/timestamps/experiment_1/transcend_sampled_today/meta_3.json",
                       "data/timestamps/experiment_1/transcend_sampled_today/meta_4.json",
                       "data/timestamps/experiment_1/transcend_sampled_today/meta_5.json"]
    }
    overlaps, std = compute_family_overlaps(_meta_files_by_group, _families_db_file, False, _date_type)
    plot_family_overlaps(overlaps, std, _save_path, order=["{T}^{2025}", "{T}^{2019}", "T"],
                         colors=["#135a94", "#3182c4", "#1999FF"], hatches=['/', '/', None])
