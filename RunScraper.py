import RequestScraper, constants


discord_listener = RequestScraper.DiscordBot(constants.AUTHORIZATION_TOKEN,
                                             constants.SERVER_ID,
                                             constants.CHANNEL_ID,
                                             constants.DISCORD_FILE_PATH)

# Get VIEW_SIZE latest messages from discord channel
discord_listener.get_historical_messages(max_num=constants.VIEW_SIZE)
# Continuously read the latest message
discord_listener.read_latest_messages()

