import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

ImageTag = Table('tag_association', Base.metadata,
                 Column('image_id', Integer, ForeignKey('image.id')),
                 Column('tag_id', Integer, ForeignKey('tag.id'))
)

class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key = True)
    fileName = Column(Text, unique = True)
    tags = relationship('Tag', secondary='tag_association', backref="images")
    rating = Column(Integer, default=0)

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key = True)
    name = Column(Text)
    #tagName = relationship(TagName, backref=backref('tags', uselist=True))
    #images = relationship('Image', secondary='tag_association', backref="tags")
    
    

class Dir(Base):
    __tablename__ = 'dirs'
    id = Column(Integer, primary_key = True)
    dirName = Column(Text, unique = True)

engine = create_engine('sqlite:///photag_database.db')

Base.metadata.create_all(engine)
