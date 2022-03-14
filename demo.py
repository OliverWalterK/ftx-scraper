import scraper

bot = scraper.FtxScraper('https://ftx.com/markets')

bot.find_all_links()
bot.valid_links()
#bot.get_data_local()
#bot.upload_data()
bot.download_data_locally()