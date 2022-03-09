import boto3
import sqlalchemy
from sqlalchemy import create_engine


# client = boto3.client("s3")

# client.upload_file("test2.py", "ftx-scraper", "test2.py")

DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
ENDPOINT = 'ftx-scraper2.cn4izzmm7yyd.eu-west-2.rds.amazonaws.com' # Change it for your AWS endpoint
USER = 'postgres'
PASSWORD = '91Weporting'
PORT = 5432
DATABASE = 'postgres'
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")

engine.connect()