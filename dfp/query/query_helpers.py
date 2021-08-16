from typing import Tuple

import jellyfish

from dfp.model.Patch import PARAM_MATCHER


class ConcretePatch:

    def __init__(self, before_after: Tuple[str, str]):
        self.before = before_after[0]
        self.after = before_after[1]
        self.rank = self.calcRank()

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, ConcretePatch):
            return self.before == other.before and self.after == other.after
        else:
            return False

    def __hash__(self):
        return hash((self.before, self.after))

    def calcRank(self) -> float:
        """
        Calculates the rank for this concrete Patch
        Calculation:
            1. Update points = number of updated parameters
            2. Add points
                if nothing added = 0
                if >0 added = 1 - sum(1/2**i for i in range(1, added))
                    e.g. 1, 0.5, 0.25, ....
                    for  1, 2, 3 added parameters
            3. Similarity = jaro winkler similarity of before and after
            4. Result = Similarity * (Update points + Added points)

        So Updates are preferred over Additions.
        More similar updates are preferred.
        More updates are preferred.
        """
        before_words = set(self.before.split())
        after_words = set(self.after.split())

        updated = sum(1 for word in before_words if word not in after_words)
        added = len(after_words) - len(before_words)

        update_points = updated
        add_points = 1 - sum(1 / 2 ** i for i in range(1, added)) if added > 0 else 0
        points = update_points + add_points

        similarity_factor = similarity(self.before, self.after)

        return similarity_factor * points

    def apply(self, input_line: str) -> str:
        return self.after if input_line == self.before else input_line


def sortConcretePatches(patches: list[ConcretePatch]) -> list[ConcretePatch]:
    # First sort by after DESC to get the highest version numbers first
    alpha_sorted_patches = sorted(patches, key=lambda it: it.after, reverse=True)
    # Then sort by ranking
    return list(sorted(alpha_sorted_patches, key=lambda it: it.rank, reverse=True))


def filterUselessPatches(patches: list[ConcretePatch]) -> list[ConcretePatch]:
    return list(filter(lambda it: it.before != it.after, patches))


def stripRegex(s: str) -> str:
    return stripEscape(s.replace(PARAM_MATCHER, ""))


def stripEscape(s: str) -> str:
    tmp = "||supersecretstring||"
    return s.replace("\\\\", tmp).replace("\\", "").replace(tmp, "\\\\")


def stripEscapeExceptParamMatcher(s: str) -> str:
    tmp = "||supersecretstring||"
    return s.replace(PARAM_MATCHER, tmp).replace("\\", "").replace(tmp, PARAM_MATCHER)


def similarity(s1: str, s2: str) -> float:
    """
        Calculates the string edit similarity of two strings
        Using the jaro winkler algorithm, since it uses a prefix scale (better rating for same prefix, useful for commands and images)

        :param s1: string 1
        :param s2: string 2
        :return: similarity in [0,1]
        """
    return jellyfish.jaro_winkler_similarity(s1, s2)
