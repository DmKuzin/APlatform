import pandas as pd
#from datetime import datetime
#import numpy as np
from enum import Enum
#import streamlit as st


#message_status = ['from_discord', 'to_analyse', 'to_group']

class MessageStatus(Enum):
    FROM_DISCORD = 1
    TO_ANALYSE = 2
    ANALYSE = 3
    SUMMARIZED = 4


class MessageLogger:

    def __init__(self, max_rows=100):
        self.max_rows = max_rows
        self.columns = ['message', 'id', 'datetime', 'author', 'status', 'server_name', 'channel_name']
        #self.data = pd.DataFrame(index=np.arange(max_rows), columns=self.columns)
        self.data = pd.DataFrame(columns=self.columns)

    def log_message(self, message, id, datetime, author, status, server_name, channel_name):
        new_df = pd.DataFrame([{'message': message,
                                'id': id,
                                'datetime': datetime,
                                'author': author,
                                'status': status,
                                'server_name': server_name,
                                'channel_name': channel_name
                                }])

        if len(self.data) >= self.max_rows:
            self.data = self.data.iloc[1:].reset_index(drop=True)

        self.data = pd.concat([self.data, new_df], axis=0, ignore_index=True)

    def save_data_to_file(self, filename):
        self.data.to_pickle(filename)

    def load_data_from_file(self, filename):
        self.data = pd.read_pickle(filename)
        if len(self.data) > self.max_rows:
            pos = len(self.data) - self.max_rows
            self.data = self.data[pos:]

        return self.data[self.columns]
