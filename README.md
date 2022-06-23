# ftx-scraper
Scraper Project (FTX) using Selenium Webdriver.
-----------------------------------------------

Overview
--------

I have made a scraper that can loop through all cryptocurrencies found on http://www.ftx.com.
I extract data such as the crypto name, url, price and save them in a json file. The scraper also takes a screenshot of the last 24 hours of traffic.

The scraper has two options for either downloading the data locally or uploading the data to my S3 bucket and a RDS on AWS.

When downloading the data locally, it will create folders for every cryptocurrency and store the data in json files. The screenshot will be saved as a png file.
![image](https://user-images.githubusercontent.com/97681246/175306791-e566aed5-d2fa-4c45-a7f1-3e8085fcfd1e.png)
![image](https://user-images.githubusercontent.com/97681246/175308368-b09368af-d72b-41bb-add4-1ad55ada005b.png)

The upload method will simply create the json and png files in the S3 bucket and RDS with timestamps
![image](https://user-images.githubusercontent.com/97681246/175307697-8a6e8dd2-4b9c-4068-bce6-8a1164a78341.png)

Docker
------

The ftx-scraper has a docker image, for uploading the data to my AWS S3 bucket, which can be found here: https://hub.docker.com/r/walteroli91/ftx-scraper-ec2.

The script was modified (-headless mode) to allow the docker image to run on EC2 instances. 

It also added a .yml file in order to monitor the docker containers on prometheus or grafana.

I added a github action for CI/CD which will automatically update the docker image when there is a git push.

Unittest
--------

I have also added a unittest in order to check whether the returned datatypes are correct. 
1. Whether each entry in the list is a string type.
2. It checks whether the links in valid_links() actually start with "https://ftx.com/trade/". 
3. It check if the get_all_links() and valid_links() methods return a list.
4. Whether the value for the cryptocurrency on the website gives a float.
