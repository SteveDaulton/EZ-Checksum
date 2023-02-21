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

import hashlib
import re
import xxhash

from typing_extensions import TypedDict


# Type hints
HashProfile = TypedDict('HashProfile',
                        {'name': str, 'hasher': 'hashlib._Hash',
                         'regex': re.Pattern[str], 'length': int})

MD5: HashProfile = {
    'name': 'MD5',
    'hasher': hashlib.md5(),
    'regex': re.compile(r'\b[a-f0-9]{32,32}\b', re.I),
    'length': 32
    }
SHA1: HashProfile = {
    'name': 'SHA-1',
    'hasher': hashlib.sha1(),
    'regex': re.compile(r'\b[a-f0-9]{40,40}\b', re.I),
    'length': 40
    }
SHA224: HashProfile = {
    'name': 'SHA-224',
    'hasher': hashlib.sha224(),
    'regex': re.compile(r'\b[a-f0-9]{56,56}\b', re.I),
    'length': 56
    }
SHA256: HashProfile = {
    'name': 'SHA-256',
    'hasher': hashlib.sha256(),
    'regex': re.compile(r'\b[a-f0-9]{64,64}\b', re.I),
    'length': 64
    }
SHA384: HashProfile = {
    'name': 'SHA-384',
    'hasher': hashlib.sha384(),
    'regex': re.compile(r'\b[a-f0-9]{96,96}\b', re.I),
    'length': 96
    }
SHA512: HashProfile = {
    'name': 'SHA-512',
    'hasher': hashlib.sha512(),
    'regex': re.compile(r'\b[a-f0-9]{128,128}\b', re.I),
    'length': 128
    }
XXH32: HashProfile = {
    'name': 'XXH32',
    'hasher': xxhash.xxh32(),
    'regex': re.compile(r'\b[a-f0-9]{8,8}\b', re.I),
    'length': 8
    }
XXH64: HashProfile = {
    'name': 'XXH64',
    'hasher': xxhash.xxh64(),
    'regex': re.compile(r'\b[a-f0-9]{16,16}\b', re.I),
    'length': 16
    }


HASH_TYPES: tuple[HashProfile, ...] = (MD5, SHA1, SHA224, SHA256,
                                       SHA384, SHA512, XXH32, XXH64,)


# Helper constants for easy access to values in hash profiles.

# A list of hashing type names for writing to saved settings.
HASH_STRINGS: tuple[str, ...] = tuple(alg['name'] for alg in HASH_TYPES)

# The length of each hash type as hex string:
HASH_LENGTHS: tuple[int, ...] = tuple(alg['length'] for alg in HASH_TYPES)

# HASH_CODES provide a reverse lookup of HASH_STRINGS
HASH_CODES: dict[str, int] = {
        alg['name']: idx for idx, alg in enumerate(HASH_TYPES)}
