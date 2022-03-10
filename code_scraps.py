import os

with open(os.path.expanduser('~/.aws/credentials')) as creds:
    credentials = creds.readlines()
    print(credentials)