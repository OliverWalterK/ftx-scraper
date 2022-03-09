import boto3
import sqlalchemy
from sqlalchemy import create_engine

# how to upload files onto the s3 database
# client = boto3.client("s3")
# client.upload_file("pickle.pkl", "ftx-scraper", "test2.py")

# DATABASE_TYPE = 'postgresql'
# DBAPI = 'psycopg2'
# HOST = 'ftx-scraper2.cn4izzmm7yyd.eu-west-2.rds.amazonaws.com' 
# USER = 'postgres'
# PASSWORD = '8750Ironpineapple?'
# PORT = 5432
# DATABASE = 'postgres'
# engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# engine.connect()
