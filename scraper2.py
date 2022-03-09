from email.contentmanager import raw_data_manager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, uuid, os, json, boto3, tempfile
from sqlalchemy import create_engine

class FtxScraper:
    '''
    This class is a scraper that will run through all cryptocurrencies on ftx.com/markets and extract information.
    
    Parameters
    ----------
    url: str
        The websites url -> (https://ftx.com/markets)

    Attribute
    ---------
    driver:
        This is the webdriver object.
    '''
    def __init__(self, url, options=None):
        self.url = url
        if options:
            self.driver = Chrome(ChromeDriverManager().install(), options=options)
        else:
            self.driver = Chrome(ChromeDriverManager().install())
        self.driver.maximize_window()
        self.driver.get(self.url)

        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        HOST = 'ftx-scraper2.cn4izzmm7yyd.eu-west-2.rds.amazonaws.com' 
        USER = 'postgres'
        PASSWORD = '8750Ironpineapple?'
        PORT = 5432
        DATABASE = 'postgres'
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
        self.client = boto3.client('s3')
    
    def find_all_links(self):
        '''
        This method will find all links found on the website and compile it in a list.

        Returns
        -------
        all_url: list
            A list of all viable url on the website.    
        '''
        self.all_url = []
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@href]")))
            loop = self.driver.find_elements(By. XPATH, "//a[@href]")
            for links in loop:
                self.all_url.append(links.get_attribute("href"))
        except:
            print("No links found. Website might not have loaded correctly. Try again.")
        self.all_url.sort()
        return self.all_url

    def valid_links(self):
        '''
        This method aims to clean the list (all_url) and get only the relevant links (valid_url).
        
        Returns
        -------
        valid_url: list
            A list of all relevant links which will be looped in the next step
        '''
        self.valid_url = []
        for i in self.all_url:
            if "trade" and "-" in i:
                self.valid_url.append(i)
        del self.valid_url[-4:]
        del self.valid_url[:2]
        return self.valid_url

    def get_data_local(self):
        '''
        This method will loop through the valid_url list and extract the price, name and link for every cryptocurrency. 
        Furthermore, it will make a uuid for every entry.
        
        Returns
        -------
        files: json
            A json file with the cryptocurrency name, price and link

        screenshots: png
            A screenshot of the graph which represents the traffic in the last 24 hours.
        '''
        for links in self.valid_url[:3]:
            self.driver.get(links)
            time.sleep(2)
            self.dictionary = {
                                'UUID':[],
                                'Link':[],
                                'Name':[],
                                'Price':[]
                             } 
            try:
                unique_id = str(uuid.uuid4())
                self.dictionary['UUID'].append(unique_id)
            except NoSuchElementException:
                self.dictionary['UUID'].append('N/A')    
            try:
                value = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/main/div[3]/div[3]/div/div/div/span[1]/p[2]').text
                self.dictionary['Price'].append(value)
            except NoSuchElementException:
                self.dictionary['Price'].append('N/A')
            try:
                self.dictionary['Link'].append(links)
            except NoSuchElementException:
                self.dictionary['Link'].append('N/A')
            try:
                crypto_name = links.split("/")[-1]
                self.dictionary['Name'].append(crypto_name)
            except NoSuchElementException:
                self.dictionary['Name'].append('N/A')
            try:
                if not os.path.exists('./raw_data/screenshots'):
                    os.makedirs('./raw_data/screenshots')
                self.driver.save_screenshot(f'./raw_data/screenshots/{crypto_name}.png')
            except NoSuchElementException:
                print("No pictures were found.")
            with open(f'./raw_data/json_files/{crypto_name}.json', 'w') as fp:
                json.dump(self.dictionary, fp)
            self.client.upload_file(f'./raw_data/json_files/{crypto_name}.json', 'ftx-scraper', f'{crypto_name}.json')

    def upload_data(self):
        '''This method will create a temporary file and upload the file to AWS at the end.'''
        with tempfile.TemporaryDirectory() as tmpdirname:
            for links in self.valid_url[:3]:
                self.driver.get(links)
                self.dictionary = {
                                'UUID':[],
                                'Link':[],
                                'Name':[],
                                'Price':[]
                                } 
                time.sleep(2)
                try:
                    value = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/main/div[3]/div[3]/div/div/div/span[1]/p[2]').text
                    self.dictionary['Price'].append(value)
                except NoSuchElementException:
                    self.dictionary['Price'].append('N/A')
                try:
                    self.dictionary['Link'].append(links)
                except NoSuchElementException:
                    self.dictionary['Link'].append('N/A')
                try:
                    crypto_name = links.split("/")[-1]
                    self.dictionary['Name'].append(crypto_name)
                except NoSuchElementException:
                    self.dictionary['Name'].append('N/A')
                try:
                    unique_id = str(uuid.uuid4())
                    self.dictionary['UUID'].append(unique_id)
                except NoSuchElementException:
                    self.dictionary['UUID'].append('N/A')
                try:
                    self.driver.save_screenshot(tmpdirname + f'/{crypto_name}.png')
                except NoSuchElementException:
                    print("No pictures were found.")
                self.client.upload_file(tmpdirname, 'ftx-scraper', f'{crypto_name}.json')


if __name__ == '__main__':
    bot = FtxScraper()