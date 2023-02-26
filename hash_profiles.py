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


# Helper constants for easy look-ups in hash profiles.
HASH_NAMES: tuple[str, ...] = tuple(alg.name for alg in HASH_TYPES)
HASH_LENGTHS: tuple[int, ...] = tuple(alg.length for alg in HASH_TYPES)

# Reverse lookup of HASH_NAMES by index,
HASH_CODES: dict[str, int] = {
        hash_name: idx for idx, hash_name in enumerate(HASH_NAMES)}
