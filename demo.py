import scraper

bot = scraper.FtxScraper('https://ftx.com/markets')

if __name__ == '__main__':
    bot.find_all_links()
    bot.valid_links()
    #bot.upload_data()
    bot.download_data()