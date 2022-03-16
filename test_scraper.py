import unittest, time
from selenium.webdriver.common.by import By

import scraper

class ScraperTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = scraper.FtxScraper('https://ftx.com/markets')

    def test_find_all_links(self):
        actual_find_all_links = self.bot.find_all_links()
        self.assertIsInstance(actual_find_all_links, list)
        for elements in actual_find_all_links:
            self.assertIsInstance(elements, str)

    def test_validate_links(self):
        self.bot.find_all_links()
        self.actual_valid_links = self.bot.valid_links()
        self.assertIsInstance(self.actual_valid_links, list)
        for element in self.actual_valid_links:
            self.assertEqual(element[0:22], 'https://ftx.com/trade/') 
            self.assertIsInstance(element, str)

    def test_download_data(self):
        for links in self.bot.valid_links()[:1]:
            self.bot.driver.get(links)
            time.sleep(2)
            self.assertIsInstance(self.bot.driver.find_element(By.XPATH, "//h5[@class='MuiTypography-root MuiTypography-h5']").text, float)

    def tearDown(self):
        del self.bot

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)