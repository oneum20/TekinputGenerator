# Copyright 2020 by Chua Teck Lee.
# All rights reserved.

import sqlite3
from sqlite3 import Error

import Utility

class Input():
    def __init__(self, name, filepath, display, fileDisplay, buttonLayout, characterList):
        self.name = name
        self.filepath = filepath
        self.display = display
        self.fileDisplay = fileDisplay
        self.buttonLayout = buttonLayout
        self.characterList = characterList

def create_connection(db_file):
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

# Data
Inputs = []

conn = create_connection(Utility.MakePath(r'\..\database.db'))
cur = conn.cursor()
cur.execute("SELECT * FROM Inputs")

rows = cur.fetchall()

for row in rows:
    if(row[5] != None):
        Inputs.append(Input(row[0], row[1], row[2], row[3], tuple(eval(row[4])), row[5].split(',')))
    else:
        Inputs.append(Input(row[0], row[1], row[2], row[3], tuple(eval(row[4])), row[5]))

# Add 'SPACE' input
Inputs.append(Input(
    name='SPACE',
    filepath=r"\Images\Inputs\space.png",  # You need to create this image or handle it specially
    display=' ',
    fileDisplay='_',
    buttonLayout=(5, 5),  # Adjust position as needed
    characterList=None
))

characters = []

cur.execute("SELECT * FROM Characters")

rows = cur.fetchall()

for row in rows:
    characters.append(row[0])
