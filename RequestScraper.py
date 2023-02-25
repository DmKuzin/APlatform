import requests
import json
import time
# from StreamlitWebPlatform.Run import message_proc
import constants
import MessageProc


class DiscordBot:
    def __init__(self, token: str, channel_id: int, save_message_path: str):
        self.token = token
        self.channel_id = channel_id
        self.headers = {
            'authorization': f'{self.token}'
        }
        self.api_url = 'https://discord.com/api/v9'
        self.last_message_id = None

        self.msg_loger = MessageProc.MessageLogger(max_rows=constants.VIEW_SIZE)
        self.save_message_path = save_message_path

    def get_messages(self, max_num=10):
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

        return scraped_msg

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
                self.last_message_id = messages[0]['id']
                # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # status = 'from_discord'
                status = MessageProc.MessageStatus.FROM_DISCORD.name
                self.msg_loger.log_message(messages[0]['content'],
                                           messages[0]['id'],
                                           messages[0]['timestamp'],
                                           messages[0]['author']['username'],
                                           status)
                self.msg_loger.save_data(filename=self.save_message_path)

            time.sleep(1)


# authorization_token = 'OTE1OTUxMTAwNzUyOTUzMzQ0.GH3xHy.Ky3XIeQtu_7cePNRlbKICzrR7Cfn-SzEIbGLws'
# server_id = 1073733605995589702
# channel_id = 1073733606679248908

# Geecko move
# authorization_token = "OTE1OTUxMTAwNzUyOTUzMzQ0.GkPguW.I-xQx8znhvPkoY2lfGx7KvIGErW3mKlqDE4Dg8"
# #server_id = 957931733351817226
# channel_id = 957931734333272067

# authorization_token = 'OTE1OTUxMTAwNzUyOTUzMzQ0.GkPguW.I-xQx8znhvPkoY2lfGx7KvIGErW3mKlqDE4Dg8'
# channel_id = 1073733606679248908
# save_message_path = 'MessageLog/msg_table.pkl'

# discord_listener = DiscordBot(constants.AUTHORIZATION_TOKEN,
#                               constants.CHANNEL_ID,
#                               constants.DISCORD_FILE_PATH)
# discord_listener.read_latest_messages()
# client.get_messages(max_num=5)

# %%
