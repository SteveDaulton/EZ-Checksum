#!/usr/bin/env python

"""Validate module contains functions handling validation / verification."""

from typing import Optional
import re
import hash_profiles as Hp


def hash_from_line(line: str) -> 'tuple[int, str] | None':
    """Extract hash string from line of text.

    Return
    ------
        tuple or None
            Tuple in the form: (algorithm index, hash)
    """
    index = 0
    # Match = NewType('Match', 're.Match[str]')
    match: Optional[re.Match[str]] = None
    for profile in Hp.HASH_TYPES:
        match = profile['regex'].search(line)
        if match:
            return (index, match.group())
        index += 1
    return None


def set_validator(parent, text: str) -> None:
    """Sets and disables the hashChoiceButton and
    parent.has_validator: bool
    """
    parent.has_validator = False
    if len(text) in Hp.HASH_LENGTHS:
        hash_tuple: 'tuple[int, str] | None' = hash_from_line(text)
        if hash_tuple:
            parent.hashChoiceButton.setCurrentIndex(hash_tuple[0])
            # Ensure that we have a clean hex string
            parent.validateLineEdit.setText(hash_tuple[1])
            parent.has_validator = True
