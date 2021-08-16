from typing import Optional, Tuple

from sqlalchemy.orm import Session

from dbHelper import initSessionMaker
from dfp.model.Patch import Patch2, PARAM_MATCHER
from dfp.query.query_helpers import ConcretePatch, sortConcretePatches, filterUselessPatches, stripRegex, \
    stripEscapeExceptParamMatcher, similarity
from dfp.query.query_repo import queryNonCombinableMatches, queryCombinableMatches, generateVersionPatches, USE_CUSTOM
from dfp.util import removeDuplicates, first


def findPatches(input_line: str, limit: Optional[int] = None, patch_blacklist: set[str] = None) -> list[ConcretePatch]:
    if patch_blacklist is None:
        patch_blacklist = {}

    session: Session = initSessionMaker("dfp")()

    non_combinable_matches = queryNonCombinableMatches(input_line, session)
    non_combinable_matches = removeDuplicates(non_combinable_matches)
    non_combinable_ranked_matches = buildConcretePatches(non_combinable_matches, input_line, patch_blacklist)

    combinable_matches = queryCombinableMatches(input_line, session)
    combinable_matches = removeDuplicates(combinable_matches)
    combinable_ranked_matches = buildCombinedConcretePatches(combinable_matches, input_line, patch_blacklist)

    session.close()

    if USE_CUSTOM:
        generated_version_patches = generateVersionPatches(input_line)
    else:
        generated_version_patches = []

    all_matches = non_combinable_ranked_matches + combinable_ranked_matches + generated_version_patches

    all_matches = removeDuplicates(all_matches)
    all_matches = filterUselessPatches(all_matches)
    all_matches = sortConcretePatches(all_matches)
    return all_matches[:limit]


def buildConcretePatches(patches: list[Patch2], input_line: str, patch_blacklist: set[str]) -> list[ConcretePatch]:
    return [
        ConcretePatch(
            before_after=buildConcretePatch(patch, input_line, patch_blacklist)
        ) for patch in patches
    ]


def buildConcretePatch(patch: Patch2, input_line: str, patch_blacklist: set[str]) -> Tuple[str, str]:
    before, after = [], []

    before_parts = stripEscapeExceptParamMatcher(patch.before).replace(PARAM_MATCHER, f" {PARAM_MATCHER}").split()
    after_parts = stripEscapeExceptParamMatcher(patch.after).replace(PARAM_MATCHER, f" {PARAM_MATCHER}").split()

    input_parts = input_line.split()
    input_index = 0

    for patch_index, patch_before in enumerate(before_parts):
        if input_index >= len(input_parts):
            # Add remaining patch parameters
            # no more input params, but we might want to add parameters from the patch (only add to after)
            for after_part in after_parts[patch_index:]:
                if after_part != PARAM_MATCHER and after_part not in after:
                    after.append(after_part)
            # there is no more information to loop through
            break
        elif patch_before == input_parts[input_index]:
            # Update parameter
            before.append(patch_before)

            new_after = after_parts[patch_index] if patch_before not in patch_blacklist else patch_before
            after.append(new_after)
            input_index += 1
        elif patch_before == PARAM_MATCHER:
            # Add input parameters for matchers until we reach a match
            next_exact_match = first(before_parts[patch_index:], condition=lambda it: it != PARAM_MATCHER)
            if next_exact_match is not None:
                # Add values until we reach the next exact match
                while input_parts[input_index] != next_exact_match:
                    before.append(input_parts[input_index])
                    after.append(
                        patch.transformSingle(input_parts[input_index])
                    )
                    input_index += 1
            else:
                while input_index < len(input_parts):
                    # purposefully a while loop since we need the index for other logic
                    before.append(input_parts[input_index])
                    after.append(
                        patch.transformSingle(input_parts[input_index])
                    )
                    input_index += 1

    return " ".join(before), patch.transformGroup(after)


def buildCombinedConcretePatches(matches: list[Patch2], input_line: str, patch_blacklist: set[str]) \
        -> list[ConcretePatch]:
    # Build a dict where each input parameter maps to a list of their changes
    param_changes = getParamChangeDict(input_line, matches, patch_blacklist)

    # Build concrete patches where only one of the params change
    concrete_patches = buildSingleParamConcretePatches(input_line, param_changes)

    # Build concrete patches where all possible params change, changes are taken in order of their ranks
    concrete_patches += buildMultiParamConcretePatches(input_line, param_changes)

    return concrete_patches


def getParamChangeDict(input_line: str, matches: list[Patch2], patch_blacklist: set[str]) -> dict[str, list[str]]:
    """
    Builds a dict where each key corresponds to a parameter in the input which is also present in the patch.
    The values consist of ranked lists of changes for these parameters.
    The ranking is based on the similarity of the before and after state of a parameter change

    :param input_line: input line containing parameters
    :param matches: list of found patches
    :param patch_blacklist: set of parameters which must not be changed
    :return: dict where each parameter (if present in any patch) maps to a list of their changes)
    """
    cleaned_befores = list(map(lambda it: (it[0], stripRegex(it[1].before)), enumerate(matches)))

    param_changes = {}
    for word in input_line.split():
        if word in patch_blacklist:
            continue

        matching_patches = list(filter(lambda it: word in it[1].split(), cleaned_befores))
        for patch_index, match in matching_patches:
            word_idx = match.split().index(word)

            after_words = stripRegex(matches[patch_index].after).split()
            changed_word = after_words[word_idx] if word_idx < len(after_words) else ""
            if changed_word != word:
                if word not in param_changes:
                    param_changes[word] = set()
                param_changes[word].add(changed_word)

    # Rank the changes of each parameter based on their similarity
    for before, value in param_changes.items():
        param_changes[before] = list(sorted(value, key=lambda it: similarity(before, it), reverse=True))

    return param_changes


def buildSingleParamConcretePatches(input_line: str, param_changes: dict[str, list[str]]) -> list[ConcretePatch]:
    """
    Builds concrete patches where always only one of the parameters change to the best fitting patch

    :param input_line: line to patch
    :param param_changes: dict where each parameter (if present in any patch) maps to a list of their changes)
    :return: list of concrete patches where only one parameter is changed
    """
    concrete_patches = []
    for param in input_line.split():
        if param in param_changes:
            after_param = param_changes[param][0]
            after = input_line.replace(param, after_param)
            concrete_patches.append(
                ConcretePatch(
                    before_after=(input_line, after)
                )
            )
    return concrete_patches


def buildMultiParamConcretePatches(input_line: str, param_changes: dict[str, list[str]]) -> list[ConcretePatch]:
    """
    Builds concrete patches where multiple parameters change.
    Starts with the best fitting change for all parameters.
    Iterates over the max length of the single parameter change lists.
    If a list doesn't contain as many changes as others, the best fitting change is taken instead.
    If a parameter is not present in the param_changes dict, the input is taken.

    :param input_line: line to patch
    :param param_changes: dict where each parameter (if present in any patch) maps to a list of their changes)
    :return: list of concrete patches where multiple parameters are changed
    """
    if len(param_changes) == 0:
        return []

    concrete_patches = []
    max_len = max(map(lambda v: len(v), param_changes.values()))
    for i in range(max_len):
        after = input_line
        for word in input_line.split():
            if word not in param_changes:
                # No changes found for this param so default to input
                after_param = word
            elif i >= len(param_changes[word]):
                # Reached the end of changes for this word, take the best fitting one instead
                after_param = param_changes[word][0]
            else:
                # Take the change at i
                after_param = param_changes[word][i]

            after = after.replace(word, after_param)

        if input_line != after:
            concrete_patches.append(
                ConcretePatch(
                    before_after=(input_line, after)
                )
            )
    return concrete_patches
