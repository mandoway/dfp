from pathlib import Path


def getProjectRoot() -> Path:
    return Path(__file__).parent.parent


def getPathFromRoot(path: str) -> Path:
    return Path(getProjectRoot(), path)
