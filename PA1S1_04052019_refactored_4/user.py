import sqlite3
import requests
from datetime import datetime, timedelta

PAGE_ACCESS_TOKEN = 'EAAEvMG9mZAREBAI2hQLAOicFoHnuoIEIiL7tfaEcr9dpxQsPcgRop2dgwl9L0Wd4QAaEVcbHnB2ksjjTqAbuRtjRKi7uFFjcPYa0aZCu9ruyaeVjXgnum2xVUi8X2r3yiHE8tPHPJW21YwudBXx0wpPbEjtsGAgf4qsGggjAZDZD'


class User:
    # Initializer / Instance Attributes
    def __init__(self, ID):
        self.ID = ID
        if self.find_by_id(ID) == False:
            target_link = 'https://graph.facebook.com/v2.6/' + ID
            params = (('fields', 'first_name, last_name, timezone, gender'),
                      ('access_token', PAGE_ACCESS_TOKEN))
            response = requests.get(target_link, params=params)
            user_info = response.text
            print(user_info)
            user_info = user_info[1:len(user_info)-1]
            user_info = user_info.replace('"', '')
            user_info = user_info.replace(',', ', ')
            self.user_info = [x.strip() for x in user_info.split(',')]
            print(self.user_info)
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()
            # Inserting one user
            insert_query = "INSERT INTO users VALUES (?, ?, ?, ?, ?)"
            this_user = (ID,
                         self.user_info[0].split(":")[1],
                         self.user_info[1].split(":")[1],
                         self.user_info[2].split(":")[1],
                         self.user_info[3].split(":")[1])

            cursor.execute(insert_query, this_user)
            connection.commit()
            connection.close()

    def find_by_id(self, ID):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (ID,))
        row = result.fetchone()
        connection.close()
        if row:
            return True
        else:
            return False

    def get_user_info_by_id(self, ID):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (ID,))
        row = result.fetchone()

        output = []
        query = "SELECT * FROM userInteractions WHERE ID = ?"
        result = cursor.execute(query, (ID,))
        all_records = result.fetchall()
        num_records = len(all_records)

        if num_records > 1:
            last_row = all_records[num_records-1]
            output.append((last_row[1], last_row[2]))
            before_last_row = all_records[num_records-2]
            output.append((before_last_row[1], before_last_row[2]))

        connection.close()
        return row, output

    def update_user_info_by_id(self, ID, update_info):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        insert_query = "INSERT INTO userInteractions VALUES (?, ?, ?, ?, ?, ?)"
        this_interaction = (ID,
                            update_info['query'],
                            update_info['response'],
                            str(datetime.now()),
                            update_info['aware'],
                            update_info['stateful'])
        cursor.execute(insert_query, this_interaction)
        connection.commit()
        connection.close()
