import scraper2

bot = scraper2.FtxScraper('https://ftx.com/markets')

# links = bot.find_all_links()
# bot.valid_links(links)
# bot.get_data()

bot.find_all_links()
bot.valid_links()
bot.get_data_local()
#bot.upload_data()