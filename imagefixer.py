#Function for fixing broken images

import sys
from PySide import QtCore
from PySide import QtGui
import os

def fixImage(fileName):
    image = QtGui.QImage(fileName)
    if image.isNull() and os.path.isfile(fileName): #It's broken
        os.system('convert ' + fileName + ' ' + fileName) #fix with imageMagick by rexporting

def fixImages(images):
    for image in images:
        fixImage(image[1])

