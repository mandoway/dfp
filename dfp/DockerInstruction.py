from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def names(cls):
        return list(map(lambda c: c.name, cls))


class DockerInstruction(ExtendedEnum):
    FROM = "FROM"
    MAINTAINER = "MAINTAINER"
    RUN = "RUN"
    CMD = "CMD"
    LABEL = "LABEL"
    EXPOSE = "EXPOSE"
    ENV = "ENV"
    ADD = "ADD"
    COPY = "COPY"
    ENTRYPOINT = "ENTRYPOINT"
    VOLUME = "VOLUME"
    USER = "USER"
    WORKDIR = "WORKDIR"
    ARG = "ARG"
    ONBUILD = "ONBUILD"
    STOPSIGNAL = "STOPSIGNAL"
    HEALTHCHECK = "HEALTHCHECK"
    SHELL = "SHELL"
