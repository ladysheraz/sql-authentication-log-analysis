#!/usr/bin/env python3
import mysql.connector

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="p@55w0rD",
    database="fakedb"
)

cur = cnx.cursor()

# disable FK checks temporarily
cur.execute("SET FOREIGN_KEY_CHECKS = 0")

cur.execute("TRUNCATE TABLE auth_logs")
cur.execute("TRUNCATE TABLE users")

cur.execute("SET FOREIGN_KEY_CHECKS = 1")

cnx.commit()
cnx.close()

print("Database reset complete")