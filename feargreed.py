import os
import sys
from datetime import datetime

import mariadb as mariadb

from classlib import ConfigFile as cfg
from classlib import FearAndGreed as fagClass


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def main():
    # Read config.ini file
    try:
        config_dir = resource_path("config")
        file_name = config_dir + '\\' + 'config.ini'
        config = cfg()
        config.filename = file_name
        config.section = "mariadb"
        dbConfig = config.readConfig()
        # print(dbConfig)
    except:
        print(f"Could not read config file")
        sys.exit(1)

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

    fag = fagClass()
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

    dbConnection.commit()
    dbConnection.close()


if __name__ == '__main__':
    main()
