import os
import pickle
import sys

import latextable as latextable
import matplotlib.pyplot as plt
import pandas as pd
from texttable import Texttable

from dfp_main import PatchStats

DEBUG_POS_DICT = {217: 9, 0: 240, 11: 3, 238: 6, 225: 16, 1: 51, 2: 13, 41: 2, 44: 2, 86: 3, 6: 3, 87: 5, 4: 21, 26: 5,
                  39: 3,
                  28: 1, 5: 15, 10: 5, 113: 2, 62: 2, 50: 3, 216: 3, 12: 5, 218: 3, 24: 8, 20: 4, 83: 2, 72: 3, 15: 2,
                  23: 2,
                  134: 6, 22: 3, 105: 3, 19: 3, 154: 1, 8: 6, 75: 1, 219: 3, 52: 4, 76: 3, 33: 8, 158: 4, 137: 4, 34: 2,
                  7: 13, 79: 2, 3: 2, 48: 6, 160: 1, 40: 1, 84: 6, 211: 8, 159: 1, 69: 3, 90: 4, 118: 4, 16: 2, 17: 1,
                  133: 2}
DEBUG_RULE_DICT = {'DL3008': 71, 'DL3009': 33, 'DL3015': 71, 'DL4000': 60, 'DL3005': 9, 'SC2086': 3, 'DL4006': 20,
                   'DL3020': 62, 'DL3007': 6, 'DL3013': 25, 'DL3042': 31, 'SC2028': 1, 'DL3003': 39, 'DL4001': 7,
                   'DL3025': 16, 'DL4003': 2, 'DL3006': 17, 'DL3010': 6, 'DL3032': 8, 'DL3033': 7, 'DL3004': 7,
                   'DL3001': 1,
                   'DL3018': 7, 'SC2155': 1, 'SC2164': 5, 'DL3028': 2, 'DL3014': 3, 'SC2039': 1, 'SC1073': 1,
                   'SC1009': 1,
                   'SC1132': 1, 'SC1072': 1, 'SC2046': 2, 'DL3002': 1, 'DL3019': 2, 'SC2016': 12, 'DL3016': 1,
                   'DL3000': 2,
                   'SC2174': 2, 'SC2006': 2}

OUTPUT_NAME = ""


def plotRules(rules: dict[str, int], title: str):
    print(f"plotRules ({title}): ")
    sorted_rules = sorted(rules.items(), key=lambda it: it[1], reverse=True)
    print(sorted_rules)
    x, y = zip(*sorted_rules)

    plt.figure(figsize=(20, 6))
    plt.title(title)
    plt.bar(x, y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_NAME + "_RuleDistribution.png")
    plt.show()
    print()


def tablePositions(positions: dict[int, int]):
    bins = [1, 5, 10, 25, 50, 100]
    rows = []
    for bin_ in bins:
        rows.append(
            [bin_, sum(map(lambda it: it[1], filter(lambda it: it[0] + 1 <= bin_, positions.items())))]
        )
    rows.append(
        ["All", sum(map(lambda it: it[1], positions.items()))]
    )

    total = rows[-1][1]
    x = bins + [total]
    y = list(map(lambda it: it[1], rows))
    plt.figure()
    plt.plot(x, y)
    plt.title("Impact of patch limit to fixes")
    plt.xlabel("maximum patches allowed")
    plt.ylabel("fixes found")
    plt.savefig(OUTPUT_NAME + "_PatchLimitImpact.png")
    plt.show()

    table = Texttable()
    table.set_deco(Texttable.HEADER | Texttable.VLINES)
    table.set_cols_align(["c", "c"])
    table.add_rows([
        ["Top-n", "Count"],
        *rows
    ], header=True)
    print(table.draw() + "\n")
    print(latextable.draw_latex(table, caption="An example table.", label="tab:positions") + "\n")


def plotTimes(total_times: list[float], times_per_v: list[float]):
    print("plotTimes")
    fig, ax = plt.subplots()
    ax.set_title("Execution times")

    ax.set_ylabel("total in s")
    result = ax.boxplot(total_times, showfliers=False, positions=[1])
    print(f"total median: {result['medians'][0].get_ydata()}")

    ax2 = ax.twinx()
    ax2.set_ylabel("per violation in s")
    result = ax2.boxplot(times_per_v, showfliers=False, positions=[2])
    print(f"per viol median: {result['medians'][0].get_ydata()}")

    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Total", "Per violation"])
    plt.savefig(OUTPUT_NAME + "_ExecutionTimes.png")
    plt.show()
    print()


def readTestSetStats() -> dict[str, int]:
    print("readTestSet:")
    folder = "testSet"
    rules = {}
    num_violations = []
    for file in sorted(os.listdir(folder)):
        if file.endswith(".csv"):
            data = pd.read_csv(f"{folder}/{file}")
            num_violations.append(len(data))
            for rule in data.rule.tolist():
                if rule not in rules:
                    rules[rule] = 0
                rules[rule] += 1

    print(f"Avg number of violations in test set: {sum(num_violations) / len(num_violations)}")
    print(f"Min violations: {min(num_violations)}")
    print(f"Max violations: {max(num_violations)}")
    print(f"Total violations: {sum(num_violations)}")
    print()
    return rules


def plotRulesVsTotal(rules: dict[str, int], total: dict[str, int]):
    print("fixedVsTotal:")
    percents = {}
    for k, v in total.items():
        if k in rules:
            percents[k] = rules[k] / v * 100
        else:
            percents[k] = 0

    sorted_rules = sorted(percents.items(), key=lambda it: it[1], reverse=True)
    print(f"Sorted rules = {sorted_rules}")
    x, y = zip(*sorted_rules)
    rest = [100 - val for val in y]

    plt.figure(figsize=(20, 6))
    plt.title("Fix rate of rule violations")
    plt.bar(x, y)
    plt.bar(x, rest, bottom=y, color="r")
    plt.ylabel("Fixed violations (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_NAME + "_FixRate.png")
    plt.show()
    print()


def main():
    global OUTPUT_NAME

    if len(sys.argv) < 2:
        print("Please provide a result file, e.g. results.pkl")
        return

    results_file = sys.argv[1]
    OUTPUT_NAME += results_file.removesuffix(".pkl")

    with open(results_file, "rb") as f:
        results: list[PatchStats] = pickle.load(f)

    rule_list_file = results_file.removesuffix(".pkl") + "_rules.txt"
    if not os.path.exists(rule_list_file):
        with open(rule_list_file, "w") as f:
            for r in results:
                f.writelines(list(map(lambda it: str(it) + "\n", r.patches)))
                f.write("\n")

    times = list(map(lambda it: it.time, results))
    avg_time = sum(times) / len(times)

    times_per_violation = list(map(lambda it: it.time / it.total, results))
    avg_time_per_violation = sum(times_per_violation) / len(times_per_violation)

    verified_patches = [p for stat in results for p in stat.patches]
    position_dist = {}
    rule_dist = {}
    for p in verified_patches:
        if p.position not in position_dist:
            position_dist[p.position] = 0
        position_dist[p.position] += 1

        if p.rule not in rule_dist:
            rule_dist[p.rule] = 0
        rule_dist[p.rule] += 1

    testSet = readTestSetStats()
    # plotRules(rule_dist, "Fixed violations")
    plotRules(testSet, "Violations in test data set")
    plotTimes(times, times_per_violation)
    plotRulesVsTotal(rule_dist, testSet)
    tablePositions(position_dist)


if __name__ == "__main__":
    main()
