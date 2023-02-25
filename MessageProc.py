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
        self.columns = ['message', 'id', 'datetime', 'author', 'status']
        #self.data = pd.DataFrame(index=np.arange(max_rows), columns=self.columns)
        self.data = pd.DataFrame(columns=self.columns)

    def log_message(self, message, id, datetime, author, status):
        # self.data = self.data.shift(1)
        # self.data.loc[0, self.columns] = [message, id, datetime, author]
        new_df = pd.DataFrame([{'message': message,
                                'id': id,
                                'datetime': datetime,
                                'author': author,
                                'status': status
                                }])

        if len(self.data) >= self.max_rows:
            self.data = self.data.iloc[1:].reset_index(drop=True)

        self.data = pd.concat([self.data, new_df], axis=0, ignore_index=True)

        # self.data = self.data.append({'message': message,
        #                               'id': id,
        #                               'datetime': datetime,
        #                               'author': author},
        #                              ignore_index=True
        #                              )

    def save_data(self, filename):
        self.data.to_pickle(filename)

    def load_data(self, filename):
        self.data = pd.read_pickle(filename)
        return self.data[self.columns]

    # def save_data(self, filename):
    #     self.data.to_excel(filename, index=False)
    #
    # def read_data(self, filename):
    #     self.data = pd.read_excel(filename)
    #     return self.data[self.columns]


# loger = MessageLogger()
# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# loger.log_message('Hello', 1, current_time, 'Mike')
# loger.save_data(filename='MessageLog/message_log.xlsx')
#
# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# loger.log_message('Hi', 2, current_time, 'Alex')
# loger.save_data(filename='MessageLog/message_log.xlsx')
#
# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# loger.log_message('Great!', 3, current_time, 'Peter')
# loger.save_data(filename='MessageLog/message_log.xlsx')
#
# df = loger.read_data(filename='MessageLog/message_log.xlsx')
#
# print(df)




#%%
