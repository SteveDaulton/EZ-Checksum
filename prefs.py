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

    # Get last used hash name and convert to index.
    _alg: str = self.settings.value('Algorithm', 'SHA256')
    try:
        self.alg_id = Hp.get_hash_index(_alg)
    except KeyError:
        pass  # Use default.

    # Directory for opening files
    open_dir: str = self.settings.value('OpenDirectory', self.open_dir)
    if Path(open_dir).exists() and Path(open_dir).is_dir():
        self.open_dir = open_dir

    # Directory for saving results
    save_dir: str = self.settings.value('SaveDirectory', self.save_dir)
    if Path(save_dir).exists() and Path(save_dir).is_dir():
        self.save_dir = save_dir


def write_settings(self) -> None:
    """Write last used settings as human readable strings"""
    geometry = self.saveGeometry()
    self.settings.setValue('Geometry', geometry)
    self.settings.setValue('Algorithm', Hp.get_hash_name(self.alg_id))
    self.settings.setValue('OpenDirectory', self.open_dir)
    self.settings.setValue('SaveDirectory', self.save_dir)
    self.settings.sync()
