from datetime import datetime
import sys
import mariadb
import click

import funclib
from classlib import ConfigFile as cfg
from classlib import ExchangeToExchange as exchangeToExchangeClass


@click.command()
@click.option('--from_exchange', default='binance', help='An exchange')
@click.option('--to_exchange', default='all_exchange', help='An exchange')
@click.option('--window', default='day', help='support day, hour, and min')
@click.option('--from_date', default='',
              help='If window=day is used, it can also be formatted as YYYYMMDD (date)')
@click.option('--to_date', default='',
              help='If window=day is used, it can also be formatted as YYYYMMDD (date)')
@click.option('--limit', default='1',
              help='The maximum number of records to return before the latest data point (or before to if specified)')
@click.option('--branch', default='dynamic', help='dynamic or stable')
@click.option('--return_format', default='json',
              help='A format type about return message type. Supported formats are json, csv')
def main(from_exchange, to_exchange, window, from_date, to_date, limit, branch, return_format):
    print(f"from_exchange={from_exchange}")
    print(f"to_exchange={to_exchange}")
    print(f"window={window}")
    print(f"from_date={from_date}")
    print(f"to_date={to_date}")
    print(f"limit={limit}")
    print(f"branch={branch}")
    print(f"return_format={return_format}")

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

    url = quantConfig["url_exchange_to_exchange"]
    accessToken = quantConfig["access_token"]

    api = exchangeToExchangeClass()
    api.cursor = cursor
    records = api.getData(url, accessToken, from_exchange, to_exchange, window, from_date, to_date,
                          limit, branch, return_format)
    if (records is not None) and (len(records) > 0):
        print(f"{records}")
        print(f"{len(records)}")
        for record in records:
            dt = datetime.strptime(record["date"], "%Y-%m-%d").date()
            api.indexDate = dt
            api.flowTotal = record["flow_total"]
            api.flowMean = record["flow_mean"]
            api.transactionsCountFlow = record["transactions_count_flow"]
            api.addData()

    dbConnection.commit()
    dbConnection.close()


main()
