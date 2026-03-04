from experiments.temporal_luck.motivational.train_models import train_all_models


if __name__ == '__main__':
    classifiers_list = ["DrebinSVM", "DeepDrebin", "HCC", "RAMDA", "MalScan"]
    datasets = ["APIGraph", "Transcendent"]
    datasets_paths = ["data/datasets/apigraph/apigraph_drebin.json",
                      "data/datasets/transcendent/transcendent_drebin.json",
                      "data/datasets/apigraph/apigraph_drebin.json",
                      "data/datasets/transcendent/transcendent_drebin.json",
                      "data/datasets/apigraph/apigraph_drebin.json",
                      "data/datasets/transcendent/transcendent_drebin.json",
                      "data/datasets/apigraph/apigraph_ramda.pickle",
                      "data/datasets/transcendent/transcendent_ramda.pickle",
                      "data/datasets/apigraph/apigraph_malscan.pickle",
                      "data/datasets/transcendent/transcendent_malscan.pickle"]
    meta_paths = ["data/meta_files/apigraph_meta.json", "data/meta_files/transcendent_meta.json"]
    vtts = [15, 4]
    date_types = ["vt_first_submission_date", "dex_date"]
    save_dir = "trained_models/temporal_luck/motivational"
    families = "data/all_families_db.json"
    start_year, end_year = 2014, 2018
    train_all_models(classifiers_list, datasets, datasets_paths, meta_paths, vtts,
                     start_year, end_year, date_types, save_dir, families)
