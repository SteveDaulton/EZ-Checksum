"""Main class for calculating checksums"""

from PyQt6.QtCore import QThread, QFileInfo, pyqtSignal

import hash_profiles as Hp

import dialogs


class ChecksumThread(QThread):
    """Worker thread to calculate checksums.

    Args:
        algorithm: Int. Index number of selected algorithm.
        data: A QListWidget or QLineEdit containing the file names
        to be processed.

    """

    updateProgressBar = pyqtSignal(int)
    checksum_sig = pyqtSignal(str, str)

    def __init__(self, algorithm, data):
        QThread.__init__(self)
        self.algorithm = algorithm
        self.data = data
        # Set stop_flag to True when we want to stop processing.
        self.stop_flag = False
        self.file_list_item = None

    # Override the destructor:
    def __del__(self):
        self.wait()

    def get_hash(self, fname):
        """Calculate the checksum."""
        profile = Hp.HASH_TYPES[self.algorithm]
        # Create a new copy of the hasher so that it will go out of
        # scope and be deleted when the function ends.
        hasher = profile['hasher'].copy()
        info = QFileInfo(fname)
        size = info.size()

        # Test for zero byte file
        if size == 0:
            self.checksum_sig.emit(fname, 'Error: Empty file.')
            return  # just bail

        # Process in blocks of at least 64k
        blocksize = max(65536, size // 100)
        progress_step = min(1.0, blocksize / float(size)) * 100
        progress = 0.0
        step = max(1.0, progress_step)
        percent = int(step)

        try:
            with open(fname, 'rb') as file_:
                buf = file_.read(blocksize)
                while (len(buf) > 0) and not self.stop_flag:
                    hasher.update(buf)
                    buf = file_.read(blocksize)
                    # Update progress bar when there's an
                    # integer increase in progress
                    progress += progress_step
                    if progress >= percent:
                        self.updateProgressBar.emit(min(100, percent))
                        percent = int(progress + step)
                if not self.stop_flag:
                    self.checksum_sig.emit(fname, str(hasher.hexdigest()))
                else:
                    self.updateProgressBar.emit(0)

        except (IOError, ValueError):
            dialogs.warning(self, 'An I/O error or a ValueError occurred')

    def run(self):
        """Override of QThread run."""
        self.get_hash(self.data.text())

    def stop(self):
        """Stop thread gracefully."""
        self.stop_flag = True
