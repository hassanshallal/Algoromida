import sqlite3

connection = sqlite3.connect('users.db')
cursor = connection.cursor()

# Creating a table
create_table1 = "CREATE TABLE users (ID text, first_name text, last_name text,  timezone text, gender text)"
cursor.execute(create_table1)

create_table2 = "CREATE TABLE userInteractions (ID text, query text, response text, dateTime text, awareness text, statefulness text)"
cursor.execute(create_table2)

connection.commit()
connection.close()
