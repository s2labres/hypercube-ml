import os.path
import pickle
from argparse import ArgumentParser
from datetime import date

import matplotlib.pyplot as plt
import numpy as np


COLORS = {
    "Transcendent": ["#011f4b", "#005b96", "#6497b1", "#b3cde0"],
    "APIGraph": ["#a70000", "#ff0000", "#ff7b7b", "#ffbaba"],
    "transcend": ["#011f4b", "#005b96", "#6497b1", "#b3cde0"],
    "Transcend": ["#011f4b", "#005b96", "#6497b1", "#b3cde0"],
    "apigraph": ["#a70000", "#ff0000", "#ff7b7b", "#ffbaba"]
}


def plot_f1s(results_dir, model_name, dataset_name, save_path):
    plt.rc("text", usetex=True)
    plt.rc("font", family="serif")
    plt.rc("font", serif=["Computer Modern Serif"])
    figure, ax = plt.subplots()

    results_by_year = load_results(results_dir, model_name, dataset_name)
    results_by_year = get_results_by_year(results_by_year)

    all_dates = get_all_distinct_dates(results_by_year)
    all_dates.append(date(2018, 12, 31))
    dates_to_x = {_date: index for index, _date in enumerate(all_dates)}
    sorted_years = get_all_years_sorted(results_by_year)

    for year, color in zip(sorted_years, COLORS[dataset_name]):
        results = results_by_year[str(year)]
        dates = [p[0] for p in results]
        dates_xs = [dates_to_x[d] for d in dates]
        f1_scores = np.asarray([p[1]["f1"] for p in results])
        label = f"{get_dataset_name(dataset_name)} [{year}]"
        ax.plot(dates_xs, f1_scores, '-', color=color, label=label, marker='o')
        ax.plot(
            [dates_to_x[dates[0]], dates_to_x[dates[0]]], [0, 1.0],
            color=color, linestyle='--'
        )

    ax.set_ylabel("$F_1$-Score", fontsize=30)
    dates_to_show = ["1-2015", "1-2016", "1-2017", "1-2018", "12-2018"]
    if isinstance(list(dates_to_x.keys())[0], str):
        date_objs_to_show = ["1-2015", "1-2016", "1-2017", "1-2018", "12-2018"]
    else:
        date_objs_to_show = [date(2015, 1, 1), date(2016, 1, 1), date(2017, 1, 1), date(2018, 1, 1), date(2018, 12, 31)]
    ax.set_xticks(np.asarray([dates_to_x[d] for d in date_objs_to_show]), dates_to_show, rotation=45, fontsize=30)
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0], fontsize=30)
    plt.ylim(0.0, 1.0)

    ax.grid()
    ax.legend(fontsize=18, loc="lower left")
    # ax.legend(fontsize=16, loc="upper center")
    figure.tight_layout()
    figure.savefig(save_path)
    plt.show()


def load_results(results_dir, model_name, dataset_name):
    results_by_year = {}
    for year_dir in os.scandir(os.path.join(results_dir, model_name, dataset_name)):
        try:
            with open(os.path.join(year_dir, f"f1_per_month.pickle"), 'rb') as infile:
                results_by_year[year_dir.name] = pickle.load(infile)
        except FileNotFoundError:
            with open(os.path.join(year_dir, f"time_aware_evaluations.pickle"), 'rb') as infile:
                results_by_year[year_dir.name] = pickle.load(infile)
    return results_by_year


def get_dataset_name(dataset_name):
    if "apigraph" in dataset_name.lower():
        return "$\mathcal{D}_{A}$"
    elif "transcend" in dataset_name.lower():
        return "$\mathcal{D}_{T}$"
    else:
        raise NameError(f"unknown dataset {dataset_name}")


def get_results_by_year(results_by_year):
    results_by_year_sorted = {}
    for year, results_by_year in results_by_year.items():
        results_list = [(_date, value) for _date, value in results_by_year.items()]
        if isinstance(results_list[0][0], str):
            results_list.sort(key=lambda x: date(year=int(x[0].split("-")[1]), month=int(x[0].split("-")[0]), day=1))
        else:
            results_list.sort(key=lambda p: p[0])
        results_by_year_sorted[year] = results_list

    return results_by_year_sorted


def get_all_distinct_dates(results_by_year):
    all_dates = set()
    for year, results in results_by_year.items():
        for result in results:
            all_dates.add(result[0])
    all_dates = list(all_dates)
    if isinstance(all_dates[0], str):
        all_dates.sort(key=lambda x: date(year=int(x.split("-")[1]), month=int(x.split("-")[0]), day=1))
    else:
        all_dates.sort()
    return all_dates


def get_all_years_sorted(results_by_year):
    all_years = {int(year) for year in results_by_year}
    all_years = list(all_years)
    all_years.sort()

    return all_years


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument("model_name", choices=["DrebinSVM", "DeepDrebin", "RAMDA", "MalScan", "HCC"])
    argument_parser.add_argument("dataset_name", choices=["APIGraph", "Transcendent"])
    argument_parser.add_argument("--results-dir", default="evaluation_results/temporal_luck/motivational/")
    args = argument_parser.parse_args()
    os.makedirs(args.results_dir, exist_ok=True)
    _save_path = f"experiment_outputs/temporal_luck/motivational_{args.model_name}_{args.dataset_name}_plot.svg"
    plot_f1s(args.results_dir, args.model_name, args.dataset_name, _save_path)
