from typing import TypeVar

T = TypeVar('T')


def getListElemWithDefault(a_list: list[T], index: int, default: T) -> T:
    """
    Get list element, if it doesn't exist return the default
    """
    try:
        return a_list[index]
    except IndexError:
        return default


def first(iterable, condition=lambda it: True, default: T = None) -> T:
    return next((x for x in iterable if condition(x)), default)


def splitDockerInstruction(input_line: str) -> (str, list[str]):
    """
    Splits a docker instruction to a tuple, where the first position contains the instruction (e.g. RUN) and the second
    contains a list of all parameters (e.g. [npm, install])

    :param input_line: string containing a docker line
    :return: tuple of instruction and parameter list
    """
    parts = input_line.split()
    if len(parts) < 1:
        return "", []
    return parts[0], parts[1:]


def joinDockerInstruction(input_instruction: str, input_params: list[str]) -> str:
    """
    Reverse operation to splitDockerInstruction

    :param input_instruction: docker instruction, e.g. FROM
    :param input_params: list of parameters, e.g. [ubuntu]
    :return: string representation of a docker instruction, e.g. FROM ubuntu
    """
    return f"{input_instruction} {' '.join(input_params)}"


def removeDuplicates(a_list: list) -> list:
    """
    Removes duplicates from a list and returns it.
    Type needs to implement __eq__
    """
    return list(dict.fromkeys(a_list))


def countOverlapping(string: str, sub: str) -> int:
    count = start = 0
    while True:
        start = string.find(sub, start) + 1
        if start > 0:
            count += 1
        else:
            return count
