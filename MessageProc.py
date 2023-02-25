import pandas as pd
from datetime import datetime
import numpy as np
from enum import Enum


#message_status = ['from_discord', 'to_analyse', 'to_group']

class MessageStatus(Enum):
    FROM_DISCORD = 1
    TO_ANALYSE = 2
    ANALYSE = 3
    SUMMARIZED = 4


class MessageLogger:

    def __init__(self, max_rows=100):
        self.max_rows = max_rows
        self.columns = ['message', 'id', 'datetime', 'author', 'status', 'server_id', 'channel_id']
        #self.data = pd.DataFrame(index=np.arange(max_rows), columns=self.columns)
        self.data = pd.DataFrame(columns=self.columns)

    def log_message(self, message, id, datetime, author, status, server_id, channel_id):
        new_df = pd.DataFrame([{'message': message,
                                'id': id,
                                'datetime': datetime,
                                'author': author,
                                'status': status,
                                'server_id': server_id,
                                'channel_id': channel_id
                                }])

        if len(self.data) >= self.max_rows:
            self.data = self.data.iloc[1:].reset_index(drop=True)

        self.data = pd.concat([self.data, new_df], axis=0, ignore_index=True)

    def save_data(self, filename):
        self.data.to_pickle(filename)

    def load_data(self, filename):
        self.data = pd.read_pickle(filename)
        return self.data[self.columns]
