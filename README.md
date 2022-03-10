# ftx-scraper
AiCore's Scraper Project (FTX)

I have made a scraper that can loop through different webpages and extract information. For this scraper, I have decided to loop through all cryptocurrencies found on ftx.com.
I extract data such as the crypto name, link and price. I also make screenshots of the last 24 hours of traffic for every crypto.
Another feature this scraper has is that it will upload the data to a s3 bucket on aws for storage.


Unittest
--------

I have also added a test in order to check whether the datatype's that are returned from a method are correct. For instance, it will check whether the links found actually correspond to a cryptocurrency or not. 


