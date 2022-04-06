# ftx-scraper
AiCore's Scraper Project (FTX)

I have made a scraper that can loop through all cryptocurrencies found on http://www.ftx.com/trade/.
I extract data such as the crypto name, url and price. I also take a screenshot of the last 24 hours of traffic.

This scraper has two methods for either downloading the data locally or uploading the data to a s3 bucket.

The ftx-scraper has a docker image, for uploading the data to my S3 bucket, which can be found here: https://hub.docker.com/r/walteroli91/ftx-scraper-ec2.

It also added a .yml file in order to monitor containers on prometheus or grafana.

Each push to github will automatically update the docker image.

Unittest
--------

I have also added a unittest in order to check whether the returned datatypes are correct. 
1. Whether each entry in the list is a string type.
2. It checks whether the links in valid_links() actually start with "https://ftx.com/trade/". 
3. It check if the get_all_links() and valid_links() methods return a list.
4. Whether the value for the cryptocurrency on the website gives a float.





