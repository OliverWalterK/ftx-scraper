# ftx-scraper
AiCore's Scraper Project (FTX)

I have made a scraper that can loop all cryptocurrencies found on ftx.com.
I extract data such as the name, link and price for each cryptocurrency. I also take a screenshot of the last 24 hours of traffic.

This scraper has two methods for either downloading the data locally or uploading the data to a s3 bucket.

Unittest
--------

I have also added a unittest in order to check whether the returned datatypes are correct. 
1. Whether each entry in the list is a string type.
2. It checks whether the links in valid_links() actually start with "https://ftx.com/trade/". 
3. It check if the get_all_links() and valid_links() methods return a list.





