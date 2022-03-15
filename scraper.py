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

    def download_data(self):
        '''
        This method will loop through the valid_url list and extract the price, name, link and time for every cryptocurrency. 
        Furthermore, it will create a uuid for every entry and save it in the dictionary. It will also create directories for every cryptocurrency and save a json
        and a screenshot of the market in those directories with time stamps.
        
        Creates
        -------
        files: json
            A json file with the cryptocurrency name, uuid, price and link

        screenshots: png
            A screenshot of the last 24 hours market value.
        '''
        crypto_dictionary = {
                    'UUID':[],
                    'Link':[],
                    'Name':[],
                    'Price':[],
                    'Time':[]
                                } 
        df_global_dictionary = {
                        'UUID':[],
                        'Link':[],
                        'Name':[],
                        'Price':[],
                        'Time':[]
                                    } 
        count = 0
        for links in self.valid_url:
            crypto_name = links.split("/")[-1]
            self.driver.get(links)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/')))   #//span[@class='jss689']//descendant::p
            time.sleep(1)
            current_time = datetime.datetime.now()
            try:
                unique_id = str(uuid.uuid4())
                crypto_dictionary['UUID'].append(unique_id)
                df_global_dictionary['UUID'].append(unique_id)
            except NoSuchElementException:
                crypto_dictionary['UUID'].append('N/A')
                df_global_dictionary['UUID'].append('N/A')
            try:
                value = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/main/div[3]/div[3]/div/div/div/span[1]/p[2]').text
                crypto_dictionary['Price'].append(value)
                df_global_dictionary['Price'].append(value)
            except NoSuchElementException:
                crypto_dictionary['Price'].append('N/A')
                df_global_dictionary['Price'].append('N/A')
            try:
                crypto_dictionary['Link'].append(links)
                df_global_dictionary['Link'].append(links)
            except NoSuchElementException:
                crypto_dictionary['Link'].append('N/A')
                df_global_dictionary['Link'].append('N/A')
            try:
                crypto_dictionary['Name'].append(crypto_name)
                df_global_dictionary['Name'].append(crypto_name)
            except NoSuchElementException:
                crypto_dictionary['Name'].append('N/A')
                df_global_dictionary['Name'].append('N/A')
            crypto_dictionary['Time'].append(current_time.strftime("%c"))
            df_global_dictionary['Time'].append(current_time.strftime("%c"))
            count = count + 1
            print(f'Downloading data:(json) and taking screenshot:(png) for {crypto_name}, {count}/{len(self.valid_url)}.')
            if not os.path.exists(f'./raw_data/{crypto_name}'):
                os.makedirs(f'./raw_data/{crypto_name}')
            with open(f'./raw_data/{crypto_name}/{current_time}.json', 'w') as fp:
                json.dump(crypto_dictionary, fp)
            try:
                self.driver.save_screenshot(f'./raw_data/{crypto_name}/{current_time}.png')
            except NoSuchElementException:
                print(f"No screenshot was made for {crypto_name}.")
        df_global_dictionary = pd.DataFrame(df_global_dictionary)
        df_global_dictionary.to_csv('~/Desktop/AiCore/Scraper/ftx-scraper/raw_data/dataframe.csv', index = False)
        
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
            time.sleep(1)
            self.crypto_name = links.split("/")[-1]
            # self.creating_dictionary(links)
            count = count + 1
            print(f'Uploading data:(json) and screenshot:(png) for {self.crypto_name}, {count}/{len(self.valid_url)}.')
            with tempfile.TemporaryDirectory() as tmpdirname:
                try:
                    self.driver.save_screenshot(tmpdirname + f'/{self.crypto_name}.png')
                    self.client.upload_file(tmpdirname + f'/{self.crypto_name}.png', 'ftx-scraper', f'{self.crypto_name}.png')
                except NoSuchElementException:
                    print(f"No screenshot was made for {self.crypto_name}!")
                with open(tmpdirname + f'/{self.crypto_name}.json', 'w') as fp:
                    json.dump(self.dictionary, fp)
                self.client.upload_file(tmpdirname + f'/{self.crypto_name}.json', 'ftx-scraper', f'{self.crypto_name}.json')
        df_dictionary = pd.DataFrame(self.df_dictionary)
        df_dictionary.to_sql('df_dictionary', con=self.engine, if_exists='append', index=False)


if __name__ == '__main__':
    bot = FtxScraper()