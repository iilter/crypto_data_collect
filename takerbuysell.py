from datetime import datetime
import sys
import mariadb

import funclib
from classlib import ConfigFile as cfg
from classlib import TakerBuySell as takerBuySellClass


def main():
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

    # Read cryptoquant section from config.ini
    try:
        config.section = "cryptoquant"
        quantConfig = config.readConfig()
    except:
        print(f"Could not read config file")
        sys.exit(1)

    print(f"{quantConfig}")

    url = quantConfig["url"]
    accessToken = quantConfig["access_token"]

    buysell = takerBuySellClass()
    buysell.cursor = cursor
    records = buysell.getData(url, accessToken, argumentRecordCount)
    print(f"{records}")
    print(f"{len(records)}")
    for record in records:
        dt = datetime.strptime(record["date"], "%Y-%m-%d").date()
        buysell.indexDate = dt
        buysell.takerBuyVolume = record["taker_buy_volume"]
        buysell.takerSellVolume = record["taker_sell_volume"]
        buysell.takerBuyRatio = record["taker_buy_ratio"]
        buysell.takerSellRatio = record["taker_sell_ratio"]
        buysell.takerBuySellRatio = record["taker_buy_sell_ratio"]
        buysell.addData()

    dbConnection.commit()
    dbConnection.close()

main()
