import os
import sys
from datetime import datetime
import mariadb as mariadb

import funclib
from classlib import ConfigFile as cfg
from classlib import FearAndGreed as fagClass


def main():
    # print(f"Arguments count: {len(sys.argv)}")
    # for i, arg in enumerate(sys.argv):
    #     print(f"Argument {i:>6}:{arg}")

    #
    # Çekilecek kayıt sayısının programa dışarıdan argüman olarak verilip verilmediği kontrol edilir.
    # Arguman sayısı > 1 ise dışarıdan verilmiştir (sys.argv[1]).
    # Çekilecek kayıt sayısı programa argüman olarak verilmemiş ise tek (son) kayıt çekmek için değer 1 yapılır.
    # sys.argv[0] da programın ismi yer alır
    #
    argumentRecordCount = 1
    if len(sys.argv) > 1:
        argumentRecordCount = sys.argv[1]

    config_dir = funclib.resource_path("config")
    config_file = config_dir + '\\' + 'config.ini'
    # Read database section from config.ini
    config = cfg()
    config.filename = config_file
    try:
        config.section = "database"
        dbConfig = config.readConfig()
    except Exception as ex:
        # print(f"Could not read config file")
        funclib.log_traceback(ex)
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
    except mariadb.Error as ex:
        # print(f"Error connecting to MariaDB Platform: {ex}")
        funclib.log_traceback(ex)
        sys.exit(1)

    # Get Cursor
    cursor = dbConnection.cursor()

    # Read fearandgreed section from config.ini
    try:
        config.section = "fearandgreed"
        fagConfig = config.readConfig()
    except Exception as ex:
        # print(f"Could not read config file")
        funclib.log_traceback(ex)
        sys.exit(1)

    url = fagConfig["url"]
    fag = fagClass()
    fag.cursor = cursor
    records = fag.getData(url, argumentRecordCount)
    for record in records:
        ts = int(record['timestamp'])
        dt = datetime.fromtimestamp(ts)
        fag.periodDate = dt.strftime("%Y-%m-%d")
        fag.periodTime = dt.strftime("%H:%M:%S")
        fag.indexValue = int(record['value'])
        fag.classification = record['value_classification']
        fag.addData()

    dbConnection.commit()
    dbConnection.close()


main()
