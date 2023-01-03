import re
import sys
import tempfile
import msr18model
import subprocess
import os
from pathlib import Path


class Linter:

    def __init__(self, dockerfile: msr18model.Dockerfile, commits):
        self.dockerfile = dockerfile
        self.commits = commits

    def computeViolations(self) -> msr18model.Dockerfile:
        for index in range(self.dockerfile.commits):
            self._setViolationsForCommits(index)
        return self.dockerfile

    def _setViolationsForCommits(self, index: int):
        # Dockerfile should be included, if not, then return
        try:
            curfile = list(filter(lambda m: Path(m.new_path) == Path(self.dockerfile.repoDockerPath),
                                  self.commits[index].modified_files))[0]
        except IndexError:
            return

        # File was probably deleted and is ignored
        if curfile.source_code is None:
            return

        violations = lintString(curfile.source_code)

        # Add missing violations if there are already some in the DB
        if len(self.dockerfile.snapshots[index].violations) > 0:
            new_set = set(violations)
            old_set = set(self.dockerfile.snapshots[index].violations)
            added = new_set - old_set
            self.dockerfile.snapshots[index].violations += added
        else:
            self.dockerfile.snapshots[index].violations = violations


def lintString(source: str) -> list[msr18model.Violation]:
    hadolint_path = getDefaultHadolintPath()

    tmp = tempfile.NamedTemporaryFile(dir="", delete=False)
    tmp.write(source.encode())
    tmp.flush()

    proc = subprocess.Popen([hadolint_path, "--no-color", tmp.name], stdout=subprocess.PIPE, text=True)
    out = proc.communicate()[0]

    tmp.close()
    os.unlink(tmp.name)

    lines = out.split("\n")
    lines = filter(lambda x: x.count(" ") >= 2, lines)
    return list(map(mapLineToViolation, lines))


def lintFile(filename: str) -> list[msr18model.Violation]:
    hadolint_path = getDefaultHadolintPath()

    proc = subprocess.Popen([hadolint_path, "--no-color", filename], stdout=subprocess.PIPE, text=True)
    out = proc.communicate()[0]

    lines = out.split("\n")
    lines = filter(lambda x: x.count(" ") >= 2, lines)
    return list(map(mapLineToViolation, lines))


def getDefaultHadolintPath() -> str:
    if sys.platform == "linux":
        return "hadolint"
    else:
        return "hadolint.exe"


def mapLineToViolation(line: str) -> msr18model.Violation:
    split = line.split(" ")

    rule = split[1]

    colsplit = split[0].split(":")
    if "unexpected" in rule:
        line_num = colsplit[-2]
    else:
        line_num = colsplit[-1]

    level = split[2][:-1]
    level = removeANSIColorCodes(level)
    return msr18model.Violation(line=int(line_num), rule=rule, level=level)


def removeANSIColorCodes(color_coded: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', color_coded)
