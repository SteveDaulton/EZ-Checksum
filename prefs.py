"""Helper functions for reading and writing user preferences."""

from pathlib import Path

from PyQt6.QtCore import QSettings

import hash_profiles as Hp


def read_settings(self) -> None:
    """Restore from last used (or default) settings"""
    self.settings = QSettings('AudioNyq', 'EZ Checksum')

    # Restore GUI size and position
    if (geometry := self.settings.value('Geometry')):
        self.restoreGeometry(geometry)
    else:
        self.setGeometry(100, 100, -1, -1)

    # The 'algorithm' parameter carries the HASH_TYPE index number.
    # This makes it easier to retrieve the profile as:
    # Hp.HASH_TYPES[self.algorithm: int]
    # Default hash encoding is Sha 256.
    algorithm: str = self.settings.value('Algorithm', 'SHA256')
    try:
        algorithm_index: int = Hp.HASH_CODES[str(algorithm)]
        self.algorithm = algorithm_index
    except KeyError:
        pass  # Use default.

    # Default directory for opening files
    open_dir: str = self.settings.value('OpenDirectory', self.open_dir)
    if Path(open_dir).exists() and Path(open_dir).is_dir():
        self.open_dir = open_dir

    # Default directory for saving results
    save_dir: str = self.settings.value('SaveDirectory', self.save_dir)
    if Path(save_dir).exists() and Path(save_dir).is_dir():
        self.save_dir = save_dir


def write_settings(self) -> None:
    """Write last used settings as human readable strings"""
    geometry = self.saveGeometry()
    self.settings.setValue('Geometry', geometry)

    # self.algorithm is the HASH_TYPE index number.
    self.settings.setValue('Algorithm', Hp.HASH_STRINGS[self.algorithm])

    self.settings.setValue('OpenDirectory', self.open_dir)
    self.settings.setValue('SaveDirectory', self.save_dir)
    self.settings.sync()
