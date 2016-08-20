import sqlite3
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbinterface import Base, Image, Tag, Dir

class Database:
    def __init__(self):
        pass

    def LoadDB(self, filename):
        self.engine = create_engine('sqlite:///photag_database.db')
        Base.metadata.bind = self.engine
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
        Base.metadata.create_all(self.engine)

    def AddDir(self, directory):
        if directory == "": return
        dirObj = Dir(dirName = directory)
        self.session.add(dirObj)

    def RemoveDir(self, directory):
        dirObj = self.session.query(Dir).filter(Dir.dirName == directory).one();
        self.session.delete(dirObj)

    def GetDirs(self):
        dirs = self.session.query(Dir).all()
        dirNames = []
        for dir in dirs:
            dirNames.append(dir.dirName)
        return dirNames

    def AddImage(self, fileName):
        imageObj = self.session.query(Image).filter(Image.fileName == fileName).first()
        if not imageObj:
            imageObj = Image(fileName = fileName)
            self.session.add(imageObj)

    def RefreshDirs(self):
        dirs = self.GetDirs()
        for dir in dirs:
            for root, dirs, files in os.walk(dir):
                for name in files:
                    if (name.endswith('.jpg') or name.endswith('.jpeg') or name.endswith('.png')):
                        self.AddImage(os.path.join(root, name))

        images = self.GetImages()
        for image in images:
            if (not os.path.isfile(image)):
                self.session.delete(self.session.query(Image).filter(Image.fileName == image).one())

    def GetImages(self):
        images = self.session.query(Image).all()
        imageNames = []
        for image in images:
            imageNames.append(image.fileName)
        return imageNames
    
    def GetImageObj(self, image):
        return self.session.query(Image).filter(Image.fileName == image).one()

    def GetTagNames(self):
        tags = self.session.query(Tag).all()
        tagNames = []
        for tag in tags:
            tagNames.append(tag.name)
        return tagNames

    def GetImagesWithTag(self, tag):
        images = self.session.query(Image).join(Image.tags).filter(Tag.name == tag).all()
        imageNames = []
        for image in images:
            imageNames.append(image.fileName)
        return imageNames
       
    def GetTagsWithImage(self, image):
        imageObj = self.session.query(Image).filter(Image.fileName == image).one()
        tagNames = []
        for tag in imageObj.tags:
            tagNames.append(tag.name)
        return tagNames
 
    def AddTag(self, tag):
        tag = Tag(name = str(tag))
        self.session.add(tag)

    def DeleteTag(self, tag):
        self.session.delete(self.session.query(Tag).filter(Tag.name == tag).first())

    def TagImage(self, fileName, tag):
        imageObj = self.GetImageObj(fileName)
        tagObj = self.session.query(Tag).filter(Tag.name == tag).one()
        imageObj.tags.append(tagObj)

    def Commit(self):
        self.session.commit()

    def UnTagImage(self, fileName, tag):
        imageObj = self.GetImageObj(fileName)
        tagObj = self.session.query(Tag).filter(Tag.name == tag).one()
        imageObj.tags.remove(tagObj)

    def GetImageRating(self, fileName):
        return self.GetImageObj(fileName).rating

    def SetImageRating(self, fileName, rating):
        self.GetImageObj(fileName).rating = rating
    
    def GetImagesWithRating(self, rating, mode):
        if mode == 1:
            images = self.session.query(Image).filter(Image.rating == rating).all()
        elif mode == 2:
            images = self.session.query(Image).filter(Image.rating > rating).all()
        elif mode == 3:
            images = self.session.query(Image).filter(Image.rating < rating).all()

        imageNames = []
        for image in images:
            imageNames.append(image.fileName)
        return imageNames
            
