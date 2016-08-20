import sys
from PySide import QtCore
from PySide import QtGui
import database

class ActiveTagsModel(QtCore.QAbstractListModel):
    def __init__(self, db):
        QtCore.QAbstractListModel.__init__(self)
        self.image = ""
        self.db = db
        self.items = []
        

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()]
        else:
            return

    def setFilterTag(self, tag):
        self.filterTag = tag

    def queryDB(self, imageName):
        itemTags = []
        if imageName != "":
            tempItems = self.db.GetTagsWithImage(imageName)
            for item in tempItems:
                itemTags.append(item)
        return itemTags

    def refresh(self, imageList):
        self.items = []
        firstImage = True
        for image in imageList:
            imageTags = self.queryDB(image)
            if firstImage:
                firstImage = False
                for tag in imageTags:
                    self.items.append(tag)
            else:
                self.items = list(set(self.items) & set(imageTags))
        self.reset()
