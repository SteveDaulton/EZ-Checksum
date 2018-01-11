"""Additional dialogs used by the application"""

from PyQt4.QtGui import QMessageBox as QMsgBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QDialog

def warning(parent, message):
    """A simple warning message, Returns True on OK."""
    return QMsgBox.warning(parent, "Warning", message) == QMsgBox.Ok

def about(parent, version):
    """About dialog"""
    message = (r"""<strong>EZ Checksum version {version}</strong><br>
&nbsp;&nbsp;&nbsp;December 2017.<br>
&nbsp;&nbsp;&nbsp;<i>by Steve Daulton.</i>
<p>Website: <a href="https://easyspacepro.com">EasySpacePro.com</a><br>
Released under terms of the
<a href="https://www.gnu.org/licenses/gpl.html">GPLv3</a>.</p>""")
    message = message.format(version=version)
    QMsgBox.about(parent, "EZ Checksum", message)


def critical(parent, message):
    """A simple error message, Returns True on OK."""
    return QMsgBox.critical(parent, "Error", message) == QMsgBox.Ok

def dialog(message, title='Warning', more='', details='', choice=False):
    """A simple message box.
    Returns True if Ok / Yes, otherwise False.
    """
    msg_box = QMsgBox()
    msg_box.setIcon(QMsgBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle(title)
    if more:
        msg_box.setInformativeText(more)
    if details:
        msg_box.setDetailedText(details)
    msg_box.setEscapeButton(QMsgBox.Cancel)
    if choice:
        msg_box.setStandardButtons(QMsgBox.Yes | QMsgBox.No)
        return msg_box.exec_() == QMsgBox.Yes
    else:
        msg_box.setStandardButtons(QMsgBox.Ok)
        return msg_box.exec_() == QMsgBox.Ok

def modeless_dialog(parent, message, title='Warning', more='', details=''):
    """A simple non-modal message box"""
    msg_box = QMsgBox(parent)
    msg_box.setIcon(QMsgBox.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    if more:
        msg_box.setInformativeText(more)
    if details:
        msg_box.setDetailedText(details)
    msg_box.setStandardButtons(QMsgBox.Ok)
    # In modeless QMessageBox, setEscapeButton must be set after setStandardButtons
    msg_box.setEscapeButton(QMsgBox.Ok)
    msg_box.show()

def save_results(parent, text):
    """Save results to file dialog"""
    dlog = QFileDialog()
    dlog.setAcceptMode(QFileDialog.AcceptSave)
    dlog.setFilter('Text Files (*.txt);;Log Files (*.log);;All Files (*)')
    dlog.setFileMode(QFileDialog.AnyFile)
    dlog.setDefaultSuffix('txt')
    dlog.setDirectory(parent.default_save_dir)
    # Check user didn't cancel
    if dlog.exec_() == QDialog.Accepted:
        parent.default_save_dir = dlog.directory().path()
        # Ensure '.log' suffix if Log File filter selected and no filter provided.
        # On Windows / Mac perhaps we should force the file extension?
        if dlog.selectedNameFilter() == 'Log Files (*.log)':
            dlog.setDefaultSuffix('log')
        try:
            _file = open(dlog.selectedFiles()[0], 'w')
        except IOError as err:
            detail_msg = 'I/O error: {0}\n{1}'.format(err.errno, err.strerror)
            dialog('File write error.', title='Error', details=detail_msg)
            return
        _file.write(text)
        _file.close()
