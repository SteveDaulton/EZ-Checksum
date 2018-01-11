"""Helper functions for reading and writing user preferences."""

from PyQt4 import QtCore

import hash_profiles as Hp


def read_settings(self):
    """Restore from last used (or default) settings"""
    # TODO: Validate settings
    self.settings = QtCore.QSettings('AudioNyq', 'EZ Checksum')

    # Restore GUI size and position
    geometry = self.setGeometry(100, 100, -1, -1)
    geometry = self.settings.value('Geometry', geometry).toByteArray()
    self.restoreGeometry(geometry)

    # The 'algorithm' parameter carries the HASH_TYPE index number.
    # This makes it easier to retrieve the profile as: Hp.HASH_TYPES[self.algorithm]
    # Default hash encoding is Sha 256
    algorithm = self.settings.value('Algorithm', 'SHA256').toString()
    try:
        algorithm_index = Hp.HASH_CODES[str(algorithm)]
    except KeyError:
        algorithm_index = Hp.HASH_CODES['SHA256']
    self.algorithm = algorithm_index
    self.hashChoiceButton.setCurrentIndex(self.algorithm)


    # Default directory for opening files
    self.default_open_dir = self.settings.value(
        'OpenDirectory', self.default_open_dir).toString()

    # Default directory for saving results
    self.default_save_dir = self.settings.value(
        'SaveDirectory', self.default_save_dir).toString()


def write_settings(self):
    """Write last used settings as human readable strings"""
    geometry = self.saveGeometry()
    self.settings.setValue('Geometry', geometry)

    # self.algorithm is the HASH_TYPE index number.
    self.settings.setValue('Algorithm', Hp.HASH_STRINGS[self.algorithm])

    self.settings.setValue('OpenDirectory', self.default_open_dir)
    self.settings.setValue('SaveDirectory', self.default_save_dir)
    self.settings.sync()
