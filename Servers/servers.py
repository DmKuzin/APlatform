import pandas as pd

# Analyse servers
columns = ['server_id', 'server_name', 'channel_id', 'channel_name', 'user_to_server_availability', 'user_to_channel_availability']
data = [[903535408846077952, 'Dark Echelon', 964218449301737503, 'Main-corner', 'dkuzin', 'dkuzin'],
        [290843998296342529, 'Anime', 826527827792887869, 'Main', 'dkuzin', 'dkuzin'],
        [290843998296342529, 'Anime_copy', 826527827792887869, 'Main', 'dkuzin', 'dkuzin']]

servers_df = pd.DataFrame(data=data, columns=columns)
servers_df.to_csv('servers_from_discord.csv', index=False)


# Group server
columns = ['server_id', 'server_name', 'channel_id', 'channel_name']
data = [[1073733605995589702, 'MyTestServer', 1073733606679248908, 'general']] #1073733606679248908

servers_df = pd.DataFrame(data=data, columns=columns)
servers_df.to_csv('servers_to_group.csv', index=False)


