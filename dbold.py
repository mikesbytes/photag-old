import sqlite3
import os

class Database:
    def __init__(self):
        pass

    def LoadDB(self, filename):
        if (not os.path.isfile(filename)):
            self.connection = sqlite3.connect(filename)

            cur = self.connection.cursor()

            cur.execute("create table if not exists images (id INTEGER PRIMARY KEY AUTOINCREMENT, file TEXT UNIQUE)")
            cur.execute("create table if not exists tagNames (id INTEGER PRIMARY KEY, tag TEXT)")
            cur.execute("create table if not exists tags (tag INTEGER, image INTEGER)")
            cur.execute("create table if not exists dirs (dir TEXT UNIQUE)")
        else:
            self.connection = sqlite3.connect(filename)

    def AddDir(self, directory):
        if directory == "": return
        cur = self. connection.cursor()
        cur.execute("INSERT INTO dirs VALUES(\"" + directory + "\")")
        self.connection.commit()

    def RemoveDir(self, directory):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM dirs WHERE dir=\"" + directory + "\"")
        self.connection.commit()

    def GetDirs(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM dirs")
        return cur.fetchall()

    def RefreshDirs(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM dirs")
        rows = cur.fetchall()
        for row in rows:
            for root, dirs, files in os.walk(row[0]):
                for name in files:
                    if (name.endswith('.jpg') or name.endswith('.jpeg') or name.endswith('.png')):
                        cur.execute("SELECT EXISTS(SELECT 1 FROM images WHERE file=\"" + os.path.join(root, name) + "\" LIMIT 1)")
                        if (cur.fetchone()[0] == 0):
                            cur.execute("INSERT INTO images (file) VALUES (\"" + os.path.join(root, name) + "\")")
        self.connection.commit()

        cur.execute("SELECT * FROM images")
        rows = cur.fetchall()
        for row in rows:
            if (not os.path.isfile(row[1])):
                cur.execute("DELETE FROM images WHERE file=\"" + row[1] + "\"")

        self.connection.commit()

    def GetImages(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM images")
        return cur.fetchall()
    
    def GetTags(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM tags")
        return cur.fetchall()

    def GetTagNames(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM tagNames ORDER BY tag")
        return cur.fetchall()

    def GetImagesWithTag(self, tag):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM tagNames WHERE tag=? LIMIT 1", (tag,)) 
        tagID = cur.fetchone()[0]
        print(tagID)
        cur.execute("SELECT file FROM images AS I JOIN tags AS T ON T.image=I.id AND T.tag=?", (tagID,))
        return cur.fetchall()

    def GetTagsWithImage(self, image):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM images WHERE file=? LIMIT 1", (image,))
        imageID = cur.fetchone()[0]
        cur.execute("SELECT N.tag FROM tags AS T JOIN tagNames AS N ON T.tag=N.id AND T.image=?", (imageID,))
        return cur.fetchall()

    def AddTag(self, tag):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO tagNames (tag) VALUES (?)", (tag,))
        self.connection.commit()

    def DeleteTag(self, tag):
        cur = self.connection.cursor()
        cur.execute("SELECT 1 FROM tagNames WHERE tag=? LIMIT 1", (tag,)) 
        tagID = cur.fetchone()[0]
        cur.execute("DELETE FROM tagNames WHERE tag=?", (tag,))
        cur.execute("DELETE FROM tags WHERE tag=?", (tagID,))
        self.connection.commit()

    def TagImage(self, fileName, tag):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM images WHERE file=? LIMIT 1", (fileName,))
        imageID = cur.fetchone()[0]
        print(imageID)
        cur.execute("SELECT * FROM tagNames WHERE tag=? LIMIT 1", (tag,))
        tagID = cur.fetchone()[0]
        print(tagID)
        cur.execute("INSERT INTO tags (tag, image) VALUES (?,?)", (tagID, imageID))

    def Commit(self):
        self.connection.commit()

    def UnTagImage(self, fileName, tag):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM images WHERE file=? LIMIT 1", (fileName,))
        imageID = cur.fetchone()[0]
        print(imageID)
        cur.execute("SELECT * FROM tagNames WHERE tag=? LIMIT 1", (tag,))
        tagID = cur.fetchone()[0]
        print(tagID)
        cur.execute("DELETE FROM tags WHERE tag=? AND image=?", (tagID, imageID))

