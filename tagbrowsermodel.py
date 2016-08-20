import sys
from PySide import QtCore
from PySide import QtGui
import database

class TagBrowserModel(QtCore.QAbstractListModel):
    def __init__(self, db):
        QtCore.QAbstractListModel.__init__(self)

        self.db = db
        self.queryDB()

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()]
        else:
            return
    def setFilterTag(self, tag):
        self.filterTag = tag

    def queryDB(self):
        self.items = []
        tempItems = self.db.GetTagNames()
        for item in tempItems:
            self.items.append(item)

    def refresh(self):
        self.queryDB()
        self.reset()
