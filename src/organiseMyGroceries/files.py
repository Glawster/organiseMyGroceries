"""Shared filesystem validation for grocery artifacts."""

from pathlib import Path

## output


def outputResolve(directory: Path, stem: str, suffix: str) -> Path:
    """Resolve a generated artifact beneath the project output directory."""

    outputRoot = Path("output").resolve()
    directoryPath = directory.resolve()
    if directoryPath != outputRoot:
        raise ValueError(f"output directory must be '{outputRoot}'")
    return directoryPath / f"{stem}{suffix}"


## source


def sourceValidate(sourcePath: Path, suffixes: set[str]) -> Path:
    """Validate and resolve a user-provided source file."""

    source = sourcePath.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"source file does not exist: '{sourcePath}'")
    if source.suffix.lower() not in suffixes:
        expected = ", ".join(sorted(suffixes))
        raise ValueError(f"source '{sourcePath}' must use one of: {expected}")
    return source


## text


def textLinesRead(source: Path) -> list[str]:
    """Read non-empty stripped lines from a text file."""

    return [line.strip() for line in source.read_text().splitlines() if line.strip()]
