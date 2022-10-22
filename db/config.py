import mysql.connector

db = mysql.connector.connect (
    host="localhost",
    user="root",
    passwd="Malisha2001",
    database="greekprofile",
)

cursor = db.cursor(dictionary=True, buffered=True)