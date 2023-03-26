import pandas as pd
# from datetime import datetime
# import numpy as np
from enum import Enum
import psycopg2


class MessageStatus(Enum):
    FROM_DISCORD = 1
    TO_ANALYSE = 2
    ANALYSE = 3
    SUMMARIZED = 4


class SQLMessageLogger:

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.columns = ['message',
                        'id',
                        'datetime',
                        'author',
                        'status',
                        'server_name',
                        'channel_name',
                        'mentions_id',
                        'mentions_username',
                        'message_reference_channel_id',
                        'message_reference_guild_id',
                        'message_reference_message_id',
                        'referenced_message_id',
                        'referenced_message_content',
                        'referenced_message_channel_id',
                        'referenced_message_author_username']

    def log_data_to_table(self,
                          destination_table,
                          message,
                          id,
                          datetime,
                          author,
                          status,
                          server_name,
                          channel_name,
                          mentions_id,
                          mentions_username,
                          message_reference_channel_id,
                          message_reference_guild_id,
                          message_reference_message_id,
                          referenced_message_id,
                          referenced_message_content,
                          referenced_message_channel_id,
                          referenced_message_author_username):

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
                                                   channel_name,
                                                   mentions_id,
                                                   mentions_username,
                                                   message_reference_channel_id,
                                                   message_reference_guild_id,
                                                   message_reference_message_id,
                                                   referenced_message_id,
                                                   referenced_message_content,
                                                   referenced_message_channel_id,
                                                   referenced_message_author_username
                                                   ) VALUES (%s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s) ON CONFLICT (id) DO NOTHING;"""
        # Insert values
        values = (message,
                  id,
                  datetime,
                  author,
                  status,
                  server_name,
                  channel_name,
                  mentions_id,
                  mentions_username,
                  message_reference_channel_id,
                  message_reference_guild_id,
                  message_reference_message_id,
                  referenced_message_id,
                  referenced_message_content,
                  referenced_message_channel_id,
                  referenced_message_author_username)

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
        sql = f"""SELECT message,
                         id,
                         datetime,
                         author,
                         status,
                         server_name,
                         channel_name,
                         mentions_id,
                         mentions_username,
                         message_reference_channel_id,
                         message_reference_guild_id,
                         message_reference_message_id,
                         referenced_message_id,
                         referenced_message_content,
                         referenced_message_channel_id,
                         referenced_message_author_username FROM {source_table}"""
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=self.columns)
        # Close connection
        cursor.close()
        conn.close()

        return df

    def get_last_row_from_table(self, source_table, channel_name):
        sql = f"""SELECT * FROM {source_table} WHERE channel_name='{channel_name}' ORDER BY datetime DESC LIMIT 1;"""
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
        # sql = f"""DELETE FROM {source_table} WHERE id = CAST({delete_id} AS TEXT);"""
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

    def log_summary(self,
                    destination_table,
                    messages,
                    summary):

        # Open connection
        conn = psycopg2.connect(host=self.host,
                                database=self.database,
                                user=self.user,
                                password=self.password)

        # make insert data query
        sql = f"""INSERT INTO {destination_table} (messages,
                                                   summary
                                                   ) VALUES (%s,
                                                             %s
                                                             ) ON CONFLICT (messages) DO NOTHING;"""

        # Insert values
        values = (messages, summary)

        # Execute query
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        count = cursor.rowcount
        # Close connection
        cursor.close()
        conn.close()
