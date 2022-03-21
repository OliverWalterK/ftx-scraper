from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, uuid, os, json, boto3, tempfile, datetime
from config import aws_creds
import pandas as pd
from sqlalchemy import create_engine

class FtxScraper:
    '''
    This class is a scraper that will run through all cryptocurrencies on ftx.com/markets and extract information. 
    
    FULLSCREEN REQUIRED
    
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

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        PATH = "/usr/local/bin/chromedriver"
        self.driver = webdriver.Chrome(PATH, options=options)

        DATABASE_TYPE = aws_creds.DATABASE_TYPE
        DBAPI = aws_creds.DBAPI
        HOST = aws_creds.HOST
        USER = aws_creds.USER
        PASSWORD = aws_creds.PASSWORD
        PORT = aws_creds.PORT
        DATABASE = aws_creds.DATABASE

        self.url = url
        self.all_url = []
        self.valid_url = []

        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
        self.client = boto3.client('s3')

        self.driver.get(self.url)
        
        self.crypto_dictionary = {
                                    'UUID':[],
                                    'Link':[],
                                    'Name':[],
                                    'Price':[],
                                    'Time':[],
                                    #'Percentage increase':[]
                                } 
        self.global_dictionary = {
                                        'UUID':[],
                                        'Link':[],
                                        'Name':[],
                                        'Price':[],
                                        'Time':[],
                                        #'Percentage increase':[]
                                } 

    def find_all_links(self):
        '''
        This method will find all links found on the website and compile it in a list.

        Returns
        -------
        all_url: list
            An alphabetically ordered list of all url on the website.    
        '''
        try:
            print("Trying to find all url's on FTX")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@href]")))
            loop = self.driver.find_elements(By. XPATH, "//a[@href]")
            for links in loop:
                self.all_url.append(links.get_attribute("href"))
        except:
            print("No links found. Website might not have loaded correctly. Try again.")
        self.all_url.sort()
        print(f"Successfully created list of all url's: {len(self.all_url)}")
        return self.all_url

    def valid_links(self):
        '''
        This method aims to clean the list (all_url) and get only the relevant links (valid_url).
        This scraper will only look at perpetual contracts and not quarterly contracts (PERP in name)

        Returns
        -------
        valid_url: list
            A list of all relevant links which will be looped in the next step.
        '''
        print("Cleaning up list")
        for i in self.all_url:
            if 'USD' in i:
                continue
            if "https://ftx.com/trade/" and "PERP" in i:
                self.valid_url.append(i)
        print(f"Successfully cleaned url list down to {len(self.valid_url)}")
        return self.valid_url

    def download_data(self):
        '''
        This method will loop through the valid_url list and extract the price, name, link and time for every cryptocurrency. 
        Furthermore, it will create a uuid for every entry and save it in the dictionary. It will also create directories for every cryptocurrency and save a json
        and a screenshot of the market in those directories with time stamps.
        
        Creates
        -------
        crypto named files: json
            A json file with the cryptocurrency name, uuid, price and link

        screenshots: png
            A screenshot of the last 24 hours market value.
        '''
        print("Starting loop and extracting information")
        count = 0
        for links in self.valid_url[:10]:
            crypto_name = links.split("/")[-1]
            if crypto_name in self.global_dictionary['Name']:
                continue
            self.driver.get(links)
            current_time = datetime.datetime.now()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[2]/div[1]/main[1]/div[3]/div[3]/div[1]/div[1]/div[1]/span[1]/p[2]"))) 
            time.sleep(1)
            try:
                self.crypto_dictionary['UUID'].append(str(uuid.uuid4()))
                self.global_dictionary['UUID'].append(str(uuid.uuid4()))
            except NoSuchElementException:
                self.crypto_dictionary['UUID'].append('N/A')
                self.global_dictionary['UUID'].append('N/A')
            try:
                value = self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[2]/div[1]/main[1]/div[3]/div[3]/div[1]/div[1]/div[1]/span[1]/p[2]").text
                self.crypto_dictionary['Price'].append(value)
                self.global_dictionary['Price'].append(value)
            except NoSuchElementException:
                self.crypto_dictionary['Price'].append('N/A')
                self.global_dictionary['Price'].append('N/A')
            try:
                self.crypto_dictionary['Link'].append(links)
                self.global_dictionary['Link'].append(links)
            except NoSuchElementException:
                self.crypto_dictionary['Link'].append('N/A')
                self.global_dictionary['Link'].append('N/A')
            try:
                self.crypto_dictionary['Name'].append(crypto_name)
                self.global_dictionary['Name'].append(crypto_name)
            except NoSuchElementException:
                self.crypto_dictionary['Name'].append('N/A')
                self.global_dictionary['Name'].append('N/A')
            self.crypto_dictionary['Time'].append(current_time.strftime("%c"))
            self.global_dictionary['Time'].append(current_time.strftime("%c"))
            count = count + 1
            print(f'Downloading data:(json) and taking screenshot:(png) for {crypto_name}, {count}/{len(self.valid_url)}.')
            if not os.path.exists(f'./raw_data/{crypto_name}'):
                os.makedirs(f'./raw_data/{crypto_name}')
            with open(f'./raw_data/{crypto_name}/{crypto_name}.json', 'w') as fp:
                json.dump(self.crypto_dictionary, fp)
            try:
                self.driver.save_screenshot(f'./raw_data/{crypto_name}/{current_time}.png')
            except NoSuchElementException:
                print(f"No screenshot was made for {crypto_name}.")
        dataframe = pd.DataFrame(self.global_dictionary)
        dataframe.to_csv('./raw_data/dataframe.csv', index = False)

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
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h5[@class='MuiTypography-root MuiTypography-h5']")))   
            time.sleep(1)
            crypto_name = links.split("/")[-1]
            try:
                self.crypto_dictionary['UUID'].append(self.unique_id)
                self.global_dictionary['UUID'].append(self.unique_id)
            except NoSuchElementException:
                self.crypto_dictionary['UUID'].append('N/A')
                self.global_dictionary['UUID'].append('N/A')
            try:
                value = self.driver.find_element(By.XPATH, "//h5[@class='MuiTypography-root MuiTypography-h5']").text
                self.crypto_dictionary['Price'].append(value)
                self.global_dictionary['Price'].append(value)
            except NoSuchElementException:
                self.crypto_dictionary['Price'].append('N/A')
                self.global_dictionary['Price'].append('N/A')
            try:
                self.crypto_dictionary['Link'].append(links)
                self.global_dictionary['Link'].append(links)
            except NoSuchElementException:
                self.crypto_dictionary['Link'].append('N/A')
                self.global_dictionary['Link'].append('N/A')
            try:
                self.crypto_dictionary['Name'].append(crypto_name)
                self.global_dictionary['Name'].append(crypto_name)
            except NoSuchElementException:
                self.crypto_dictionary['Name'].append('N/A')
                self.global_dictionary['Name'].append('N/A')
            self.crypto_dictionary['Time'].append(datetime.datetime.now().strftime("%c"))
            self.global_dictionary['Time'].append(datetime.datetime.now().strftime("%c"))
            count = count + 1
            print(f'Uploading data:(json) and screenshot:(png) for {crypto_name}, {count}/{len(self.valid_url)}.')
            with tempfile.TemporaryDirectory() as tmpdirname:
                try:
                    self.driver.save_screenshot(tmpdirname + f'/{crypto_name}.png')
                    self.client.upload_file(tmpdirname + f'/{crypto_name}.png', 'ftx-scraper', f'{crypto_name}_{self.current_time.strftime("%c")}.png')
                except NoSuchElementException:
                    print(f"No screenshot was made for {crypto_name}!")
                with open(tmpdirname + f'/{crypto_name}.json', 'w') as fp:
                    json.dump(self.crypto_dictionary, fp)
                self.client.upload_file(tmpdirname + f'/{crypto_name}.json', 'ftx-scraper', f'{crypto_name}_{self.current_time.strftime("%c")}.json')
        dataframe = pd.DataFrame(self.global_dictionary)
        dataframe.to_sql('ftx-dataframe', con=self.engine, if_exists='append', index=False)