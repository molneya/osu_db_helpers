
import os, threading
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox, QHBoxLayout, QVBoxLayout, QMessageBox, QStatusBar

import dates, stars, purge
from capture import Capturing

class OsuDbHelpersWidget(QMainWindow):
    message = Signal(QMessageBox.Icon, str, str)
    status = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("osu! db helpers gui")
        self.resize(500, 240)
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout(self.widget)

        self.directoryLineEdit = QLineEdit(placeholderText="osu! Directory")
        self.directoryPushButton = QPushButton("Change")
        self.directoryPushButton.clicked.connect(self.changeDirectory)
        self.addWidgetsToLayout(self.directoryLineEdit, self.directoryPushButton)

        self.starsCheckBox = self.createCheckBoxLabel("Update Stars", "<p>Updates the stars for all beatmaps and modes to the latest ranked version.</p>")
        self.datesCheckBox = self.createCheckBoxLabel("Sort Date Added by Ranked Time", "<p>This overwrites the file modification times of your maps to the ranked time, allowing you to sort by ranked date in game by using the Date Added sort. If you use this sort often, it will break.</p>")
        self.purgeCheckBoxes = []

        for mode in ("osu!", "osu!taiko", "osu!catch", "osu!mania"):
            purgeCheckBox = self.createCheckBoxLabel(f"Purge all {mode} beatmaps")
            self.purgeCheckBoxes.append(purgeCheckBox)

        self.startPushButton = QPushButton("Start")
        self.startPushButton.clicked.connect(self.start)
        self.addWidgetsToLayout(self.startPushButton)

        self.message.connect(self.showMessageBox)
        self.status.connect(self.updateStatus)
        self.status.emit("Ready!")

    @Slot(str)
    def updateStatus(self, message):
        '''
        Updates the status bar with message.
        '''
        self.statusBar().showMessage(message)

    @Slot(QMessageBox.Icon, str, str)
    def showMessageBox(self, icon, title, message):
        '''
        Shows message box with message.
        '''
        messageBox = QMessageBox(icon, title, message, parent=self)
        messageBox.exec()

    def createCheckBoxLabel(self, text, tooltip=None):
        '''
        Creates a option with checkbox.
        '''
        checkBox = QCheckBox()
        label = QLabel(text)
        label.setToolTip(tooltip)
        label.mousePressEvent = lambda x: checkBox.setChecked(not checkBox.isChecked())
        self.addWidgetsToLayout(checkBox, label, addStretch=True)
        return checkBox

    def addWidgetsToLayout(self, *widgets, addStretch=False):
        '''
        Helper to add widgets to a main layout.
        '''
        newLayout = QHBoxLayout()
        self.layout.addLayout(newLayout)

        for widget in widgets:
            newLayout.addWidget(widget)

        if addStretch:
            newLayout.addStretch()

    def changeDirectory(self):
        '''
        Updates the file location in directoryLineEdit.
        '''
        dir = QFileDialog.getExistingDirectory(self, "Open osu! folder", "", QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.directoryLineEdit.setText(dir)

    def start(self):
        '''
        Checks values before starting the osu! db functions.
        '''
        # Final warning to user to back up before running
        messageBox = QMessageBox(QMessageBox.Warning, "Warning", "If you haven't done so, back up your stuff before continuing. I am not responsible for any database corruption or data loss you may experience. If you understand, click OK to continue.", QMessageBox.Ok | QMessageBox.Cancel)
        if messageBox.exec() == QMessageBox.Cancel:
            return

        # Get osu! database and Songs folder location
        osu_dir = self.directoryLineEdit.text()
        osu_db_path = os.path.join(osu_dir, "osu!.db")
        osu_songs_dir = os.path.join(osu_dir, "Songs")

        # Get selected options
        update_stars = self.starsCheckBox.isChecked()
        update_dates = self.datesCheckBox.isChecked()
        purge_modes = []

        for i, purgeCheckBox in enumerate(self.purgeCheckBoxes):
            if purgeCheckBox.isChecked():
                purge_modes.append(i)

        try:
            if not os.path.isfile(osu_db_path):
                raise ValueError("osu!.db not found. Did you supply the right directory?")
            if not os.path.isdir(osu_songs_dir):
                raise ValueError("Songs folder not found. Did you supply the right directory?")
            if not (update_dates or update_stars or purge_modes):
                raise ValueError("No options selected. Please select an option and try again.")

        except Exception as err:
            self.status.emit(f"Exited with exception: {err}")
            self.message.emit(QMessageBox.Critical, "Exception", str(err))
            return

        else:
            threading.Thread(target=self.worker, args=(osu_db_path, osu_songs_dir, purge_modes, update_dates, update_stars), daemon=True).start()

    def worker(self, osu_db_path, osu_songs_dir, purge_modes, update_dates, update_stars):
        '''
        The function that runs the actual osu! db functions.
        '''
        self.startPushButton.setEnabled(False)
        capturing = Capturing()
        capturing.on_readline(lambda status: self.status.emit(status))
        capturing.start()

        try:
            if purge_modes:
                purge.run(osu_db_path, osu_songs_dir, purge_modes)
            if update_dates:
                dates.run(osu_db_path, osu_songs_dir)
            if update_stars:
                stars.run(osu_db_path)

        except Exception as err:
            self.status.emit(f"Exited with exception: {err}")
            self.message.emit(QMessageBox.Critical, "Exception", str(err))

        else:
            self.status.emit("Completed successfully!")
            self.message.emit(QMessageBox.Information, "Completed", "Completed successfully!")

        finally:
            capturing.stop()
            self.startPushButton.setEnabled(True)
