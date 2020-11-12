""" Entrypoint and functions for cli to test relations between metadata files."""
import argparse
import sys
from csv import DictReader
from json import load
from pathlib import Path
from typing import List, TypedDict


class FileRelationInformation(TypedDict):
    """Information about a file, whose relations can be tested."""

    file: Path
    fields: List[str]


class RelationOrigin(TypedDict):
    """Information of a file a relation is originating from."""

    file: str
    fields: List[str]


class RelationTarget(TypedDict):
    """Information of a file relations are pointing towards."""

    file: str
    fields: List[str]
    relations_from: List[RelationOrigin]


def read_relations(folder_path: Path) -> List[RelationTarget]:
    """Read config file containing relational information."""
    with open(folder_path.joinpath("relations.json")) as file:
        relations: List[RelationTarget] = load(file)
    return relations


def parse_arguments() -> argparse.Namespace:
    """Set up arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-folder", help="Path to the input metadata files.", type=_full_path
    )
    parser.add_argument(
        "-r",
        "--relational-file",
        help="JSON file containing relational information between files",
        type=_full_path,
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def relations_exist(
    target: FileRelationInformation, origins: List[FileRelationInformation]
) -> bool:
    """Check if reference from origin file to a target file exists."""
    with open(target["file"], "r") as _file:
        _reader = DictReader(_file)
        keypairs = set()
        for row in _reader:
            _keypair = list()
            for field in target["fields"]:
                _keypair.append(row[field])
            keypairs.add(tuple(_keypair))

    for origin in origins:
        with open(origin["file"], "r") as _file:
            _reader = DictReader(_file)
            for row in _reader:
                _keypair = list()
                for field in origin["fields"]:
                    _keypair.append(row[field])
                if tuple(_keypair) not in keypairs:
                    return False

    return True


def _full_path(path: str) -> Path:
    return Path(path).resolve()
