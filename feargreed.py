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

    config_dir = resource_path("config")
    config_file = config_dir + '\\' + 'config.ini'
    # Read database section from config.ini
    config = cfg()
    config.filename = config_file
    try:
        config.section = "database"
        dbConfig = config.readConfig()
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

    # Read fearandgreed section from config.ini
    try:
        config.section = "fearandgreed"
        fagConfig = config.readConfig()
    except:
        print(f"Could not read config file")
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
