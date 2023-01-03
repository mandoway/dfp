import csv

import msr18model
from linter import linter


def getViolations(dockerfile: str, violations_file: str) -> list[msr18model.Violation]:
    if violations_file is None:
        violations = linter.lintFile(dockerfile)
    else:
        with open(violations_file, "r", newline="") as f:
            if violations_file.endswith(".csv"):
                reader = csv.DictReader(f)
                violations = list(
                    map(lambda l: msr18model.Violation(line=l["line"], rule=l["rule"], level=l["level"]), reader)
                )
            else:
                lines = filter(lambda x: x.count(" ") >= 2, f.readlines())
                violations = list(map(linter.mapLineToViolation, lines))
    return violations
