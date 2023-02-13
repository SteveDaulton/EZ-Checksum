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

# from typing import TypeAlias  # Not supported in Python 3.9
from typing import Union

import hashlib
import re
import xxhash


HashType = Union[str, 'hashlib._Hash', re.Pattern]
HashProfile = dict[str, HashType]

MD5: HashProfile = {
    'name': 'MD5',
    'hasher': hashlib.md5(),
    'regex': re.compile(r'\b[a-f0-9]{32,32}\b', re.I)
    }
SHA1: HashProfile = {
    'name': 'SHA-1',
    'hasher': hashlib.sha1(),
    'regex': re.compile(r'\b[a-f0-9]{40,40}\b', re.I)
    }
SHA224: HashProfile = {
    'name': 'SHA-224',
    'hasher': hashlib.sha224(),
    'regex': re.compile(r'\b[a-f0-9]{56.56}\b', re.I)
    }
SHA256: HashProfile = {
    'name': 'SHA-256',
    'hasher': hashlib.sha256(),
    'regex': re.compile(r'\b[a-f0-9]{64,64}\b', re.I)
    }
SHA384: HashProfile = {
    'name': 'SHA-384',
    'hasher': hashlib.sha384(),
    'regex': re.compile(r'\b[a-f0-9]{96,96}\b', re.I)
    }
SHA512: HashProfile = {
    'name': 'SHA-512',
    'hasher': hashlib.sha512(),
    'regex': re.compile(r'\b[a-f0-9]{128,128}\b', re.I)
    }
XXH32: HashProfile = {
    'name': 'XXH32',
    'hasher': xxhash.xxh32(),
    'regex': re.compile(r'\b[a-f0-9]{8,8}\b', re.I)
    }
XXH64: HashProfile = {
    'name': 'XXH64',
    'hasher': xxhash.xxh64(),
    'regex': re.compile(r'\b[a-f0-9]{16,16}\b', re.I)
    }

# A list of dicts that allow a specified hash profile
# to be selected by its index number.
HASH_TYPES: tuple[HashProfile, ...] = (MD5, SHA1, SHA224, SHA256,
                                       SHA384, SHA512, XXH32, XXH64,)
# The length of each hash type as hex string:
HASH_LENGTHS: tuple[int, ...] = (32, 40, 56, 64, 96, 128, 8, 16,)
# A list of hashing type names for writing to saved settings.
HASH_STRINGS: tuple[str, ...] = ('MD5', 'SHA1', 'SHA224', 'SHA256',
                                 'SHA384', 'SHA512', 'XXH32', 'XXH64',)
# HASH_CODES provide a reverse lookup of HASH_STRINGS
HASH_CODES = {alg_name: HASH_STRINGS.index(alg_name)
              for alg_name in HASH_STRINGS}
