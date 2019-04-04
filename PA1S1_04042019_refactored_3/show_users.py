import sqlite3

connection = sqlite3.connect('users.db')
cursor = connection.cursor()

query = "SELECT * FROM users"
result = cursor.execute(query)
row = result.fetchall()
for n in range(len(row)):
    print(row[n])
print('==========')
query = "SELECT * FROM userInteractions"
result = cursor.execute(query)
row = result.fetchall()
for n in range(len(row)):
    print(row[n])

connection.close()

