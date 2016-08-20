import sys
from PySide import QtCore
from PySide import QtGui

import database

class SettingsMenu(QtGui.QWidget):
    def __init__(self, db, parent=None):
        super(SettingsMenu, self).__init__(parent)
        
        self.db = db

        self.setupUi()

    def setupUi(self):
        self.dirList = QtGui.QListWidget()
        self.refreshDirList()

        self.addDirButton = QtGui.QPushButton()
        self.addDirButton.clicked.connect(self.addDir)
        #Layout
        vBox1 = QtGui.QVBoxLayout()
        vBox1.addWidget(self.dirList)
        vBox1.addWidget(self.addDirButton)

        self.setLayout(vBox1)

    def addDir(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, str("Open Directory"), QtCore.QDir.currentPath())
        self.db.AddDir(dirName)
        self.refreshDirList()

    def refreshDirList(self):
        self.dirList.clear()
        dirs = self.db.GetDirs()
        for dir in dirs:
            self.dirList.addItem(dir[0])
