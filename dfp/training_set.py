from itertools import groupby

import pandas as pd
from sqlalchemy.orm import Session
from tqdm import tqdm

from dbHelper import Sessionmaker
from msr18model import FixChange

PATH_TO_TEST_SET_LIST = "../testSet_28062021.csv"
DEL_PREFIX = "del"
ADD_PREFIX = "add"
UPDATE_TYPE = "UpdateType"


def readTrainingSet() -> list[FixChange]:
    testSetDiffIds: list[str] = pd.read_csv(PATH_TO_TEST_SET_LIST).diff_id.tolist()

    session: Session = Sessionmaker()
    trainingSet: list[FixChange] = session.query(FixChange) \
        .filter(FixChange.diff_id.notin_(testSetDiffIds)) \
        .order_by(FixChange.diff_id) \
        .all()

    session.close()
    return trainingSet


def augmentTrainingSet(data: list[FixChange]):
    """
    Augments the training set by adding fixes based on heuristics:
        1.  Finds pairs of changes where instruction and executable did not change, but the parameters differ.
            If the suffix of the change type is equal, a new change with type Update will be added.

        2.  Finds pairs of changes where nothing but the instruction and/or the executable changed.
            Adds new changes where instruction and executable are empty, but the before and after contain the full changes

    :param data: list of fix changes where new changes are appended (the training set before augmentation)
    """
    groupedData = groupby(data, key=lambda c: c.diff_id)

    artificial_changes: set[FixChange] = set()
    for diff_id, diff_changes in tqdm(groupedData, total=len(set(map(lambda c: c.diff_id, data))), desc="Augmenting per Diff: "):
        changelist = list(diff_changes)
        deleted_lines = list(filter(lambda c: c.change_type.lower().startswith(DEL_PREFIX), changelist))
        added_lines = list(filter(lambda c: c.change_type.lower().startswith(ADD_PREFIX), changelist))

        for deleted in deleted_lines:
            # Find updates which are represented as DELETE and ADD in dataset
            change_suffix = deleted.change_type[deleted.change_type.index("_") + 1:]
            # Filter checks if instruction and executable is equal
            # and if the added line is similar (contains) to the deleted one and the other way around
            add_candidates = filter(lambda c:
                                    c.change_type.endswith(change_suffix)
                                    and c.instruction == deleted.instruction
                                    and c.executable == deleted.executable,
                                    added_lines)

            # Add new Update fixes
            for candidate in add_candidates:
                artificial_changes.add(
                    FixChange(diff_id=candidate.diff_id, instruction=candidate.instruction,
                              executable=candidate.executable, change_type=f"{UPDATE_TYPE}_{change_suffix}",
                              before=deleted.before, after=candidate.after)
                )

            # Find updates to instruction and/or executable
            add_candidates = filter(lambda c:
                                    (c.instruction != deleted.instruction
                                     or c.executable != deleted.executable)
                                    and c.after == deleted.before,
                                    added_lines)
            # Add new fixes (special case since there is no before and after for instruction)
            for candidate in add_candidates:
                artificial_changes.add(
                    FixChange(diff_id=candidate.diff_id, instruction="",
                              executable="", change_type=f"{UPDATE_TYPE}_{change_suffix}",
                              before=f"{deleted.instruction} {deleted.executable or ''} {deleted.before}",
                              after=f"{candidate.instruction} {candidate.executable or ''} {candidate.after}")
                )

    # Append artificial changes to data
    data += artificial_changes


def filterDeletingChanges(data: list[FixChange]) -> list[FixChange]:
    """
    Removes all deleting changes from the list, since these changes won't be very useful for patches
    Should be called after augmentTrainingSet(), since that function uses the deleting changes to construct new ones

    :param data: a list of FixChange objects
    :return: a list with all FixChange objects of change type ADD or Update but not Delete
    """
    return list(
        filter(
            lambda it: not it.change_type.lower().startswith(DEL_PREFIX),
            data
        )
    )
