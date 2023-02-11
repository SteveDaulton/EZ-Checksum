#!/usr/bin/env python

"""Validate module contains functions handling validation / verification."""

import hash_profiles as Hp


def hash_from_line(line):
    """Extract hash string from line of text.

    Return
    ------
        tuple or None
            Tuple in the form: (algorithm index, hash)
    """
    index = 0
    for profile in Hp.HASH_TYPES:
        match = profile['regex'].search(line)
        if match:
            return (index, match.group())
        index += 1
    return None


def set_validator(parent, text):
    """Set and disable the hashChoiceButton.
        Does a very fast length check first

        Return
        ------
            True if valid verifcation string, else False.
    """

    if len(text) in Hp.HASH_LENGTHS:
        hash_tuple = hash_from_line(text)
        if hash_tuple:
            parent.hashChoiceButton.setCurrentIndex(hash_tuple[0])
            parent.hashChoiceButton.setEnabled(False)
            # Ensure that we have a clean hex string
            parent.validateLineEdit.setText(hash_tuple[1])
            parent.has_validator = True
            return
    else:
        parent.hashChoiceButton.setEnabled(True)
        parent.has_validator = False
