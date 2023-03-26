import RequestScraper, constants
import pandas as pd
# from multiprocessing import Process
import threading
import time
import sys

# Read servers table from file
from_discord_servers_table = pd.read_csv(constants.FROM_DISCORD_SERVERS_TABLE_PATH)


def get_historical_messages(server_id, channel_id):
    # Create Discord channel listener
    psql_conn = {'host': constants.POSTGRESQL_CONNECTION_HOST,
                 'database': constants.POSTGRESQL_CONNECTION_DATABASE,
                 'user': constants.POSTGRESQL_CONNECTION_USER,
                 'password': constants.POSTGRESQL_CONNECTION_PASSWORD}

    discord_listener = RequestScraper.DiscordBot(constants.AUTHORIZATION_TOKEN,
                                                 server_id,
                                                 channel_id,
                                                 psql_conn)

    discord_listener.get_historical_messages(max_num=3)


def read_latest_messages(server_id, channel_id):
    # Create Discord channel listener
    psql_conn = {'host': constants.POSTGRESQL_CONNECTION_HOST,
                 'database': constants.POSTGRESQL_CONNECTION_DATABASE,
                 'user': constants.POSTGRESQL_CONNECTION_USER,
                 'password': constants.POSTGRESQL_CONNECTION_PASSWORD}

    discord_listener = RequestScraper.DiscordBot(constants.AUTHORIZATION_TOKEN,
                                                 server_id,
                                                 channel_id,
                                                 psql_conn)

    discord_listener.read_latest_messages()


listeningPeriod = int(constants.LISTENING_PERIOD * 60 * 0.3)

while True:
    try:
        sys.stdout.flush()
        threads = []
        for idx, row in from_discord_servers_table.iterrows():
            print(f'Server: {row["server_name"]} Channel: {row["channel_name"]}\n')
            t = threading.Thread(target=get_historical_messages, args=(row['server_id'], row['channel_id']))
            # Start both threads
            threads.append(t)

        # start each thread
        for t in threads:
            t.start()

        # wait for each thread to finish
        for t in threads:
            t.join()

        while True:
            threads = []
            for idx, row in from_discord_servers_table.iterrows():
                t = threading.Thread(target=read_latest_messages, args=(row['server_id'], row['channel_id']))
                # Start both threads
                threads.append(t)

            # start each thread
            for t in threads:
                t.start()

            for t in threads:
                t.join()

            for _ in range(listeningPeriod):
                for cursor in '|/-\\':
                    sys.stdout.write('\rListening msg...{}'.format(cursor))
                    sys.stdout.flush()
                    time.sleep(0.3)
    except Exception as error:
        print("Incorrect message format", error)
        continue
    # break;

# %%

# %%
