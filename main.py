import sys
from datetime import datetime

import mariadb as mariadb

import classlib as apilib

if __name__ == '__main__':
    config = apilib.ConfigFile()
    config.section = "mariadb"
    dbConfig = config.readConfig()
    # print(dbConfig)

    # Connect to MariaDB Platform
    try:
        dbConnection = mariadb.connect(
            user=dbConfig["user"],
            password=dbConfig["password"],
            host=dbConfig["host"],
            port=int(dbConfig["port"]),
            database=dbConfig["database"],
            autocommit=True
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cursor = dbConnection.cursor()

    fag = apilib.FearAndGreed()
    records = fag.getData(cursor)
    for record in records:
        ts = int(record['timestamp'])
        dt = datetime.fromtimestamp(ts)
        fag.cursor = cursor
        fag.periodDate = dt.strftime("%Y-%m-%d")
        fag.periodTime = dt.strftime("%H:%M:%S")
        fag.indexValue = int(record['value'])
        fag.classification = record['value_classification']
        fag.addData()

