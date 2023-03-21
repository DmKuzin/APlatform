# My Token
TO_GROUP_AUTHORIZATION_TOKEN: str = 'OTE1OTUxMTAwNzUyOTUzMzQ0.Gs18Go.1M-rqO_38uwkecEdAf-PGgrAPY9MMEd80zQzyU'

# Platon token
AUTHORIZATION_TOKEN: str = 'ODEwNTA1MDgzMzA4NzM2NTI0.GL5olG.WeYUW_4m5DGjyqRtHo2pfg3LW5jQ-gwltMvHds'
FROM_DISCORD_SERVERS_TABLE_PATH: str = 'Servers/servers_from_discord.csv'

TO_GROUP_SERVERS_TABLE_PATH: str = 'Servers/servers_to_group.csv'

APP_LOGO_PATH: str = "logo/argonauts3.png"

DISCORD_FILE_PATH: str = 'MessageLog/msg_table.pkl'
ANALYSE_FILE_PATH: str = 'MessageLog/msg_analysis_table.pkl'

POSTGRESQL_CONNECTION_HOST: str = 'localhost'
POSTGRESQL_CONNECTION_DATABASE: str = 'postgres'
POSTGRESQL_CONNECTION_USER: str = 'postgres'
POSTGRESQL_CONNECTION_PASSWORD: str = 'qwerty'

DISCORD_SQL_TABLE: str = 'raw_discord_data.from_discord'
DISCORD_SQL_VIEW: str = 'raw_discord_data.view_from_discord'
ANALYSE_SQL_TABLE: str = 'raw_discord_data.to_analyse'
ANALYSE_SQL_VIEW: str = 'raw_discord_data.view_to_analyse'

HASHED_FILE_PATH: str = 'Authentication/hashed_pw.pkl'

AUTHENTICATION_CONFIG_FILE_PATH: str = 'Authentication/authentication_config.yaml'

DATA_TABLE_SIZE: int = 5000

NUM_HISTORICAL_MESSAGE_MIN: int = 1
NUM_HISTORICAL_MESSAGE_MAX: int = 300
NUM_DEFAULT_HISTORICAL_MESSAGE: int = 20

MESSAGE_TABLE_HEIGHT: int = 600
MESSAGE_TABLE_WIDTH: int = 150

IMAGE_LOGO_SIZE: int = 300
