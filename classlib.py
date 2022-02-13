from configparser import ConfigParser
from datetime import datetime
from datetime import timedelta
import mariadb
import requests
import funclib


class ConfigFile:
    def __init__(self, filename="config.ini", section=None):
        self.filename = filename
        self.section = section

    def readConfig(self):
        # create parser and read ini configuration file
        parser = ConfigParser()
        if not (parser.read(self.filename)):
            raise Exception("{0} file not found".format(self.filename))

        # get section, default to mysql
        parameters = {}
        if parser.has_section(self.section):
            items = parser.items(self.section)
            for item in items:
                parameters[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(self.section, self.filename))
        return parameters


class FearAndGreed:
    def __init__(self, cursor=None, periodDate=None, periodTime=None, indexValue=None, classification=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")):
        self.cursor = cursor
        self.periodDate = periodDate
        self.periodTime = periodTime
        self.indexValue = indexValue
        self.classification = classification
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO fear_greed (period_date, period_time, fear_index, classification, "
                                "update_date, update_time) VALUES (?, ?, ?, ?, ?, ?)",
                                (self.periodDate, self.periodTime, self.indexValue, self.classification,
                                 self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO fear_greed"
            log.addData()

    def getData(self, url=None, limit=1, returnFormat=None):
        #
        # limit = 0 ise bütün index bilgileri çekilir
        # limit = 1 ise son index bilgisi çekilir
        # limit = N ise son N tane index bilgisi çekilir
        #
        cursor = self.cursor
        prm = {'limit': limit, 'format': returnFormat}
        try:
            response = requests.get(url, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class TakerBuySell:
    def __init__(self, cursor=None, indexDate=None, takerBuyVolume=None, takerSellVolume=None,
                 takerBuyRatio=None, takerSellRatio=None, takerBuySellRatio=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")
                 ):
        self.cursor = cursor
        self.indexDate = indexDate
        self.takerBuyVolume = takerBuyVolume
        self.takerSellVolume = takerSellVolume
        self.takerBuyRatio = takerBuyRatio
        self.takerSellRatio = takerSellRatio
        self.takerBuySellRatio = takerBuySellRatio
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO taker_buy_sell (index_date, taker_buy_volume, taker_sell_volume, "
                                "taker_buy_ratio, taker_sell_ratio, taker_buy_sell_ratio, "
                                "update_date, update_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (self.indexDate, self.takerBuyVolume, self.takerSellVolume,
                                 self.takerBuyRatio, self.takerSellRatio, self.takerBuySellRatio,
                                 self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO taker_buy_sell"
            log.addData()

    def getData(self, url=None, accessToken=None, exchange=None, window=None, fromDate=None,
                toDate=None, limit=1, returnFormat=None):

        # fromDate = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

        cursor = self.cursor
        headers = {'Authorization': 'Bearer ' + accessToken}

        # fromDate girilmemiş ise en erken tarihten itibaren
        # toDate girilmemiş ise en son son tarihten itibaren
        if (toDate == '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate == '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        try:
            response = requests.get(url, headers=headers, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['result']['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class FundingRates:
    def __init__(self, cursor=None, indexDate=None, fundingRates=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")
                 ):
        self.cursor = cursor
        self.indexDate = indexDate
        self.fundingRates = fundingRates
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO funding_rates (index_date, funding_rates, "
                                "update_date, update_time) VALUES (?, ?, ?, ?)",
                                (self.indexDate, self.fundingRates, self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO funding_rates"
            log.addData()

    def getData(self, url=None, accessToken=None, exchange=None, window=None, fromDate=None,
                toDate=None, limit=1, returnFormat=None):

        cursor = self.cursor
        headers = {'Authorization': 'Bearer ' + accessToken}

        # fromDate girilmemiş ise en erken tarihten itibaren
        # toDate girilmemiş ise en son son tarihten itibaren
        if (toDate == '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate == '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        try:
            response = requests.get(url, headers=headers, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['result']['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class Liquidation:
    def __init__(self, cursor=None, indexDate=None, longLiquidations=None, shortLiquidations=None,
                 longLiquidationsUSD=None, shortLiquidationsUSD=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")
                 ):
        self.cursor = cursor
        self.indexDate = indexDate
        self.longLiquidations = longLiquidations
        self.shortLiquidations = shortLiquidations
        self.longLiquidationsUSD = longLiquidationsUSD
        self.shortLiquidationsUSD = shortLiquidationsUSD
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO liquidation (index_date, long_liquidations, short_liquidations, "
                                "long_liquidations_usd, short_liquidations_usd, "
                                "update_date, update_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (self.indexDate, self.longLiquidations, self.shortLiquidations,
                                 self.longLiquidationsUSD, self.shortLiquidationsUSD,
                                 self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO liquidation"
            log.addData()

    def getData(self, url=None, accessToken=None, exchange=None, window=None, fromDate=None,
                toDate=None, limit=1, returnFormat=None):

        cursor = self.cursor
        headers = {'Authorization': 'Bearer ' + accessToken}

        # fromDate girilmemiş ise en erken tarihten itibaren
        # toDate girilmemiş ise en son son tarihten itibaren
        if (toDate == '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate == '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        try:
            response = requests.get(url, headers=headers, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['result']['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class OpenInterest:
    def __init__(self, cursor=None, indexDate=None, openInterest=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")
                 ):
        self.cursor = cursor
        self.indexDate = indexDate
        self.openInterest = openInterest
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO open_interest (index_date, open_interest, "
                                "update_date, update_time) VALUES (?, ?, ?, ?)",
                                (self.indexDate, self.openInterest, self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO open_interest"
            log.addData()

    def getData(self, url=None, accessToken=None, exchange=None, window=None, fromDate=None,
                toDate=None, limit=1, returnFormat=None):

        cursor = self.cursor
        headers = {'Authorization': 'Bearer ' + accessToken}

        # fromDate girilmemiş ise en erken tarihten itibaren
        # toDate girilmemiş ise en son son tarihten itibaren
        if (toDate == '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate == '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        try:
            response = requests.get(url, headers=headers, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['result']['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class Nupl:
    def __init__(self, cursor=None, indexDate=None, nupl=None, nup=None, nul=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")
                 ):
        self.cursor = cursor
        self.indexDate = indexDate
        self.nupl = nupl
        self.nup = nup
        self.nul = nul
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO nupl (index_date, nupl, nup, nul, "
                                "update_date, update_time) VALUES (?, ?, ?, ?, ?, ?)",
                                (self.indexDate, self.nupl, self.nup, self.nul, self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO nupl"
            log.addData()

    def getData(self, url=None, accessToken=None, window=None, fromDate=None,
                toDate=None, limit=1, returnFormat=None):

        cursor = self.cursor
        headers = {'Authorization': 'Bearer ' + accessToken}

        # fromDate girilmemiş ise en erken tarihten itibaren
        # toDate girilmemiş ise en son son tarihten itibaren
        if (toDate == '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        if (toDate == '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        try:
            response = requests.get(url, headers=headers, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['result']['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class Sopr:
    def __init__(self, cursor=None, indexDate=None, sopr=None, aSopr=None, sthSopr=None, lthSopr=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")
                 ):
        self.cursor = cursor
        self.indexDate = indexDate
        self.sopr = sopr
        self.aSopr = aSopr
        self.sthSopr = sthSopr
        self.lthSopr = lthSopr
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO sopr (index_date, sopr, a_sopr, sth_sopr, lth_sopr, "
                                "update_date, update_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (self.indexDate, self.sopr, self.aSopr, self.sthSopr, self.lthSopr,
                                 self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO sopr"
            log.addData()

    def getData(self, url=None, accessToken=None, window=None, fromDate=None,
                toDate=None, limit=1, returnFormat=None):
        cursor = self.cursor
        headers = {'Authorization': 'Bearer ' + accessToken}

        # fromDate girilmemiş ise en erken tarihten itibaren
        # toDate girilmemiş ise en son son tarihten itibaren
        if (toDate == '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        if (toDate == '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'format': returnFormat
                   }
        try:
            response = requests.get(url, headers=headers, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['result']['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class Leverage:
    def __init__(self, cursor=None, indexDate=None, estimatedLeverageRatio=None,
                 updateDate=datetime.now().strftime("%Y-%m-%d"),
                 updateTime=datetime.now().strftime("%H:%M:%S")
                 ):
        self.cursor = cursor
        self.indexDate = indexDate
        self.estimatedLeverageRatio = estimatedLeverageRatio
        self.updateDate = updateDate
        self.updateTime = updateTime

    def addData(self):
        try:
            self.cursor.execute("INSERT INTO leverage (index_date, estimated_leverage_ratio, "
                                "update_date, update_time) VALUES (?, ?, ?, ?)",
                                (self.indexDate, self.estimatedLeverageRatio,
                                 self.updateDate, self.updateTime))
        except mariadb.Error as e:
            # print(f"Error: {e.errno} {e.errmsg}")
            log = ErrorLog()
            log.cursor = self.cursor
            log.errorNo = e.errno
            log.errorMessage = e.errmsg
            log.moduleName = type(self).__name__
            log.explanation = "INSERT INTO leverage"
            log.addData()

    def getData(self, url=None, accessToken=None, exchange=None, window=None, fromDate=None,
                toDate=None, limit=1, returnFormat=None):

        cursor = self.cursor
        headers = {'Authorization': 'Bearer ' + accessToken}

        # fromDate girilmemiş ise en erken tarihten itibaren
        # toDate girilmemiş ise en son son tarihten itibaren
        if (toDate == '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate == '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   # 'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate == ''):
            prm = {'window': window,
                   # 'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        if (toDate != '') and (fromDate != ''):
            prm = {'window': window,
                   'from': fromDate,
                   'to': toDate,
                   'limit': limit,
                   'exchange': exchange,
                   'format': returnFormat
                   }
        try:
            response = requests.get(url, headers=headers, params=prm)
            response.raise_for_status()
            records = response.json()
            return records['result']['data']
        except requests.exceptions.HTTPError as errh:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = type(self).__name__
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = type(self).__name__
            log.explanation = err.response.url
            log.addData()


class ErrorLog:
    def __init__(self, cursor=None, transactionDate=datetime.now().strftime("%Y-%m-%d"),
                 transactionTime=datetime.now().strftime("%H:%M:%S"), moduleName=None, errorNo=None,
                 errorMessage=None, explanation=None):
        self.cursor = cursor
        self.transactionDate = transactionDate
        self.transactionTime = transactionTime
        self.moduleName = moduleName
        self.errorNo = errorNo
        self.errorMessage = errorMessage
        self.explanation = explanation

    def addData(self):
        if self.cursor is None:
            funclib.log_error(f"{self.moduleName} {self.errorNo} {self.errorMessage}")
        else:
            try:
                self.cursor.execute("INSERT INTO errorlog (transaction_date, transaction_time, module_name, error_no, "
                                    "error_message, explanation) VALUES (?, ?, ?, ?, ?, ?)",
                                    (self.transactionDate, self.transactionTime, self.moduleName, self.errorNo,
                                     self.errorMessage, self.explanation))
            except mariadb.Error as ex:
                # print(f"Error: {ex.errno} {ex.errmsg}")
                funclib.log_traceback(ex)
