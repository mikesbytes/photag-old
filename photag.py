#!/usr/bin/python

import sys
from PySide import QtCore
from PySide import QtGui
import subprocess
import shutil
import os

import database
import imageviewmodel
import settingsmenu
import imagefixer
import tagbrowsermodel
import activetagsmodel

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #init variables
        self.currentPreviewFile = ""

        self.db = database.Database()
        self.db.LoadDB("test.db")

        self.setupUi()


    def setupUi(self):
        self.statusBar().showMessage('Ready')

        #Menu Bar
        openAction = QtGui.QAction('Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open a file')
        openAction.triggered.connect(self.open)

        settingsAction = QtGui.QAction('Settings', self)
        settingsAction.setShortcut('Ctrl+P')
        settingsAction.triggered.connect(self.showSettings)

        syncAction = QtGui.QAction('Sync DB', self)
        syncAction.setShortcut('Ctrl+U')
        syncAction.setStatusTip('Grab changes in watched directories')
        syncAction.triggered.connect(self.db.RefreshDirs)

        fixAction = QtGui.QAction('Fix Images', self)
        fixAction.setStatusTip('Fix broken images with ImageMagick')
        fixAction.setShortcut('Ctrl+F')
        fixAction.triggered.connect(self.fixImages)

        exportAction = QtGui.QAction('Export', self)
        exportAction.setStatusTip('Export current query to folder')
        exportAction.triggered.connect(self.export)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(settingsAction)
        fileMenu.addAction(syncAction)
        fileMenu.addAction(fixAction)
        fileMenu.addAction(exportAction)

        togglePreviewScalingAction = QtGui.QAction('Toggle Scaling', self)
        togglePreviewScalingAction.triggered.connect(self.TogglePreviewMode)

        previewMenu = menuBar.addMenu('&Preview')
        previewMenu.addAction(togglePreviewScalingAction)

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(1)
        self.previewFitted = False

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)

        #main image list on the left side of the screen
        self.imageList = QtGui.QListView()
        self.imageList.setUniformItemSizes(True)
        imageListModel = imageviewmodel.ImageListModel(self.db)
        self.imageList.setModel(imageListModel)
        self.imageList.setSelectionMode(QtGui.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.imageListSelMod = self.imageList.selectionModel()
        self.imageListSelMod.currentRowChanged.connect(self.changeImagePreview)
        self.imageListSelMod.selectionChanged.connect(self.RefreshActiveTags)

        self.tagBrowser = QtGui.QListView()
        tagBrowserModel = tagbrowsermodel.TagBrowserModel(self.db)
        self.tagBrowser.setModel(tagBrowserModel)
        self.tagBrowser.doubleClicked.connect(self.TagImage)

        self.newTagButton = QtGui.QPushButton("New")
        self.newTagButton.clicked.connect(self.NewTag)
        self.delTagButton = QtGui.QPushButton("Del")
        self.delTagButton.clicked.connect(self.DelTag)

        self.activeTags = QtGui.QListView()
        activeTagsModel = activetagsmodel.ActiveTagsModel(self.db)
        self.activeTags.setModel(activeTagsModel)
        self.activeTags.doubleClicked.connect(self.UnTagImage)

        self.filterInput = QtGui.QLineEdit()
        self.filterInput.editingFinished.connect(self.ChangeFilter)
        self.imageCountLabel = QtGui.QLabel("Items: 0")

        self.imageRatingBox = QtGui.QSpinBox()
        self.imageRatingBox.setMaximum(5)
        self.imageRatingBox.setMinimum(0)
        self.imageRatingBox.valueChanged.connect(self.UpdateRating)

        #Layout
        mainWidget = QtGui.QWidget()
        hBox1 = QtGui.QHBoxLayout()
        vBox2 = QtGui.QVBoxLayout()

        vSplit1 = QtGui.QSplitter()
        vSplit1.setOrientation(QtCore.Qt.Vertical)

        imageListLayout = QtGui.QVBoxLayout()
        imageListLayout.addWidget(self.imageList)
        imageListLayout.addWidget(self.imageCountLabel)
        imageListLayout.addWidget(self.imageRatingBox)

        imageListWidget = QtGui.QWidget()
        imageListWidget.setLayout(imageListLayout)

        vSplit1.addWidget(imageListWidget)
        vSplit1.addWidget(self.scrollArea)

        vSplit2 = QtGui.QSplitter()
        vSplit2.setOrientation(QtCore.Qt.Vertical)
        vSplit2.addWidget(self.activeTags)

        vBox1 = QtGui.QVBoxLayout()
        vBox1.addWidget(QtGui.QLabel("Tag Browser"))
        vBox1.addWidget(self.tagBrowser)
        hBox2 = QtGui.QHBoxLayout()
        hBox2.addWidget(self.newTagButton)
        hBox2.addWidget(self.delTagButton)
        vBox1.addLayout(hBox2)
        tagBrowserFrame = QtGui.QFrame()
        tagBrowserFrame.setLayout(vBox1)
        vSplit2.addWidget(tagBrowserFrame)

        hBox1.addWidget(vSplit1)
        hBox1.addWidget(vSplit2)

        vBox2.addWidget(self.filterInput)
        vBox2.addLayout(hBox1)

        mainWidget.setLayout(vBox2)
        self.setCentralWidget(mainWidget)

    def export(self):
        print("exporting current selection")
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'path')
        if ok and text != "":
            selections = self.imageList.selectedIndexes()
            for selection in selections:
                shutil.copy(selection.data(), text)

    def open(self):
        subprocess.Popen(["feh", self.previewFile])

    def changeImagePreview(self, current, previous):
        self.previewFile = current.data()
        self.UpdatePreview()

    def showSettings(self):
        self.settingsMenu = settingsmenu.SettingsMenu(self.db)
        self.settingsMenu.show()

    def fixImages(self):
        imagefixer.fixImages(self.db.GetImages())

    def NewTag(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter new tag:')
        if ok and text != "":
            self.db.AddTag(text)
            self.db.Commit()
            self.tagBrowser.model().refresh()

    def DelTag(self):
        self.db.DeleteTag(self.tagBrowser.selectionModel().currentIndex().data())
        self.tagBrowser.model().refresh()

    def UpdatePreview(self):
        if (self.previewFile != '' and self.previewFile != self.currentPreviewFile):
            self.currentPreviewFile = self.previewFile
            if not os.path.isfile(self.previewFile):
                print("Image does not exist!")
            pixmap = QtGui.QPixmap(self.previewFile)
            self.imageLabel.setPixmap(pixmap)

        if (self.previewFitted):
            self.scrollArea.setWidgetResizable(True)
        else:
            self.scrollArea.setWidgetResizable(False)
            self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
            self.imageLabel.resize(pixmap.size())
        self.imageRatingBox.setValue(self.db.GetImageRating(self.previewFile))


    def TogglePreviewMode(self):
        self.previewFitted = not self.previewFitted

    def TagImage(self, tag):
        selections = self.imageList.selectedIndexes()
        for selection in selections:
            self.db.TagImage(selection.data(), tag.data())
        self.db.Commit()
        self.RefreshActiveTags(self.imageList.selectionModel().currentIndex(), None)

    def UnTagImage(self, tag):
        selections = self.imageList.selectedIndexes()
        for selection in selections:
            self.db.UnTagImage(selection.data(), tag.data())
        self.db.Commit()
        self.RefreshActiveTags(self.imageList.selectionModel().currentIndex(), None)

    def RefreshActiveTags(self, current, previous):
        selections = self.imageList.selectedIndexes()
        selectedImages = []
        for i in selections:
            selectedImages.append(i.data())
        self.activeTags.model().refresh(selectedImages)

    def ChangeFilter(self):
        self.imageListSelMod.model().setQueryFilter(self.filterInput.text())
        self.imageListSelMod.model().refresh()
        self.imageCountLabel.setText("Items: " + str(self.imageListSelMod.model().rowCount()))

    def UpdateRating(self, newRating):
        self.db.SetImageRating(self.previewFile, newRating)
        self.db.Commit()


def main():
    app = QtGui.QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()

if __name__ == "__main__":
    main()
