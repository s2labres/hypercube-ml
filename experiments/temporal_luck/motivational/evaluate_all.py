from experiments.temporal_luck.motivational.evaluate_models import evaluate_all_models


if __name__ == '__main__':
    classifiers_list = ["DrebinSVM", "DeepDrebin", "HCC", "RAMDA", "MalScan"]
    classifiers_path_root = "trained_models/temporal_luck/motivational"
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
    save_dir = "evaluation_results/temporal_luck/motivational"
    families = "data/all_families_db.json"
    start_year, end_year = 2014, 2017
    evaluate_all_models(classifiers_list, classifiers_path_root, datasets, datasets_paths, meta_paths,
                        start_year, end_year, date_types, vtts, save_dir)
