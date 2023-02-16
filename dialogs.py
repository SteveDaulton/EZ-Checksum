"""Additional dialogs used by the application"""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QDialog


def warning(parent, message) -> None:
    """A simple warning message, Returns True on OK."""
    QMessageBox.warning(parent, "Warning", message)


def about(parent, version) -> None:
    """About dialog"""
    message = r"""<strong>EZ Checksum version {version}</strong><br>
&nbsp;&nbsp;&nbsp;January 2023.<br>
&nbsp;&nbsp;&nbsp;<i>by Steve Daulton.</i>
<p>Website: <a href="https://easyspacepro.com">EasySpacePro.com</a><br>
Released under terms of the
<a href="https://www.gnu.org/licenses/gpl.html">GPLv3</a>.</p>"""
    message = message.format(version=version)
    QMessageBox.about(parent, "EZ Checksum", message)


def dialog(message, title='Warning', more='',
           details='', choice=False) -> bool:
    """A simple message box.
    Returns True if Ok / Yes, otherwise False.
    """
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle(title)
    if more:
        msg_box.setInformativeText(more)
    if details:
        msg_box.setDetailedText(details)
    msg_box.setEscapeButton(QMessageBox.StandardButton.Cancel)
    if choice:
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes |
                                   QMessageBox.StandardButton.No)
        return msg_box.exec() == QMessageBox.StandardButton.Yes
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return msg_box.exec() == QMessageBox.StandardButton.Ok


def save_results(parent, text) -> None:
    """Save results to file dialog"""
    dlog = QFileDialog()
    dlog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    dlog.setNameFilter('Text Files (*.txt);;Log Files (*.log);;All Files (*)')
    dlog.setFileMode(QFileDialog.FileMode.AnyFile)
    dlog.setDefaultSuffix('txt')
    dlog.setDirectory(parent.save_dir)
    # Check user didn't cancel
    if dlog.exec() == QDialog.DialogCode.Accepted:
        parent.save_dir = dlog.directory().path()
        # Ensure '.log' suffix if Log File filter selected
        # and no filter provided.
        # On Windows / Mac perhaps we should force the file extension?
        if dlog.selectedNameFilter() == 'Log Files (*.log)':
            dlog.setDefaultSuffix('log')
        fname = dlog.selectedFiles()[0]
        try:
            with open(fname, 'w', encoding='utf8') as _file:
                _file.write(text)
        except IOError as err:
            detail_msg = f'I/O error: {err.errno}\n{err.strerror}'
            dialog('File write error.', title='Error', details=detail_msg)
