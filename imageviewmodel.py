import sys
from PySide import QtCore
from PySide import QtGui
import database
import re

class ImageListModel(QtCore.QAbstractListModel):
    def __init__(self, db):
        QtCore.QAbstractListModel.__init__(self)

        self.db = db
        self.queryFilter = ""
        self.queryDB()

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()]
        else:
            return

    def setQueryFilter(self, queryFilter):
        self.queryFilter = queryFilter

    def addItems(self, itemsToAdd, mode=0): #0 = AND, 1 = OR
        if (self.items == []):
            self.items = itemsToAdd
        else:
            for item in itemsToAdd:
                self.items = list(set(self.items) & set(itemsToAdd))


    def queryDB(self):
        #Query all images in db
        self.items = []
        if self.queryFilter == "": 
            
            self.addItems(self.db.GetImages())
        else:
            if ';' in self.queryFilter:
                advancedQuery = True
                ratingMode = 0 #0 = none, 1 = equal, 2 = grthan, 3 = lthan
                ratingVal = 0
                reqTags = []
                excTags = []
                optTags = []
                splitQuery = self.queryFilter.split(';')
                for segment in splitQuery:
                    tagtype = 0
                    segment = segment.strip()
                    # identify which things to look for
                    if segment.startswith('RT'):
                        clippedSeg = segment[2:]
                        if clippedSeg.startswith('_EQ'):
                            ratingMode = 1
                        elif clippedSeg.startswith('_GR'):
                            ratingMode = 2
                        elif clippedSeg.startswith('_LT'):
                            ratingMode = 3
                        clippedSeg = clippedSeg[3:]
                        clippedSeg = clippedSeg.strip()
                        ratingVal = int(clippedSeg)
                        self.addItems(self.db.GetImagesWithRating(ratingVal, ratingMode))
                    if segment.startswith('TAG'):
                        clippedSeg = segment[7:]
                        tagSplit = clippedSeg.split(",")
                        strippedTags = []
                        for tag in tagSplit:
                            strippedTags.append(tag.strip())
                        if segment.startswith('TAG_REQ'):
                            for tag in strippedTags:
                                self.addItems(self.db.GetImagesWithTag(tag))
                        if segment.startswith('TAG_ONL'):
                            tempItems = []
                            finalItems = []
                            for tag in strippedTags:
                                if tempItems == []:
                                    tempItems = self.db.GetImagesWithTag(tag)
                                else:
                                    tempItems = list(set(tempItems) & set(self.db.GetImagesWithTag(tag)))
                            for item in tempItems:
                                itemTags = self.db.GetTagsWithImage(item)
                                goodImg = True
                                for itemTag in itemTags:
                                    if not itemTag in strippedTags:
                                        goodImg = False
                                        break
                                if goodImg:
                                    finalItems.append(item)
                            self.addItems(finalItems) 
                            
                    
            else:
                tempItems = self.db.GetImagesWithTag(self.queryFilter)
                self.items = []
                for item in tempItems:
                    self.items.append(item)
            """
            advancedQuery = False
            excTags = []
            reqTags = []
            optTags = []
            if "REQ" in self.queryFilter:
                advancedQuery = True
                reqTagString = self.queryFilter[self.queryFilter.find("REQ") + 3:]
                if "OPT" in self.queryFilter:
                    reqTagString = reqTagString[:reqTagString.find("OPT")]
                if "EXC" in self.queryFilter:
                    reqTagString = reqTagString[:reqTagString.find("EXC")]
                reqTagsSplit = reqTagString.split(",")
                for tag in reqTagsSplit:
                    reqTags.append(tag.strip())
                print (reqTags)
            if "OPT" in self.queryFilter:
                advancedQuery = True
                tagString = self.queryFilter[self.queryFilter.find("REQ") + 3:]
                if "REQ" in self.queryFilter:
                    tagString = reqTagString[:tagString.find("REQ")]
                if "EXC" in self.queryFilter:
                    tagString = tagString[:reqTagString.find("EXC")]
                tagsSplit = tagString.split(",") 
                for tag in tagsSplit:
                    optTags.append(tag.strip())
            if "EXC" in self.queryFilter:
                advancedQuery = True
                advancedQuery = True
                tagString = self.queryFilter[self.queryFilter.find("EXC") + 3:]
                if "REQ" in tagString:
                    tagString = reqTagString[:tagString.find("REQ")]
                if "OPT" in tagString:
                    tagString = tagString[:reqTagString.find("OPT")]
                tagsSplit = tagString.split(",") 
                for tag in tagsSplit:
                    excTags.append(tag.strip())
                print(excTags)
            if not advancedQuery:
                tempItems = self.db.GetImagesWithTag(self.queryFilter)
                self.items = []
                for item in tempItems:
                    self.items.append(item)
            else:
                #advanced query!
                self.items = []
                firstRun = True
                if reqTags == []:
                    for item in self.db.GetImages():
                        self.items.append(item)
                for tag in reqTags:
                    if firstRun:
                        firstRun = False
                        tempItems = self.db.GetImagesWithTag(tag)
                        for item in tempItems:
                            self.items.append(item)
                    else:
                        newItemsTemp = self.db.GetImagesWithTag(tag)
                        newItems = []
                        for item in newItemsTemp:
                            newItems.append(item)
                        self.items = list(set(newItems) & set(self.items))
                for tag in excTags:
                    print(tag)
                    tempItems = self.db.GetImagesWithTag(tag)
                    excItems = []
                    for item in tempItems:
                        if item[0] in self.items:
                            self.items.remove(item[0])
            """
    def refresh(self):
        self.queryDB()
        self.items.sort()
        self.reset()
