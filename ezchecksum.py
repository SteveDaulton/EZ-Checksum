#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""EZchecksum is a GUI application for calculating and testing checksums."""

import os
import sys

from PyQt4 import QtCore, QtGui

import gui
import hash_profiles as Hp
import prefs
import dialogs
import calc
import validate

VERSION = '0.1.0'


class ShaApp(QtGui.QMainWindow, gui.Ui_MainWindow):
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

    def __init__(self, parent=None):
        super(ShaApp, self).__init__(parent)
        self.setupUi(self)

        # Initialise attributes to defaults
        self.default_open_dir = QtCore.QDir.homePath()
        self.default_save_dir = QtCore.QDir.homePath()
        self.hash_thread = None
        self.has_validator = False  # True when verification hash is valid.

        # Settings
        self.algorithm = Hp.HASH_CODES['SHA256']
        # Data is a QLineEdit
        #  containing the file name(s) to be processed.
        self.data = None

        # Update settings from saved config
        prefs.read_settings(self)

        # Add Drag and drop methods (some methods defined in gui.py)
        self.fileSelectLineEdit.dragEnterEvent = file_drag_enter_event
        self.fileSelectLineEdit.dragMoveEvent = file_drag_move_event
        self.fileSelectLineEdit.dropEvent = self.file_line_drop_event

        # Menu actions
        self.actionSelect_File.triggered.connect(self.file_browser)
        self.actionSave_Result.triggered.connect(self.save_result)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout.triggered.connect(self.about)

        # Button actions
        self.fileAddButton.clicked.connect(self.file_browser)
        self.goButton.clicked.connect(self.run_checksum)
        self.cancelButton.clicked.connect(self.stop)
        self.resetButton.clicked.connect(self.reset_or_clear)
        self.hashChoiceButton.currentIndexChanged.connect(self.set_hash_algorithm)

        # fileSelectLineEdit actions
        self.fileSelectLineEdit.textChanged.connect(self.file_input_text_changed)
        self.validateLineEdit.textChanged.connect(self.validator_changed)


    # Process
    def run_checksum(self):
        """Checksum calculation."""
        # Create a new thread with appropriate parameters
        #self.algorithm = Hp.HASH_CODES['SHA256']  # This should already be set
        self.data = self.fileSelectLineEdit

        ############################
        # If validation string is a valid hash, set the algorithm for hash_thread to match.
        verify_text = self.validateLineEdit.text()
        validate.set_validator(self, verify_text)
        ############################
        # Now create thread
        self.hash_thread = calc.ChecksumThread(self.algorithm, self.data)
        # Connect self.hash_thread object's SIGNAL "checksum" to the method 'add_result()'.
        self.connect(
            self.hash_thread,
            QtCore.SIGNAL("checksum(QString, QString)"),
            self.add_result)
        # Connect SIGNAL updateProgressBar to fileProgressBar
        self.connect(
            self.hash_thread,
            QtCore.SIGNAL("updateProgressBar(int)"),
            self.progressBar.setValue)
        # and start the thread.
        self.hash_thread.start()
        self.update_gui()


    # Close event
    def closeEvent(self, event):
        """Override window close requests."""
        # pylint: disable=invalid-name
        event.ignore()
        self.quit()


    # Update controls and settings
    def update_gui(self):
        """Update buttons and menus."""

        # Get current states
        has_input = len(self.fileSelectLineEdit.text()) > 0
        has_output = len(self.resultTextBrowser.toPlainText()) > 0
        has_verify = len(self.validateLineEdit.text()) > 0

        # Is ChecksumThread running?
        try:
            hash_thread_running = self.hash_thread.isRunning()
        except AttributeError:  # hash_thread may not have been created yet.
            hash_thread_running = False
        hash_thread_idle = not hash_thread_running

        # Set states (most parts of gui are disabled during processing)
        # Note: goButton is handled by file_input_text_changed

        # Enabled when hash_thread_idle
        self.fileSelectLineEdit.setEnabled(hash_thread_idle)
        self.validateLineEdit.setEnabled(hash_thread_idle)
        # Enabled when hash_thread_idle and something to clear.
        can_clear = has_input or has_output or has_verify
        self.resetButton.setEnabled(can_clear and hash_thread_idle)
        # Enabled when hash_thread_running
        self.cancelButton.setEnabled(hash_thread_running)

        self.hashChoiceButton.setEnabled(hash_thread_idle and not self.has_validator)

    # Write to Output
    def add_result(self, name, checksum):
        """Handle checksum results."""
        txt = 'File name: ' + name + '\n' +\
              Hp.HASH_TYPES[self.algorithm]['name'] +\
              ' checksum: ' + checksum + '\n'

        self.resultTextBrowser.append(txt)

        ##############
        # Validate
        # Compare 'checksum' with the expected value(s) from
        # validation thread.
        # self.val_thread.join()  # block until we have the validator.

        if self.has_validator:
            if checksum == self.validateLineEdit.text():
                self.resultTextBrowser.append(
                    '<font color="#009900"><b>Success. Checksum matches the expected value.'
                    '</b></font>')
            else:
                self.resultTextBrowser.append(
                    '<font color="red"><b>Fail. Checksum does not match expected value.'
                    '</b></font>')
        elif len(self.validateLineEdit.text()) > 0:
            self.resultTextBrowser.append(
                '<b>Warning. The \'Validation\' text is not '
                'a recognised checksum.</b>')

        ##############
        self.update_gui()


    ###############
    # Event handlers:
    ###############

    # Menu Handlers:
    ################

    # Menu: File > Save Result.
    def save_result(self):
        """Save results to file"""
        text = self.resultTextBrowser.toPlainText()

        if not text:
            dialogs.critical(
                self,
                'No results to print.\nCalculate checksum first.')
            return
        dialogs.save_results(self, text)

    # Menu: File > Quit
    def quit(self):
        """Shutdown application."""
        if dialogs.dialog('Close EZ Checksum?', choice=True):
            prefs.write_settings(self)
            sys.exit()

    # Menu: Help > About
    def about(self):
        """Show :py:mod:`'About' <dialogs.about>` dialog"""
        dialogs.about(self, VERSION)


    # Drag and drop handlers:
    #######################

    def file_line_drop_event(self, event):
        """Handle fileSelectLineEdit drop events"""
        if event.mimeData().hasText():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            self.fileSelectLineEdit.setText(event.mimeData().text())
        elif event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            file_ = str(event.mimeData().urls()[0].toLocalFile())
            if os.path.isfile(file_):
                self.fileSelectLineEdit.setText(file_)

    def file_list_drop_event(self, event):
        """Handle fileSelectQListWidget drop events"""
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                path = str(url.toLocalFile())
                if not os.path.islink(path):
                    if os.path.isfile(path):
                        item = QtGui.QListWidgetItem(path)
                        self.fileSelectQListWidget.addItem(item)
                    else:
                        # Can this happen?
                        dialogs.warning(self, 'Unsupported URL')
        else:
            event.ignore()


    # Line Edit handlers
    def file_input_text_changed(self):
        """QLineEdit handler for typed input.

        Sets goButton state: Enabled when file input string is a valid file.
        """
        is_valid_file = os.path.isfile(self.fileSelectLineEdit.text())
        self.goButton.setEnabled(is_valid_file)
        if is_valid_file:
            self.goButton.setToolTip('Click to start processing')
            self.goButton.setStatusTip('File selected')

        else:
            self.goButton.setToolTip('Select file first')
            self.goButton.setStatusTip('No file selected')
        self.update_gui()

    def validator_changed(self):
        """QLineEdit handler for typed validator.

            Update GUI if resetButton state may need changing, if either:

            a. resetButton was enabled and validateLineEdit is now empty,
            b. resetButton was disabled and validateLineEdit is not now empty.
        """
        # set_validator bails very quickly if wrong number of characters
        validate.set_validator(self, self.validateLineEdit.text())

        if self.resetButton.isEnabled():
            if len(self.validateLineEdit.text()) == 0:
                self.update_gui()
        elif len(self.validateLineEdit.text()) > 0:
            self.update_gui()


    # Button handlers
    ################

    # Button: Add File
    def file_browser(self):
        """Qt File browser for single file."""
        fname = QtGui.QFileDialog.getOpenFileName(
            self, 'Select File', self.default_open_dir)
        if fname:
            self.default_open_dir = os.path.dirname(str(fname))
            self.fileSelectLineEdit.setText(fname)

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
        self.hashChoiceButton.setStatusTip("Current algorithm: " + alg_name)


    # Button: Reset / Clear
    def reset_or_clear(self):
        """Reset GUI."""
        self.fileSelectLineEdit.clear()
        self.validateLineEdit.clear()
        self.resultTextBrowser.clear()
        self.update_gui()



def number_of_files(path):
    """Return the number of files in a directory
    including subdirectories."""
    return sum([len(files) for _, _, files in os.walk(path)])

def file_drag_enter_event(event):
    """Accept drag enter event if hasUrls"""
    if event.mimeData().hasUrls:
        event.accept()
    else:
        event.ignore()

def file_drag_move_event(event):
    """Accept move event if hasUrls"""
    if event.mimeData().hasUrls:
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
    else:
        event.ignore()



def main():
    """Create window"""
    app = QtGui.QApplication(sys.argv)
    window = ShaApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
