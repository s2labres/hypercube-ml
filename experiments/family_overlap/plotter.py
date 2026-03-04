import numpy as np
import matplotlib.pyplot as plt


def plot(results_list, std_list, labels_list, colors_list, hatches_list, years_list, save_path):

    plt.rc("text", usetex=True)
    plt.rc("font", family="serif")
    plt.rc("font", serif=["Computer Modern Serif"])

    x_ticks = np.arange(0, len(years_list) * 2.5, 2.5)
    width = 0.5

    fig, ax = plt.subplots(layout='constrained')
    print(results_list)
    center_multiplier = 1
    bars_to_the_left = len(results_list) // 2
    if (len(results_list) % 2) == 0:
        bars_to_the_left -= 0.5
    bars_to_the_left *= -1
    print("results list", results_list)

    for results, stds, label, color, hatch in zip(results_list, std_list, labels_list, colors_list, hatches_list):
        print(center_multiplier, bars_to_the_left)
        ax.bar(
            x_ticks + center_multiplier * bars_to_the_left * width,
            results, width, yerr=stds, color=color, label=label, hatch=hatch
        )
        bars_to_the_left += 1

    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], ["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=20)
    ax.set_ylabel("\% Family Overlap w/ Training", fontsize=15)

    ax.set_xticks(x_ticks, years_list, rotation=45, fontsize=20)

    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18),
    #           fancybox=True, shadow=True, ncol=2, fontsize=16)
    ax.legend(loc='upper center', bbox_to_anchor=(1.15, 0.6),
              fancybox=True, shadow=True, ncol=1, fontsize=15)
    # fig.tight_layout()
    fig.savefig(save_path)
    plt.show()
