import sqlite3

connection: sqlite3.Connection = sqlite3.connect('database.db')

with open('schema.sql') as schema:
    connection.executescript(schema.read())

connection.close()
