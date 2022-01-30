import sys
import json
from datetime import datetime

import mariadb as mariadb

import classlib as apilib

if __name__ == '__main__':
    config = apilib.ConfigFile()
    config.section = "mariadb"
    dbConfig = config.readConfig()
    print(dbConfig)

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
    records = fag.getData(2)
    #    records = api.getFearAndGreedData(2)
    for ix in records:
        value = int(ix['value'])
        classification = ix['value_classification']
        ts = int(ix['timestamp'])
        dt = datetime.fromtimestamp(ts)

        #     db.addFearAndGreed(cursor, dt, value, classification)
        fag.cursor = cursor
        fag.indexValue = value
        fag.indexDate = dt
        fag.classification = classification
        fag.addData()

