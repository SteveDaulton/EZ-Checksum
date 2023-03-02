#!/usr/bin/env python

"""Validate module contains functions handling validation / verification."""

import os
from typing import Optional
import re
import hash_profiles as Hp


def hash_from_line(line: str) -> 'tuple[int, str] | None':
    # TODO: We only really need the index.
    """Extract hash string from line of text.

    Return
    ------
        tuple or None
            Tuple in the form: (index, hash)
    """
    _idx = Hp.hash_idx_from_length(len(line))
    if is_valid_hash(line):
        return (_idx, line)


def set_validator(parent, text: str) -> None:
    """Sets and disables the hashChoiceButton and
    parent.has_validator: bool
    """
    parent.has_validator = False
    if Hp.is_valid_hash_length(len(text)):
        hash_tuple: 'tuple[int, str] | None' = hash_from_line(text)
        if hash_tuple:
            parent.hashChoiceButton.setCurrentIndex(hash_tuple[0])
            # Ensure that we have a clean hex string
            parent.validateLineEdit.setText(hash_tuple[1])
            parent.has_validator = True


def is_valid_hash(chksum: str) -> bool:
    """Return True if chksum could be a valid checksum."""
    if Hp.is_valid_hash_length(len(chksum)):
        _idx = Hp.hash_idx_from_length(len(chksum))
        _match = Hp.HASH_TYPES[_idx].regex.search(chksum)
        return bool(_match)
    return False


def file_exists(fname: str, path: Optional[str] = None) -> bool:
    """Return True if file found, else False."""
    if path:
        fname = os.path.join(path, fname)
    return os.path.isfile(fname)
