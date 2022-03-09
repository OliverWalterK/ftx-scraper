import scraper2

bot = scraper2.FtxScraper('https://ftx.com/markets')

bot.find_all_links()
bot.valid_links()
bot.get_data()