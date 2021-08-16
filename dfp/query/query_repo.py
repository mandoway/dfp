import re

from sqlalchemy import literal
from sqlalchemy.orm import Session

from dfp.DockerInstruction import DockerInstruction
from dfp.model.Patch import Patch2
from dfp.query.custom_patches import CUSTOM_PATCHES
from dfp.query.query_helpers import ConcretePatch
from dfp.query.version_query import SUPPORTED_PM, NOT_FOUND, dockerFetchLatestVersion
from dfp.util import splitDockerInstruction

USE_CUSTOM = True


def queryNonCombinableMatches(input_line: str, session: Session) -> list[Patch2]:
    matches = session.query(Patch2) \
        .filter(
        Patch2.is_combinable == False,
        literal(input_line).op("SIMILAR TO")(Patch2.before)
    ).all()

    if USE_CUSTOM:
        matches += queryCustomPatches(input_line, is_combinable=False)

    return matches


def queryCombinableMatches(input_line: str, session: Session) -> list[Patch2]:
    matches = session.query(Patch2) \
        .filter(
        Patch2.is_combinable == True,
        literal(input_line).op("SIMILAR TO")(Patch2.before)
    ).all()

    if USE_CUSTOM:
        matches += queryCustomPatches(input_line, is_combinable=True)

    return matches


def queryCustomPatches(input_line: str, is_combinable: bool):
    return list(
        filter(lambda it: it.is_combinable == is_combinable and re.match(it.before, input_line), CUSTOM_PATCHES))


def generateVersionPatches(input_line: str) -> list[ConcretePatch]:
    instruction, params = splitDockerInstruction(input_line)

    gen_patches = []
    if instruction == DockerInstruction.FROM.name:
        for param in params:
            # Should only be one param but just to be sure
            versions = dockerFetchLatestVersion(param)
            if NOT_FOUND not in versions:
                for version in versions:
                    gen_patches.append(
                        ConcretePatch(
                            before_after=(input_line, input_line.replace(param, f"{param}:{version}"))
                        )
                    )

    elif instruction == DockerInstruction.RUN.name:
        if params[0] in SUPPORTED_PM:
            delimiter = SUPPORTED_PM[params[0]][0]
            getLatestVersion = SUPPORTED_PM[params[0]][1]

            output_params = params[:2]
            for param in params[2:]:
                latest = getLatestVersion(param)
                if latest != NOT_FOUND:
                    output_params.append(
                        param + delimiter + latest
                    )
                else:
                    output_params.append(
                        param
                    )
            gen_patches.append(
                ConcretePatch(
                    before_after=(input_line, f"{instruction} {' '.join(output_params)}")
                )
            )

    return gen_patches
