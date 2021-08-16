import re
from typing import Tuple, Optional

import tqdm
from sqlalchemy.orm import Session

from dbHelper import initSessionMaker
from dfp.DockerInstruction import DockerInstruction
from dfp.model.Patch import Patch2, PARAM_MATCHER
from dfp.training_set import readTrainingSet, augmentTrainingSet, filterDeletingChanges
from dfp.util import getListElemWithDefault
from msr18model import FixChange


def extractPatches():
    """
    Loads changes from MSR18 DB and maps them to Patches for DFP DB.
    Saves all changes to DFP DB.
    """
    training_set = loadTrainingSet()
    patches = mapTrainingSetToPatches(training_set)

    print("Adding created patches to dfp database (can take several minutes)")
    dfp_session: Session = initSessionMaker("dfp")()
    dfp_session.add_all(patches)
    dfp_session.commit()
    dfp_session.close()
    print("Done!")


def loadTrainingSet() -> list[FixChange]:
    """
    Loads the changes for training the patch database.
    Training set is all changes minus the test set found in a csv file specified in training_set.py
    Also augments the training set with additional changes according to heuristics defined in training_set.py
    :return: changes from db + augmented changes
    """
    print("Reading training set...")
    training_set = readTrainingSet()
    training_set_len = len(training_set)
    print(f"> Done, found {training_set_len} changes")

    print("Augmenting training set...")
    augmentTrainingSet(training_set)
    print(f"> Done, added {len(training_set) - training_set_len} changes, total {len(training_set)}")

    print("Removing only deleting changes...")
    training_set = filterDeletingChanges(training_set)
    print(f"> Done, total length: {len(training_set)}")

    return training_set


def isChangeFullCmd(change: FixChange) -> bool:
    """
    A change is a "full command change" when the change type ends with the instruction name
    e.g. UpdateType_RUN is a full command change, UpdateType_PARAMETER is not
    :param change: change to check
    :return: if the change contains the full cmd or not
    """
    change_suffix = change.change_type[change.change_type.index("_") + 1:]

    return change_suffix in _getFullCmdSuffixes()


def _getFullCmdSuffixes() -> set[str]:
    # every change ending with a docker instruction contains the full line change
    full_cmd_names = set(DockerInstruction.names())
    # comments are represented with an artificial instruction called COMMENT
    full_cmd_names.add("COMMENT")
    # For ADD or COPY, these changes still contain the full line
    full_cmd_names.add("DESTINATION")
    full_cmd_names.add("SOURCE")

    return full_cmd_names


def mapTrainingSetToPatches(training_set: list[FixChange]) -> list[Patch2]:
    """
    Maps all changes from MSR18 DB to Patches in DFP DB
    :param training_set: list of FixChange objects to create Patches for
    :return: input mapped to Patch objects
    """
    patches = []

    for change in tqdm.tqdm(training_set, desc="Mapping changes to patches"):
        if change.instruction == "" and change.executable == "":
            # Special case: change was added in augmentation function
            # instruction and/or executable changed
            before_parts = splitParamString(change.before)
            after_parts = splitParamString(change.after)
            instruction_before = before_parts[0]
            instruction_after = after_parts[0]

            is_run = instruction_before == DockerInstruction.RUN.name

            executable_before = before_parts[1] if is_run else None
            executable_after = after_parts[1] if is_run else None

            start_index = 2 if is_run else 1
            before_change = ' '.join(before_parts[start_index:])
            after_change = ' '.join(after_parts[start_index:])

            before, after = getPatternStrings(instruction_before, instruction_after,
                                              executable_before, executable_after,
                                              before_change, after_change,
                                              is_full_cmd=True)
            is_combinable = isCombinable(instruction_before, is_full_cmd=True)

            patches.append(
                Patch2(
                    before=before,
                    after=after,
                    is_combinable=is_combinable,
                    single_transform=None,
                    group_transform=None
                )
            )
        else:
            is_full_cmd = isChangeFullCmd(change)
            before, after = getPatternStringsFromChange(change, is_full_cmd)
            is_combinable = isCombinable(change.instruction, is_full_cmd)

            patches.append(
                Patch2(
                    before=before,
                    after=after,
                    is_combinable=is_combinable,
                    single_transform=None,
                    group_transform=None
                )
            )

    return patches


def getPatternStringsFromChange(change: FixChange, is_full_cmd: bool) -> Tuple[str, str]:
    return getPatternStrings(change.instruction, change.instruction,
                             change.executable, change.executable,
                             change.before, change.after,
                             is_full_cmd)


def getPatternStrings(before_instruction: str, after_instruction: str,
                      before_executable: Optional[str], after_executable: Optional[str],
                      before_change: str, after_change: str,
                      is_full_cmd: bool) -> Tuple[str, str]:
    before, after = before_instruction, after_instruction

    if after_instruction == DockerInstruction.RUN.name and before_executable is not None:
        before += f" {re.escape(before_executable)}"
        after += f" {re.escape(after_executable)}"

    before += PARAM_MATCHER
    after += PARAM_MATCHER

    if is_full_cmd:
        before_parts = splitParamString(before_change)
        after_parts = splitParamString(after_change)

        max_len = max(len(before_parts), len(after_parts))
        is_param_matcher = False
        found_change = False
        for i in range(max_len):
            before_param = getListElemWithDefault(before_parts, i, "")
            after_param = getListElemWithDefault(after_parts, i, "")

            if before_param != "" and before_param == after_param:
                is_param_matcher = True
            else:
                if is_param_matcher and found_change:
                    before += PARAM_MATCHER
                    after += PARAM_MATCHER
                    is_param_matcher = False

                found_change = True

                new_before, new_after = getChanges(before_param, after_param, after_instruction)
                before += new_before
                after += new_after
    else:
        new_before, new_after = getChanges(before_change, after_change, after_instruction)
        before += new_before
        after += new_after

    before += PARAM_MATCHER
    after += PARAM_MATCHER

    return before, after


def getChanges(before_change: str, after_change: str, after_instruction: str):
    if after_instruction == DockerInstruction.FROM.name:
        # Parameters are likely image + version. Version can represented as 0.0 in the MSR18 DB when it was invalid
        # So we remove the :0.0 or : suffix to extract correct patches
        before_change = before_change.removesuffix(":0.0")
        before_change = before_change.removesuffix(":")
        after_change = after_change.removesuffix(":0.0")
        after_change = after_change.removesuffix(":")

    before = f" {before_change}" if before_change is not None and before_change != "" else ""
    after = f" {after_change}"
    return re.escape(before), re.escape(after)


def isCombinable(instruction: str, is_full_cmd: bool):
    """
    A Patch is only combinable with other patches, if it doesn't change the full cmd
    and the instruction is RUN (other instructions don't really benefit from this)
    """
    return instruction == DockerInstruction.RUN.name and not is_full_cmd


def splitParamString(param_str: str) -> list[str]:
    """
    Splits parameter strings from the MSR18 database.
    The strings are sometimes delimited with ¦ and sometimes with whitespace,
    therefore this function

    :param param_str: string containing parameters delimited with ¦ or whitespace
    :return: list of parameters
    """
    return (param_str or "").replace("¦", " ").split()


if __name__ == "__main__":
    extractPatches()
