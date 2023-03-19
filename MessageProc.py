import pandas as pd
#from datetime import datetime
#import numpy as np
from enum import Enum
import psycopg2
#import streamlit as st


#message_status = ['from_discord', 'to_analyse', 'to_group']

class MessageStatus(Enum):
    FROM_DISCORD = 1
    TO_ANALYSE = 2
    ANALYSE = 3
    SUMMARIZED = 4


# class MessageLogger:
#
#     def __init__(self, max_rows=100):
#         self.max_rows = max_rows
#         self.columns = ['message', 'id', 'datetime', 'author', 'status', 'server_name', 'channel_name']
#         #self.data = pd.DataFrame(index=np.arange(max_rows), columns=self.columns)
#         self.data = pd.DataFrame(columns=self.columns)
#
#     def log_message(self, message, id, datetime, author, status, server_name, channel_name):
#         new_df = pd.DataFrame([{'message': message,
#                                 'id': id,
#                                 'datetime': datetime,
#                                 'author': author,
#                                 'status': status,
#                                 'server_name': server_name,
#                                 'channel_name': channel_name
#                                 }])
#
#         if len(self.data) >= self.max_rows:
#             self.data = self.data.iloc[1:].reset_index(drop=True)
#
#         self.data = pd.concat([self.data, new_df], axis=0, ignore_index=True)
#
#     def save_data_to_file(self, filename):
#         self.data.to_pickle(filename)
#
#     def load_data_from_file(self, filename):
#         self.data = pd.read_pickle(filename)
#         if len(self.data) > self.max_rows:
#             pos = len(self.data) - self.max_rows
#             self.data = self.data[pos:]
#
#         return self.data[self.columns]

class SQLMessageLogger:

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.columns = ['message', 'id', 'datetime', 'author', 'status', 'server_name', 'channel_name']

    def log_data_to_table(self, destination_table, message, id, datetime, author, status, server_name, channel_name):
        # Open connection
        conn = psycopg2.connect(host=self.host,
                                database=self.database,
                                user=self.user,
                                password=self.password)
        # make insert data query
        sql = f"""INSERT INTO {destination_table} (message,
                                                   id,
                                                   datetime,
                                                   author,
                                                   status,
                                                   server_name,
                                                   channel_name) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"""
        # Insert values
        values = (message,
                  id,
                  datetime,
                  author,
                  status,
                  server_name,
                  channel_name)

        # Execute query
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        count = cursor.rowcount
        # Close connection
        cursor.close()
        conn.close()

    def load_data_from_table(self, source_table):
        # Open connection
        conn = psycopg2.connect(host=self.host,
                                database=self.database,
                                user=self.user,
                                password=self.password)

        cursor = conn.cursor()
        sql = f"SELECT message, id, datetime, author, status, server_name, channel_name FROM {source_table}"
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=self.columns)
        # Close connection
        cursor.close()
        conn.close()

        return df

    def get_last_row_from_table(self, source_table):
        sql = f"""SELECT * FROM {source_table} ORDER BY datetime DESC LIMIT 1;"""
        # Open connection
        conn = psycopg2.connect(host=self.host,
                                database=self.database,
                                user=self.user,
                                password=self.password)

        cursor = conn.cursor()
        cursor.execute(sql)
        last_row = cursor.fetchall()
        df = pd.DataFrame(last_row, columns=self.columns)
        # Close connection
        cursor.close()
        conn.close()

        return df

    def delete_rows_from_table(self, source_table, delete_id_list):
        #sql = f"""DELETE FROM {source_table} WHERE id = CAST({delete_id} AS TEXT);"""
        sql = f"""DELETE FROM {source_table} WHERE id IN ({delete_id_list});"""
        # Open connection
        conn = psycopg2.connect(host=self.host,
                                database=self.database,
                                user=self.user,
                                password=self.password)

        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()

    def update_status_rows_from_table(self, source_table, update_ids_list, new_status):
        sql = f"""UPDATE {source_table} SET status = '{new_status}' WHERE id IN ({update_ids_list});"""

        # Open connection
        conn = psycopg2.connect(host=self.host,
                                database=self.database,
                                user=self.user,
                                password=self.password)

        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()





