"""Provides dictionaries defining the available hashing profiles.

    Supported algorithms:

    - MD5
    - SHA-1
    - SHA-224
    - SHA-256
    - SHA-384
    - SHA-512
    - XXH32
    - XXH64

"""

from typing import NamedTuple

import sys
import hashlib
import re
import xxhash


HashProfile = NamedTuple('HashProfile', [('name', str),
                                         ('hasher', 'hashlib._Hash'),
                                         ('regex', re.Pattern[str]),
                                         ('length', int)])

MD5 = HashProfile('MD5', hashlib.md5(),
                  re.compile(r'\b[a-f0-9]{32,32}\b', re.I), 32)
SHA1 = HashProfile('SHA1', hashlib.sha1(),
                   re.compile(r'\b[a-f0-9]{40,40}\b', re.I), 40)
SHA224 = HashProfile('SHA224', hashlib.sha224(),
                     re.compile(r'\b[a-f0-9]{56,56}\b', re.I), 56)
SHA256 = HashProfile('SHA256', hashlib.sha256(),
                     re.compile(r'\b[a-f0-9]{64,64}\b', re.I), 64)
SHA384 = HashProfile('SHA384', hashlib.sha384(),
                     re.compile(r'\b[a-f0-9]{96,96}\b', re.I), 96)
SHA512 = HashProfile('SHA512', hashlib.sha512(),
                     re.compile(r'\b[a-f0-9]{128,128}\b', re.I), 128)
XXH32 = HashProfile('XXH32', xxhash.xxh32(),
                    re.compile(r'\b[a-f0-9]{8,8}\b', re.I), 8)
XXH64 = HashProfile('XXH64', xxhash.xxh64(),
                    re.compile(r'\b[a-f0-9]{16,16}\b', re.I), 16)


HASH_TYPES: tuple[HashProfile, ...] = (MD5, SHA1, SHA224, SHA256,
                                       SHA384, SHA512, XXH32, XXH64,)


_HASH_NAMES: tuple[str, ...] = tuple(alg.name for alg in HASH_TYPES)
_HASH_LENGTHS: tuple[int, ...] = tuple(alg.length for alg in HASH_TYPES)


# Getter functions.

def get_hash(idx: int) -> HashProfile:
    """Return HashProfile at HASH_TYPES[index]"""
    return HASH_TYPES[idx]


def get_hash_name(idx):
    """Return name of hash at HASH_TYPES[index]"""
    try:
        return HASH_TYPES[idx].name
    except IndexError:
        msg = f'Error: "{idx}" out of range in get_hash_name().'
        sys.exit(msg)
    except TypeError:
        msg = f'Error: get_hash_name() requires an int. Got {type(idx)}'
        sys.exit(msg)


def is_valid_hash_length(val: int) -> bool:
    """Return True if val is a valid checksum length."""
    return val in _HASH_LENGTHS


def get_hash_index(name: str) -> int:
    """Return index of HashProfile.name in HASH_TYPES."""
    try:
        return _HASH_NAMES.index(name)
    except ValueError:
        msg = f'Error: "{name}" is not a valid hash name'
        sys.exit(msg)


def hash_idx_from_length(length: int) -> int:
    """Return hash index of HashProfile with specified hash length"""
    try:
        return _HASH_LENGTHS.index(length)
    except ValueError:
        sys.exit('Error in hash_idx_from_length: '
                 f'\"{length}\" not in _HASH_LENGTHS')
