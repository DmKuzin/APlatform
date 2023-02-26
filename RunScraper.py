import RequestScraper, constants


discord_listener = RequestScraper.DiscordBot(constants.AUTHORIZATION_TOKEN,
                                             constants.SERVER_ID,
                                             constants.CHANNEL_ID,
                                             constants.DISCORD_FILE_PATH)
discord_listener.read_latest_messages()
