import os
from timeit import default_timer as timer

import click
from tqdm import tqdm

from dfp.query.query import findPatches
from dfp.violation_util import getViolations
from linter import linter
from msr18model import Violation

# How many patches are tried (None = all found)
PATCH_LIMIT = 300
VERBOSE = True
# Default blacklist of words which are not patched
DEFAULT_PATCH_BLACKLIST = {
    # Package Managers
    "apt-get",
    "pip",
    "yum",
    "npm",
    "apk",
    "conda",
    # Keywords
    "update",
    "install",
    # Other Executables
    "curl",
    "wget",
    "git",
    "rm",
    # Docker instructions
    "RUN"
}


class PatchStats:
    def __init__(self, total: int, fixed: int = 0, unfixed: int = 0, patches=None):
        if patches is None:
            patches = []
        self.total = total
        self.fixed = fixed
        self.unfixed = unfixed
        self.patches = patches
        self.time = None

    def print(self):
        _print(f"Time: {self.time} s")
        _print(f"Total: {self.total}")
        _print(f"Fixed: {self.fixed}")
        _print(f"Not fixed: {self.unfixed}")
        for i, found_patch in enumerate(self.patches):
            _print(f"Patch {i}: {found_patch}")

    def __repr__(self):
        return str(self.__dict__)


class VerifiedPatch:
    def __init__(self, before: str, after: str, line: int, rule: str, position: int):
        self.before = before
        self.after = after
        self.line = line
        self.rule = rule
        self.position = position

    def __repr__(self):
        return f"Line {self.line} ({self.rule}): {self.before}   --->   {self.after}"


@click.command()
@click.argument("dockerfile", type=click.Path(exists=True))
@click.option("-l", "--linter-results", "violations_file", type=click.Path(exists=True))
@click.option("-hp", "--hadolint-path", "hadolint_path", type=click.Path(exists=True), default="hadolint.exe")
@click.option("-q", "--quiet", is_flag=True)
@click.option("-pl", "--patch-limit", type=click.INT)
def patch_command(dockerfile: str, violations_file: str, hadolint_path: str, quiet: bool, patch_limit: int):
    patch(dockerfile, violations_file, hadolint_path, quiet, patch_limit)


def patch(dockerfile: str, violations_file: str, hadolint_path: str, quiet: bool = not VERBOSE,
          limit: int = PATCH_LIMIT, blacklist: set[str] = None):
    if blacklist is None:
        blacklist = DEFAULT_PATCH_BLACKLIST
    global VERBOSE
    VERBOSE = not quiet

    violations = getViolations(dockerfile, violations_file, hadolint_path)

    _print(f"Number of violations: {len(violations)}")

    with open(dockerfile, "r", encoding="utf-8") as f:
        docker_lines = [line.strip() for line in f.readlines()]

    stats = PatchStats(total=len(violations))
    start = timer()
    for i, violation in enumerate(violations):
        # line is 1-based, but list index is 0-based
        index = int(violation.line) - 1
        if index >= len(docker_lines):
            # the violation line can be greater than the lines in the file for some reason
            continue
        affected_line = docker_lines[index]

        # Querying the patch database
        _print(f"Searching for patches for line ({violation.rule}): {affected_line}")
        patches = findPatches(affected_line, limit=limit, patch_blacklist=blacklist)

        # Try to apply all patches found
        fixed = False
        iterator = tqdm(enumerate(patches[:limit]), desc=f"Trying patches for violation {i}: ") if VERBOSE \
            else enumerate(patches[:limit])

        for pos, ranked_patch in iterator:
            patched_line = ranked_patch.apply(affected_line)

            if verifyFix(docker_lines, patched_line, violation, violations, hadolint_path):
                # Violation was fixed!
                fixed = True
                stats.fixed += 1
                stats.patches.append(
                    VerifiedPatch(affected_line, patched_line, int(violation.line), violation.rule, pos)
                )
                if VERBOSE:
                    iterator.close()
                break

        if not fixed:
            _print("No patches found")
            stats.unfixed += 1

    end = timer()
    stats.time = end - start
    _print("Done with patch process!")
    stats.print()

    return stats


def verifyFix(docker_lines: list[str], patched_line: str, violation: Violation, old_violations: list[Violation],
              hadolint_path: str) -> bool:
    """
    Verify if a patch did actually remove the violation.
    It only removes the violation when it is no longer present, no new violation was introduced and the file contains no
    syntax errors.

    :param docker_lines: lines of the dockerfile
    :param patched_line: line where a patch was applied
    :param violation: the violation which is possibly removed
    :param old_violations: all violations before the patch
    :param hadolint_path: path of linter executable
    :return: whether the patch was successful or not
    """

    new_docker_lines = docker_lines.copy()
    new_docker_lines[int(violation.line) - 1] = patched_line

    dockerfile = os.linesep.join(new_docker_lines)
    new_violations = linter.lintString(dockerfile, hadolint_path)
    is_violation_gone = violation not in new_violations and len(new_violations) < len(old_violations)
    has_no_syntax_error = len(list(filter(lambda it: it.rule == "unexpected", new_violations))) == 0

    return is_violation_gone and has_no_syntax_error


def _print(msg):
    if VERBOSE:
        print(msg)


def setVerbose(v: bool):
    global VERBOSE
    VERBOSE = v


if __name__ == "__main__":
    patch_command()
