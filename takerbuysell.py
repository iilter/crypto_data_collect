from datetime import datetime
import sys
import mariadb
import click

import funclib
from classlib import ConfigFile as cfg
from classlib import TakerBuySell as takerBuySellClass


@click.command()
@click.option('--exchange', default='all_exchange', help='A derivative exchange')
@click.option('--window', default='day', help='support day, hour, and min')
@click.option('--from_date', default='',
              help='If window=day is used, it can also be formatted as YYYYMMDD (date)')
@click.option('--to_date', default='',
              help='If window=day is used, it can also be formatted as YYYYMMDD (date)')
@click.option('--limit', default='1',
              help='The maximum number of records to return before the latest data point (or before to if specified)')
@click.option('--return_format', default='json',
              help='A format type about return message type. Supported formats are json, csv')
def main(exchange, window, from_date, to_date, limit, return_format):
    print(f"exchange={exchange}")
    print(f"window={window}")
    print(f"from_date={from_date}")
    print(f"to_date={to_date}")
    print(f"limit={limit}")
    print(f"return_format={return_format}")

    #
    # Programa dışarıdan argüman olarak verilip verilmediği kontrol edilir.
    # Arguman sayısı (sys.argv[1]) > 1 ise programa dışarıdan argüman verilmiştir.
    # Çekilecek kayıt sayısı programa argüman olarak verilmemiş ise tek (son) kayıt çekmek için değer 1 yapılır.
    # sys.argv[0] da programın ismi yer alır
    #
    # argumentRecordCount = 1
    # if len(sys.argv) > 1:
    #     argumentRecordCount = sys.argv[1]

    # config_dir = funclib.resource_path("config")
    # config_file = config_dir + '\\' + 'config.ini'
    config_file = 'config.ini'
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

    # Read cryptoquant section from config.ini
    try:
        config.section = "cryptoquant"
        quantConfig = config.readConfig()
    except Exception as ex:
        # print(f"Could not read config file")
        funclib.log_traceback(ex)
        sys.exit(1)

    # print(f"{quantConfig}")

    url = quantConfig["url"]
    accessToken = quantConfig["access_token"]

    buysell = takerBuySellClass()
    buysell.cursor = cursor
    records = buysell.getData(url, accessToken, exchange, window, from_date, to_date, limit, return_format)
    if (records is not None) and (len(records) > 0):
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
