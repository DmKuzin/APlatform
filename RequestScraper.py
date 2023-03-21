import requests
import json
import time
# from StreamlitWebPlatform.Run import message_proc
import constants
import MessageProc
import pandas as pd


class DiscordBot:
    def __init__(self, token: str, server_id: int, channel_id: int, save_message_path: str):
        self.token = token
        self.server_id = server_id
        self.channel_id = channel_id
        self.headers = {
            'authorization': f'{self.token}'
        }
        self.api_url = 'https://discord.com/api/v9'
        self.last_message_id = ''

        # Initialize logger
        self.sql_msg_logger = MessageProc.SQLMessageLogger(constants.POSTGRESQL_CONNECTION_HOST,
                                                           constants.POSTGRESQL_CONNECTION_DATABASE,
                                                           constants.POSTGRESQL_CONNECTION_USER,
                                                           constants.POSTGRESQL_CONNECTION_PASSWORD)

        # self.msg_loger = MessageProc.MessageLogger(max_rows=constants.DATA_TABLE_SIZE)
        # self.msg_loger.load_data_from_file(filename=save_message_path)
        # self.save_message_path = save_message_path

        # if len(self.msg_loger.data) > 0:
        #     self.last_message_id = self.msg_loger.data[-1:]['id'].tolist()[0]
        # else:
        #     self.last_message_id = None

        # self.server_name = self.get_server_name_from_discord()
        # self.channel_name = self.get_channel_name_from_discord()

        self.server_name = self.get_server_name_from_table()
        self.channel_name = self.get_channel_name_from_table()

        # self.last_message_id = None
        # if len(self.msg_loger.data) > 0:
        #     channel_data = self.msg_loger.data[self.msg_loger.data['channel_name'] == self.channel_name]
        #     if len(channel_data) > 0:
        #         self.last_message_id = channel_data[-1:]['id'].tolist()[0]
        last_row = self.sql_msg_logger.get_last_row_from_table(constants.DISCORD_SQL_VIEW)
        if len(last_row) > 0:
            self.last_message_id = str(last_row['id'].to_list()[0])

    def get_channel_name_from_discord(self):
        channel_response = requests.get(f"https://discord.com/api/channels/{self.channel_id}", headers=self.headers)
        if channel_response.status_code == 200:
            channel_data = channel_response.json()
            return channel_data["name"]
        else:
            return print(f"Error getting channel information: {channel_response.text}")

    def get_server_name_from_discord(self):
        server_response = requests.get(f"https://discord.com/api/guilds/{self.server_id}", headers=self.headers)
        if server_response.status_code == 200:
            server_data = server_response.json()
            return server_data["name"]
        else:
            return print(f"Error getting server information: {server_response.text}")

    def get_server_name_from_table(self):
        # Read servers table from file
        from_discord_servers_table = pd.read_csv(constants.FROM_DISCORD_SERVERS_TABLE_PATH)
        if sum(from_discord_servers_table['server_id'] == self.server_id) > 0:
            server_name = from_discord_servers_table[from_discord_servers_table['server_id'] == self.server_id][
                'server_name'].to_list()[0]
            return server_name
        else:
            return print(f"Error getting server name")

    def get_channel_name_from_table(self):
        # Read servers table from file
        from_discord_servers_table = pd.read_csv(constants.FROM_DISCORD_SERVERS_TABLE_PATH)
        if sum(from_discord_servers_table['channel_id'] == self.channel_id) > 0:
            channel_name = from_discord_servers_table[from_discord_servers_table['channel_id'] == self.channel_id][
                'channel_name'].to_list()[0]
            return channel_name
        else:
            return print(f"Error getting channel name")

    def get_historical_messages(self, max_num=10):
        """
        Get N historical messages from the Discord channel.
        """
        last_historical_message_id = None
        scraped_msg = []
        num = 0
        limit = 1
        while True:
            query_parameters = f'limit={limit}'
            if last_historical_message_id is not None:
                query_parameters += f'&before={last_historical_message_id}'
            # else:
            #     self.last_message_id = last_historical_message_id

            r = requests.get(
                f'{self.api_url}/channels/{self.channel_id}/messages?{query_parameters}', headers=self.headers
            )
            jsonn = json.loads(r.text)
            if len(jsonn) == 0:
                break

            for value in jsonn:
                scraped_msg.append(value)
                last_historical_message_id = value['id']
                num = num + 1

            if num >= max_num:
                break

        # log scraped msg to sql table
        for messages in reversed(scraped_msg):
            message = messages['content']
            id = str(messages['id'])
            datetime = messages['timestamp']
            author = messages['author']['username']
            status = MessageProc.MessageStatus.FROM_DISCORD.name
            server_name = self.server_name
            channel_name = self.channel_name
            mentions_id = None
            mentions_username = None
            message_reference_channel_id = None
            message_reference_guild_id = None
            message_reference_message_id = None
            referenced_message_id = None
            referenced_message_content = None
            referenced_message_channel_id = None
            referenced_message_author_username = None

            # Message parser by headers
            for header in messages:
                # print(header)
                # print('^^^^^^^^^^^^^')
                if 'mentions' in header:
                    if len(messages['mentions']) > 0:
                        mentions_id = str(messages['mentions'][0]['id'])
                        mentions_username = messages['mentions'][0]['username']

                if 'message_reference' in header:
                    if len(messages['message_reference']) > 0:
                        message_reference_channel_id = messages['message_reference']['channel_id']
                        message_reference_guild_id = messages['message_reference']['guild_id']
                        message_reference_message_id = messages['message_reference']['message_id']

                if 'referenced_message' in header:
                    if len(messages['referenced_message']) > 0:
                        referenced_message_id = messages['referenced_message']['id']
                        referenced_message_content = messages['referenced_message']['content']
                        referenced_message_channel_id = messages['referenced_message']['channel_id']
                        referenced_message_author_username = messages['referenced_message']['author']['username']

            self.sql_msg_logger.log_data_to_table(constants.DISCORD_SQL_TABLE,
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
                                                  referenced_message_author_username)
            # Save last message id
            self.last_message_id = str(messages['id'])

    def send_message(self, message):
        """
        Send a message to the Discord channel.
        """
        url = f'{self.api_url}/channels/{self.channel_id}/messages'
        data = {'content': message}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()

    def read_latest_messages(self):
        """
        Continuously read the latest new message from the Discord channel.
        """
        while True:
            params = {'limit': 1}
            # if self.last_message_id is not None:
            if self.last_message_id:
                params['after'] = self.last_message_id

            url = f'{self.api_url}/channels/{self.channel_id}/messages'
            response = requests.get(url, headers=self.headers, params=params)
            messages = json.loads(response.text)

            if len(messages) > 0:
                message = messages[0]['content']
                id = str(messages[0]['id'])
                datetime = messages[0]['timestamp']
                author = messages[0]['author']['username']
                status = MessageProc.MessageStatus.FROM_DISCORD.name
                server_name = self.server_name
                channel_name = self.channel_name
                mentions_id = None
                mentions_username = None
                message_reference_channel_id = None
                message_reference_guild_id = None
                message_reference_message_id = None
                referenced_message_id = None
                referenced_message_content = None
                referenced_message_channel_id = None
                referenced_message_author_username = None

                # Message parser by headers
                for header in messages[0]:
                    if 'mentions' in header:
                        if len(messages[0]['mentions']) > 0:
                            #print(messages[0]['mentions'])
                            mentions_id = str(messages[0]['mentions'][0]['id'])
                            mentions_username = messages[0]['mentions'][0]['username']

                    if 'message_reference' in header:
                        if len(messages[0]['message_reference']) > 0:
                            message_reference_channel_id = messages[0]['message_reference']['channel_id']
                            message_reference_guild_id = messages[0]['message_reference']['guild_id']
                            message_reference_message_id = messages[0]['message_reference']['message_id']

                    if 'referenced_message' in header:
                        if len(messages[0]['referenced_message']) > 0:
                            referenced_message_id = messages[0]['referenced_message']['id']
                            referenced_message_content = messages[0]['referenced_message']['content']
                            referenced_message_channel_id = messages[0]['referenced_message']['channel_id']
                            referenced_message_author_username = messages[0]['referenced_message']['author']['username']

                self.sql_msg_logger.log_data_to_table(constants.DISCORD_SQL_TABLE,
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
                                                      referenced_message_author_username)
                # Save last message id
                self.last_message_id = str(messages[0]['id'])

            # time.sleep(1)
            else:
                break
