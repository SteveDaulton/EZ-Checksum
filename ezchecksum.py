#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""EZchecksum is a GUI application for calculating and testing checksums."""

import os
import sys

from pathlib import PurePath, Path

from PyQt6.QtCore import QDir, Qt, QRegularExpression
from PyQt6.QtWidgets import (QMainWindow, QApplication, QFileDialog,
                             QMessageBox)
from PyQt6.QtGui import QIcon, QRegularExpressionValidator

import gui
import hash_profiles as Hp
import prefs
import dialogs
import calc
import validate

VERSION = '0.3.0'


class ShaApp(QMainWindow, gui.Ui_MainWindow):
    """GUI application for calculating and testing checksums.

    Algorithm:

        The default algorithm is SHA-256. Supported hash algorithms
        are defined in hash_profiles.

    Validation String:

        An optional test value (hex hash string). If provided the
        algorithm will be selected based on the length of the string.

    Attributes
    ----------
        open_dir : string
            Default directory for opening files or directories.
        save_dir : string
            Default directory for saving results.
        hash_thread : QThread
            Worker thread.
        has_validator : bool
            True when a validation hex checksum with length of a
            suported hash type exists.
        algorithm : dict
            Hash profile (see: :doc:`hash_profiles`)
        data : QLineEdit
            Data for worker thread. See: :py:mod:`calc.ChecksumThread`.
    """

    def __init__(self, parent: None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.png'))

        # Default settings
        self.open_dir: str = QDir.homePath()
        self.save_dir: str = QDir.homePath()
        self.hash_thread: calc.ChecksumThread
        self.has_validator: bool = False
        self.alg_id: int = Hp.HASH_CODES['SHA-256']

        # Widget properties
        self.resultTextBrowser.setStyleSheet("background-color: white;")
        hexreg = QRegularExpression(r'[0-9a-fA-F]*')
        self.validateLineEdit.setValidator(QRegularExpressionValidator(hexreg))

        # Update settings from saved config
        prefs.read_settings(self)
        # Must be set after reading prefs.
        self.hashChoiceButton.setCurrentIndex(self.alg_id)

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
                self.set_hash_algorithm)

        # LineEdit actions
        self.fileSelectLineEdit.textChanged.connect(
                self.file_select_changed)
        self.validateLineEdit.textChanged.connect(
                self.validator_changed)
        self.outputLineEdit.textChanged.connect(
                self.output_line_changed)

    def run_checksum(self) -> None:
        """Checksum calculation."""
        # Create checksum processing QThread.
        self.hash_thread = calc.ChecksumThread(self.alg_id,
                                               self.fileSelectLineEdit)
        self.hash_thread.checksum_sig.connect(self.handle_result)
        self.hash_thread.updateProgressBar.connect(self.progressBar.setValue)
        self.hash_thread.start()
        self.update_gui()

    def update_gui(self) -> None:
        """Update buttons and menus when calculations
        starts or stops, and on Reset."""
        # Get current states
        try:
            hash_thread_running: bool = self.hash_thread.isRunning()
        except AttributeError:  # hash_thread may not have been created yet.
            hash_thread_running = False
        hash_thread_idle: bool = not hash_thread_running
        # Disable QLineEdit's when calculation in progress.
        self.fileSelectLineEdit.setEnabled(hash_thread_idle)
        self.validateLineEdit.setEnabled(hash_thread_idle)
        self.outputLineEdit.setEnabled(hash_thread_idle)
        # Enabled buttons when hash_thread_running
        self.cancelButton.setEnabled(hash_thread_running)
        # Disabled buttons when hash_thread_running
        self.fileAddButton.setEnabled(hash_thread_idle)
        self.outputFileButton.setEnabled(hash_thread_idle)
        self.goButton.setEnabled(hash_thread_idle)
        if hash_thread_running:
            self.progressBar.setStatusTip('Calculating Checksum...')
            self.hashChoiceButton.setEnabled(False)
        else:
            self.progressBar.setStatusTip('Not running')
            # hashChoiceButton remains disabled when validator supplied.
            self.hashChoiceButton.setEnabled(not self.has_validator)
        self.set_reset_state()

    def handle_result(self, name: str, checksum: str) -> None:
        """Handle results and output."""
        alg_name: str = Hp.HASH_STRINGS[self.alg_id]
        txt = (f'<font color="black">File name: {name}\n'
               f'{alg_name} checksum: {checksum}</font>\n')
        self.resultTextBrowser.append(txt)

        if self.has_validator:
            if checksum == self.validateLineEdit.text().lower():
                self.resultTextBrowser.append(
                    '<font color="green"><b>Success. '
                    'Checksum matches the expected value.'
                    '</b></font>')
            else:
                self.resultTextBrowser.append(
                    '<font color="red"><b>Fail. Checksum does not '
                    'match expected value. </b></font>')
        elif len(self.validateLineEdit.text()) > 0:
            self.resultTextBrowser.append(
                '<font color="orange"><b>Warning</b>. The \'Validation\' '
                'text is not a recognised checksum.</font>')
        if len(self.outputLineEdit.text()) > 0:
            output = self.outputLineEdit.text()
            fname = PurePath(name).name  # Name of the processed file
            if PurePath(output).is_absolute():
                try:
                    with open(output, 'wt', encoding='utf8') as fp:
                        fp.write(f'{checksum} {fname}')
                        self.resultTextBrowser.append(
                            f'<font color="black">Result written to '
                            f'{output}</font>\n')
                except FileNotFoundError:
                    self.resultTextBrowser.append(
                        f'<font color="red">{output} '
                        'is not writeable.</font>')
            else:
                self.resultTextBrowser.append(
                            f'<font color="red">Could not write to {output}\n'
                            'Output path is not fully qualified.</font>\n')
        # Update UI on completion.
        self.update_gui()

    def save_result(self) -> None:
        """Save results to file"""
        text = self.resultTextBrowser.toPlainText()
        if text:
            dialogs.save_results(self, text)
        else:
            msg: str = 'No results to print.\nCalculate checksum first.'
            QMessageBox.critical(self, "Error", msg)

    def quit(self) -> None:
        """Shutdown application."""
        prefs.write_settings(self)
        sys.exit()

    def about(self) -> None:
        """Show :py:mod:`'About' <dialogs.about>` dialog"""
        dialogs.about(self, VERSION)

    def file_line_drop_event(self, event) -> None:
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

    def line_validate_drop_event(self, event) -> None:
        """Handle drop event for validateLineEdit."""
        etype = event.mimeData()
        if etype.hasText() and len(etype.text()) > 1:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.validateLineEdit.setText(etype.text())
        else:
            event.ignore()

    def file_select_changed(self) -> None:
        """QLineEdit handler for changed fileSelectLineEdit."""
        has_text: bool = len(self.fileSelectLineEdit.text()) > 0
        self.set_reset_state()
        # Resolve home path shortcut.
        file_select: Path = Path(self.fileSelectLineEdit.text()).expanduser()
        if file_select != Path(self.fileSelectLineEdit.text()):
            self.fileSelectLineEdit.setText(str(file_select))
        # Set goButton state
        is_valid_file = os.path.isfile(self.fileSelectLineEdit.text())
        self.goButton.setEnabled(is_valid_file)
        # Set StatusTips
        if is_valid_file:
            msg = 'File selected.'
            go_button_msg = 'Click to start.'
        elif has_text:
            msg = 'File not found.'
            go_button_msg = 'No file selected.'
        else:
            msg = "No file selected."
            go_button_msg = 'No file selected.'
        self.statusbar.showMessage(msg)
        self.fileSelectLineEdit.setStatusTip(msg)
        self.goButton.setStatusTip(go_button_msg)

    def validator_changed(self) -> None:
        """QLineEdit handler for changed validateLineEdit."""
        self.set_reset_state()
        validate.set_validator(self, self.validateLineEdit.text())
        self.hashChoiceButton.setEnabled(not self.has_validator)
        if self.has_validator:
            hash_from_line: 'tuple[int, str] | None' = (
                validate.hash_from_line(self.validateLineEdit.text()))
            if hash_from_line:  # MyPy doesn't know this must be True.
                msg = f'Auto-selected {Hp.HASH_STRINGS[hash_from_line[0]]}'
        elif len(self.validateLineEdit.text()) == 0:
            msg = 'No validation text entered.'
        else:
            msg = 'Invalid checksum.'
        self.statusbar.showMessage(msg)
        self.validateLineEdit.setStatusTip(msg)

    def output_line_changed(self) -> None:
        """QLineEdit handler for changed outputLineEdit.
        Note: The directory must exist."""
        self.set_reset_state()
        out_file: Path = Path(self.outputLineEdit.text()).expanduser()
        # Resolve home path shortcut.
        if out_file != Path(self.outputLineEdit.text()):
            self.outputLineEdit.setText(str(out_file))
        out_dir: Path = Path(PurePath(out_file).parent)
        if out_dir.is_dir() and not out_file.is_dir():
            msg = f'Write checksum to {out_file}.'
        else:
            msg = 'No output file selected. Output will not be saved.'
        self.statusbar.showMessage(msg)
        self.outputLineEdit.setStatusTip(msg)

    def file_browser(self) -> None:
        """Qt File browser for single file."""
        fname = QFileDialog.getOpenFileName(
            self, 'Select File', self.open_dir)
        if fname[0]:
            self.open_dir = os.path.dirname(str(fname[0]))
            self.fileSelectLineEdit.setText(fname[0])

    def set_outpath(self) -> None:
        """Set the checksum output file path."""
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Save",
            self.save_dir,
            ('Checksum Files (*.md5 *.sha1 *.sha224 *.sha256 *.384 '
             '*.sha512 *.sha);;Text Files (*.txt);;All Files (*)'))
        self.outputLineEdit.setText(fname)

    def set_reset_state(self) -> None:
        """Enable Reset button when there's something to reset and
        calculation QThread is not running."""
        try:
            hash_thread_running: bool = self.hash_thread.isRunning()
        except AttributeError:  # hash_thread may not have been created yet.
            hash_thread_running = False
        hash_thread_idle: bool = not hash_thread_running
        can_reset: bool = (hash_thread_idle and
                           (self.fileSelectLineEdit.text() != '' or
                            self.validateLineEdit.text() != '' or
                            self.outputLineEdit.text() != '' or
                            self.progressBar.value() != 0))
        self.resetButton.setEnabled(can_reset)

    # Button: Stop
    def stop(self) -> None:
        """Stop ChecksumThread."""
        self.hash_thread.stop()
        self.hash_thread.wait()
        self.update_gui()

    # Choice Button: Algorithm
    def set_hash_algorithm(self, choice: int) -> None:
        """hash algorithm setter."""
        self.alg_id = choice
        alg_name = Hp.HASH_STRINGS[choice]
        self.hashChoiceButton.setStatusTip(f'Current algorithm: {alg_name}.')

    def reset_or_clear(self) -> None:
        """Reset GUI."""
        self.fileSelectLineEdit.clear()
        self.validateLineEdit.clear()
        self.outputLineEdit.clear()
        self.resultTextBrowser.clear()
        self.progressBar.setValue(0)
        self.update_gui()
        self.statusbar.showMessage('Reset', 2000)


def file_drag_enter_event(event) -> None:
    """Accept drag enter event if hasUrls"""
    if event.mimeData().hasUrls:
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
    else:
        event.ignore()


def line_validate_enter_event(event) -> None:
    """Accept drag enter event if text"""
    etype = event.mimeData()
    if etype.hasText() and len(etype.text()) > 1:
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
    else:
        event.ignore()


def main() -> None:
    """Create window"""
    app = QApplication(sys.argv)
    window = ShaApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
