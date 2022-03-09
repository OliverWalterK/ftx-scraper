import unittest, all_url

from numpy import dtype
import scraper2

class ScraperTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = scraper2.FtxScraper('https://ftx.com/markets')

    def test_find_all_links(self):
        actual_find_all_links = self.bot.find_all_links()
        # self.assertEqual(actual_find_all_links, all_url.expected_original_find_all_links)
        self.assertIsInstance(actual_find_all_links, list)
        for element in actual_find_all_links:
            self.assertIsInstance(element, str)

    # def test_validate_links(self):
        actual_valid_links = self.bot.valid_links()
        # self.assertEqual(actual_valid_links, all_url.expected_original_valid_links)
        self.assertIsInstance(actual_valid_links, list)
        for element in actual_valid_links:
            self.assertEqual(element[0:22], 'https://ftx.com/trade/') 
            self.assertIsInstance(element, str)

    def tearDown(self):
        del self.bot

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)