#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""EZchecksum is a GUI application for calculating and testing checksums."""

import os
import sys

from pathlib import PurePath

from PyQt6.QtCore import QDir, pyqtSignal, Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtGui import QIcon

import gui
import hash_profiles as Hp
import prefs
import dialogs
import calc
import validate

VERSION = '0.2.0'


class ShaApp(QMainWindow, gui.Ui_MainWindow):
    """GUI application for calculating and testing checksums.

    Supported hash algorithms are defined in hash_profiles.


    Algorithm:

        The default algorithm is SHA-256. May also be overridden
        if an optional validation string is set.

    Validation String:

        An optional test value (hex hash string) may be
        entered. If provided the algorithm will be detected from the
        length of the string.

        If the validation string is a URL, the target will be downloaded
        and searched for supported hash strings. The file will be tested
        against each hash string found.


    Attributes
    ----------
        default_open_dir : string
            Default directory for opening files or directories.
        default_save_dir : string
            Default directory for saving results.
        hash_thread : QThread
            Worker thread.
        has_validator : bool
            True when a validation hex checksum exists
        algorithm : dict
            Hash profile (see: :doc:`hash_profiles`)
        data : QLineEdit
            Data for worker thread. See: :py:mod:`calc.ChecksumThread`.
    """

    checksum = pyqtSignal(str, str)
    updateProgressBar = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.png'))

        self.default_open_dir: str = QDir.homePath()
        self.default_save_dir = QDir.homePath()
        self.hash_thread = None
        self.has_validator = False  # True when verification hash is valid.

        # Settings
        self.algorithm = Hp.HASH_CODES['SHA256']
        self.data = None

        # Update settings from saved config
        prefs.read_settings(self)

        # Drag and drop methods
        self.fileSelectLineEdit.dragEnterEvent = file_drag_enter_event
        self.fileSelectLineEdit.dropEvent = self.file_line_drop_event
        self.validateLineEdit.dragEnterEvent = line_validate_enter_event
        self.validateLineEdit.dropEvent = self.line_validate_drop_event

        # Menu actions
        self.actionSelect_File.triggered.connect(self.file_browser)
        self.actionSave_Result.triggered.connect(self.save_result)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout.triggered.connect(self.about)
        self.actionAbout_Qt.triggered.connect(QApplication.aboutQt)

        # Button actions
        self.fileAddButton.clicked.connect(self.file_browser)
        self.outputFileButton.clicked.connect(self.set_outpath)
        self.goButton.clicked.connect(self.run_checksum)
        self.cancelButton.clicked.connect(self.stop)
        self.closeButton.clicked.connect(self.quit)
        self.resetButton.clicked.connect(self.reset_or_clear)
        self.hashChoiceButton.currentIndexChanged.connect(
                self.set_hash_algorithm
                )

        # fileSelectLineEdit actions
        self.fileSelectLineEdit.textChanged.connect(
                self.file_input_text_changed
                )
        self.validateLineEdit.textChanged.connect(self.validator_changed)

    def run_checksum(self):
        """Checksum calculation."""
        # Checksum processing in separate thread.
        self.data = self.fileSelectLineEdit
        verify_text = self.validateLineEdit.text()
        validate.set_validator(self, verify_text)

        # Now create thread
        self.hash_thread = calc.ChecksumThread(self.algorithm, self.data)
        self.hash_thread.checksum.connect(self.handle_result)
        self.hash_thread.updateProgressBar.connect(self.progressBar.setValue)
        self.hash_thread.start()
        self.update_gui()

    def closeEvent(self, event):  # pylint: disable=C0103
        """Override window close requests."""
        event.ignore()
        self.quit()

    def update_gui(self):
        """Update buttons and menus."""
        # Get current states
        has_input = len(self.fileSelectLineEdit.text()) > 0
        has_output = len(self.resultTextBrowser.toPlainText()) > 0
        has_verify = len(self.validateLineEdit.text()) > 0

        try:
            hash_thread_running = self.hash_thread.isRunning()
        except AttributeError:  # hash_thread may not have been created yet.
            hash_thread_running = False
        hash_thread_idle = not hash_thread_running

        self.fileSelectLineEdit.setEnabled(hash_thread_idle)
        self.validateLineEdit.setEnabled(hash_thread_idle)
        # Enabled when hash_thread_idle and something to clear.
        can_clear = has_input or has_output or has_verify
        self.resetButton.setEnabled(can_clear and hash_thread_idle)
        # Enabled when hash_thread_running
        self.cancelButton.setEnabled(hash_thread_running)
        if self.has_validator:
            self.statusbar.clearMessage()
            self.validateLineEdit.setStatusTip('')
        else:
            self.hashChoiceButton.setEnabled(hash_thread_idle)
            self.statusbar.showMessage('No validation text entered.')
            self.validateLineEdit.setStatusTip(
                'No validation text entered.')

    # Write to Output
    def handle_result(self, name, checksum):
        """Handle checksum results."""
        alg_name = Hp.HASH_TYPES[self.algorithm]['name']
        txt = f'File name: {name}\n{alg_name} checksum: {checksum}\n'
        self.resultTextBrowser.append(txt)

        if self.has_validator:
            if checksum == self.validateLineEdit.text():
                self.resultTextBrowser.append(
                    '<font color="#009900"><b>Success. '
                    'Checksum matches the expected value.'
                    '</b></font>')
            else:
                self.resultTextBrowser.append(
                    '<font color="red"><b>Fail. Checksum does not '
                    'match expected value. </b></font>')
        elif len(self.validateLineEdit.text()) > 0:
            self.resultTextBrowser.append(
                '<b>Warning. The \'Validation\' text is not '
                'a recognised checksum.</b>')
        if len(self.outputLineEdit.text()) > 0:
            output = self.outputLineEdit.text()
            fname = PurePath(name).name  # Name of the processed file
            try:
                with open(output, 'wt', encoding='utf8') as fp:
                    fp.write(f'{checksum} {fname}')
                    self.resultTextBrowser.append(
                        f'Result written to {output}\n')
            except FileNotFoundError:
                self.resultTextBrowser.append(
                    f'<font color="red">{output} '
                    'is not writeable.</font>')
        self.update_gui()

    def save_result(self):
        """Save results to file"""
        text = self.resultTextBrowser.toPlainText()

        if not text:
            dialogs.critical(
                self,
                'No results to print.\nCalculate checksum first.')
            return
        dialogs.save_results(self, text)

    def quit(self):
        """Shutdown application."""
        prefs.write_settings(self)
        sys.exit()

    def about(self):
        """Show :py:mod:`'About' <dialogs.about>` dialog"""
        dialogs.about(self, VERSION)

    def file_line_drop_event(self, event):
        """Handle fileSelectLineEdit drop events"""
        etype = event.mimeData()
        if etype.hasText() and len(etype.text()) > 1:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.fileSelectLineEdit.setText(etype.text())
        elif etype.hasUrls:
            if len(etype.urls()) == 1:
                event.setDropAction(Qt.DropAction.CopyAction)
                file_ = str(etype.urls()[0].toLocalFile())
                self.fileSelectLineEdit.setText(file_)
                event.accept()
            elif len(etype.urls()) > 1:
                dialogs.warning(self, 'Too many files dropped.')
            else:
                dialogs.warning(self, 'Invalid file.')
        else:
            event.ignore()

    def line_validate_drop_event(self, event):
        """Handle drop event for validateLineEdit."""
        etype = event.mimeData()
        if etype.hasText() and len(etype.text()) > 1:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.validateLineEdit.setText(etype.text())
        else:
            event.ignore()

    def file_input_text_changed(self):
        """QLineEdit handler for typed input.

        Sets goButton state: Enabled when file input string is a valid file.
        """
        is_valid_file = os.path.isfile(self.fileSelectLineEdit.text())
        self.goButton.setEnabled(is_valid_file)
        if is_valid_file:
            self.goButton.setToolTip('Click to start processing.')
            self.goButton.setStatusTip('File selected.')
            self.fileSelectLineEdit.setStatusTip('')

        else:
            self.goButton.setToolTip('Select file first')
            self.goButton.setStatusTip('No file selected.')
        self.update_gui()

    def validator_changed(self):
        """QLineEdit handler for typed validator."""
        validate.set_validator(self, self.validateLineEdit.text())
        self.update_gui()

    def file_browser(self):
        """Qt File browser for single file."""
        fname = QFileDialog.getOpenFileName(
            self, 'Select File', self.default_open_dir)
        if fname[0]:
            self.default_open_dir = os.path.dirname(str(fname[0]))
            self.fileSelectLineEdit.setText(fname[0])

    def set_outpath(self):
        """Set the checksum output file path."""
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Save",
            self.default_save_dir,
            ('Checksum Files (*.md5 *.sha1 *.sha224 *.sha256 *.384 '
             '*.sha512 *.sha);;Text Files (*.txt);;All Files (*)'))
        self.outputLineEdit.setText(fname)

    # Button: Stop
    def stop(self):
        """Stop ChecksumThread."""
        self.hash_thread.stop()
        self.hash_thread.wait()
        self.update_gui()

    # Choice Button: Algorithm
    def set_hash_algorithm(self, choice):
        """hash algorithm setter."""
        self.algorithm = choice
        alg_name = Hp.HASH_TYPES[choice]['name']
        self.hashChoiceButton.setStatusTip(f'Current algorithm: {alg_name}.')

    def reset_or_clear(self):
        """Reset GUI."""
        self.fileSelectLineEdit.clear()
        self.fileSelectLineEdit.setStatusTip('No file selected.')
        self.validateLineEdit.clear()
        self.resultTextBrowser.clear()
        self.update_gui()


def file_drag_enter_event(event):
    """Accept drag enter event if hasUrls"""
    if event.mimeData().hasUrls:
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
    else:
        event.ignore()


def line_validate_enter_event(event):
    """Accept drag enter event if text"""
    etype = event.mimeData()
    if etype.hasText() and len(etype.text()) > 1:
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
    else:
        event.ignore()


def main():
    """Create window"""
    app = QApplication(sys.argv)
    window = ShaApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
