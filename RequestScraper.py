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

        self.msg_loger = MessageProc.MessageLogger(max_rows=constants.DATA_TABLE_SIZE)
        self.msg_loger.load_data_from_file(filename=save_message_path)
        self.save_message_path = save_message_path

        # if len(self.msg_loger.data) > 0:
        #     self.last_message_id = self.msg_loger.data[-1:]['id'].tolist()[0]
        # else:
        #     self.last_message_id = None

        # self.server_name = self.get_server_name_from_discord()
        # self.channel_name = self.get_channel_name_from_discord()

        self.server_name = self.get_server_name_from_table()
        self.channel_name = self.get_channel_name_from_table()

        self.last_message_id = None
        if len(self.msg_loger.data) > 0:
            channel_data = self.msg_loger.data[self.msg_loger.data['channel_name'] == self.channel_name]
            if len(channel_data) > 0:
                self.last_message_id = channel_data[-1:]['id'].tolist()[0]

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
            server_name = from_discord_servers_table[from_discord_servers_table['server_id'] == self.server_id]['server_name'].to_list()[0]
            return server_name
        else:
            return print(f"Error getting server name")

    def get_channel_name_from_table(self):
        # Read servers table from file
        from_discord_servers_table = pd.read_csv(constants.FROM_DISCORD_SERVERS_TABLE_PATH)
        if sum(from_discord_servers_table['channel_id'] == self.channel_id) > 0:
            channel_name = from_discord_servers_table[from_discord_servers_table['channel_id'] == self.channel_id]['channel_name'].to_list()[0]
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

        # return scraped_msg
        for messages in reversed(scraped_msg):
            self.last_message_id = messages['id']
            status = MessageProc.MessageStatus.FROM_DISCORD.name
            self.msg_loger.log_message(messages['content'],
                                       messages['id'],
                                       messages['timestamp'],
                                       messages['author']['username'],
                                       status,
                                       self.server_name,
                                       self.channel_name)
            self.msg_loger.save_data_to_file(filename=self.save_message_path)

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
            if self.last_message_id is not None:
                params['after'] = self.last_message_id

            url = f'{self.api_url}/channels/{self.channel_id}/messages'
            response = requests.get(url, headers=self.headers, params=params)
            messages = json.loads(response.text)

            if len(messages) > 0:
                # current_ids = self.msg_loger.data['id'].to_list()
                # if not (messages[0]['id'] in current_ids):
                self.last_message_id = messages[0]['id']
                status = MessageProc.MessageStatus.FROM_DISCORD.name
                self.msg_loger.log_message(messages[0]['content'],
                                           messages[0]['id'],
                                           messages[0]['timestamp'],
                                           messages[0]['author']['username'],
                                           status,
                                           self.server_name,
                                           self.channel_name)
                self.msg_loger.save_data_to_file(filename=self.save_message_path)

            # time.sleep(1)
            else:
                break
