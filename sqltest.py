#!/usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbinterface import Base, Image, Tag, Dir

import dbold
import database

engine = create_engine('sqlite:///photag_database.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
#session.autoflush = False
Base.metadata.create_all(engine)

db = database.Database()
db.LoadDB("asd.db")

print(db.GetDirs())
#print(db.GetTagNames())
print(db.GetImagesWithTag('People.Mia'))
print(db.GetTagsWithImage('/home/michael/pictures/cs/final/2015/01/12/14:08:32.jpg'))

"""
db = dbold.Database()
db.LoadDB("test.db")

images = db.GetImages()
for image in images:
    newImage = Image(fileName = image[1])
    session.add(newImage)

tags = db.GetTagNames()
for tag in tags:
    newTag = Tag(name = tag[1])
    taggedImages = db.GetImagesWithTag(tag[1])
    for image in taggedImages:
        imageObj = session.query(Image).filter(Image.fileName == image[0]).one();
        imageObj.tags.append(newTag)
    session.add(newTag)

dirs = db.GetDirs()
for dir in dirs:
    dirObj = Dir(dirName = dir[0])
    session.add(dirObj)

session.commit()
"""
