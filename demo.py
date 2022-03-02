from ukraine_war_map_twitter_bot.main import UkraineBot

bot = UkraineBot("permanent_data.json", "twitter.json")
bot.post()