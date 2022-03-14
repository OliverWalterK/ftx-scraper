from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, uuid, os, json, boto3, tempfile, aws_creds, datetime
import pandas as pd
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
    def __init__(self, url:str, options=None):
        self.url = url
        # self.options = Options()
        # self.options.add_argument('--headless')
        if options:
            self.driver = Chrome(ChromeDriverManager().install(), options=options)
        else:
            self.driver = Chrome(ChromeDriverManager().install())
        self.driver.maximize_window()
        self.driver.get(self.url)

        DATABASE_TYPE = aws_creds.DATABASE_TYPE
        DBAPI = aws_creds.DBAPI
        HOST = aws_creds.HOST
        USER = aws_creds.USER
        PASSWORD = aws_creds.PASSWORD
        PORT = aws_creds.PORT
        DATABASE = aws_creds.DATABASE
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
        self.client = boto3.client('s3')
    
    def find_all_links(self):
        '''
        This method will find all links found on the website and compile it in a list.

        Returns
        -------
        all_url: list
            An alphabetically ordered list of all url on the website.    
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
            A list of all relevant links which will be looped in the next step.
        '''
        self.valid_url = []
        for i in self.all_url:
            if 'USD' in i:
                continue
            if "trade" in i:
                self.valid_url.append(i)
        return self.valid_url

    def creating_dictionary(self, links):
        '''
        Input
        -----
        links
        
        Output
        ------
        Dictionary
        
        '''
        self.dictionary = {
                    'UUID':[],
                    'Link':[],
                    'Name':[],
                    'Price':[]
                    } 
        try:
            unique_id = str(uuid.uuid4())
            self.dictionary['UUID'].append(unique_id)
            self.df_dictionary['UUID'].append(unique_id)
        except NoSuchElementException:
            self.dictionary['UUID'].append('N/A')
            self.df_dictionary['UUID'].append('N/A')
        try:
            value = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/main/div[3]/div[3]/div/div/div/span[1]/p[2]').text
            self.dictionary['Price'].append(value)
            self.df_dictionary['Price'].append(value)
        except NoSuchElementException:
            self.dictionary['Price'].append('N/A')
            self.df_dictionary['Price'].append('N/A')
        try:
            self.dictionary['Link'].append(links)
            self.df_dictionary['Link'].append(links)
        except NoSuchElementException:
            self.dictionary['Link'].append('N/A')
            self.df_dictionary['Link'].append('N/A')
        try:
            self.dictionary['Name'].append(self.crypto_name)
            self.df_dictionary['Name'].append(self.crypto_name)
        except NoSuchElementException:
            self.dictionary['Name'].append('N/A')
            self.df_dictionary['Name'].append('N/A')
        return self.dictionary

    def download_data_locally(self):
        '''
        This method will loop through the valid_url list and extract the price, name, and link for every cryptocurrency. 
        Furthermore, it will create a uuid for every entry and save it in the dictionary.
        
        Creates
        -------
        files: json
            A json file with the cryptocurrency name, uuid, price and link

        screenshots: png
            A screenshot of the last 24 hours market value.
        '''
        count = 0
        self.df_dictionary = {
                        'UUID':[],
                        'Link':[],
                        'Name':[],
                        'Price':[]
                            } 
        for links in self.valid_url[:5]:
            self.crypto_name = links.split("/")[-1]
            self.driver.get(links)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div/main/div[3]/div[3]/div/div/div/span[1]/p[2]')))
            time.sleep(1)
            self.creating_dictionary(links)
            count = count + 1
            print(f'Downloading data:(json) and taking screenshot:(png) for {self.crypto_name}, {count}/{len(self.valid_url)}.')
            if not os.path.exists('./raw_data/json_files'):
                os.makedirs('./raw_data/json_files')
            with open(f'./raw_data/json_files/{self.crypto_name}.json', 'w') as fp:
                json.dump(self.dictionary, fp)
            try:
                if not os.path.exists('./raw_data/screenshots'):
                    os.makedirs('./raw_data/screenshots')
                self.driver.save_screenshot(f'./raw_data/screenshots/{self.crypto_name}.png')
            except NoSuchElementException:
                print("No screenshot was made for {self.crypto_name}.")
        df_dictionary = pd.DataFrame(self.df_dictionary)
        df_dictionary.to_sql('df_dictionary', con=self.engine, if_exists='append', index=False)


    def upload_data(self):
        '''
        This method will loop through the valid_url list and extract the price, name, and link for every cryptocurrency. 
        Furthermore, it will create a uuid for every entry and save it in the dictionary.
        It will create a temporary file and upload the file to AWS for each iteration.

        Uploads
        -------
        files: json
            A json file with the cryptocurrency name, uuid, price and link.

        screenshots: png
            A screenshot of the last 24 hours market value.

        '''
        count = 0
        for links in self.valid_url:
            self.driver.get(links)
            crypto_name = links.split("/")[-1]
            count = count + 1
            print(f'Uploading data for {crypto_name}, {count}/{len(self.valid_url)}.')
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
                self.dictionary['Name'].append(crypto_name)
            except NoSuchElementException:
                self.dictionary['Name'].append('N/A')
            try:
                unique_id = str(uuid.uuid4())
                self.dictionary['UUID'].append(unique_id)
            except NoSuchElementException:
                self.dictionary['UUID'].append('N/A')
            with tempfile.TemporaryDirectory() as tmpdirname:
                try:
                    self.driver.save_screenshot(tmpdirname + f'/{crypto_name}.png')
                    self.client.upload_file(tmpdirname + f'/{crypto_name}.png', 'ftx-scraper', f'{crypto_name}.png')
                except NoSuchElementException:
                    print(f"No screenshot was made for {crypto_name}!")
                with open(tmpdirname + f'/{crypto_name}.json', 'w') as fp:
                    json.dump(self.dictionary, fp)
                self.client.upload_file(tmpdirname + f'/{crypto_name}.json', 'ftx-scraper', f'{crypto_name}.json')

        df_dictionary = pd.DataFrame(self.df_dictionary)
        df_dictionary.to_sql('df_dictionary', con=self.engine, if_exists='append', index=False)


if __name__ == '__main__':
    bot = FtxScraper()