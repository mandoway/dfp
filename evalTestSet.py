import pickle
from pathlib import Path
from datetime import datetime

from tqdm import tqdm

from dfp_main import patch, PatchStats, setVerbose

TEST_SET_PATH = "testSet"
# How many test files should be examined [0,100]
LIMIT = None


def evaluateTestSet():
    testFiles = list(Path(TEST_SET_PATH).iterdir())
    testPairs = [(testFiles[i], testFiles[i + 1]) for i in range(0, len(testFiles), 2)]

    all_stats = []
    for dockerfile, violationFile in tqdm(testPairs[:LIMIT]):
        stats = patch(str(dockerfile), str(violationFile), "hadolint.exe", quiet=True)

        all_stats.append(stats)

    for s in all_stats:
        print(s)

    with open(f"evalStats_{datetime.now().strftime('%d%m%Y_%H%M')}.pkl", "wb") as f:
        pickle.dump(all_stats, f, protocol=pickle.HIGHEST_PROTOCOL)

    times = list(map(lambda it: it.time, all_stats))
    avg_time = sum(times) / len(times)

    total = sum(map(lambda it: it.total, all_stats))
    fixed = sum(map(lambda it: it.fixed, all_stats))
    unfixed = sum(map(lambda it: it.unfixed, all_stats))

    verified_patches = [p for stat in all_stats for p in stat.patches]
    position_dist = {}
    rule_dist = {}
    for p in verified_patches:
        if p.position not in position_dist:
            position_dist[p.position] = 0
        position_dist[p.position] += 1

        if p.rule not in rule_dist:
            rule_dist[p.rule] = 0
        rule_dist[p.rule] += 1

    setVerbose(True)
    PatchStats(total, fixed, unfixed).print()
    print(f"Average time: {avg_time}s")
    print(f"Position distribution: {position_dist}")
    print(f"Rule distribution: {rule_dist}")


if __name__ == "__main__":
    evaluateTestSet()
