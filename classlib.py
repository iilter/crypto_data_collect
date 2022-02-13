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
            log.moduleName = type(self).__name__  # "FearAndGreed().addData()"
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
            # if cursor is None:
            #     print("Http Error:", errh)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = "FearAndGreed getData()"
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            # if cursor is None:
            #     print("Error Connecting:", errc)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = "FearAndGreed getData()"
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            # if cursor is None:
            #     print("Timeout Error:", errt)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = "FearAndGreed getData()"
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            # if cursor is None:
            #     print(err)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = "FearAndGreed getData()"
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
            log.moduleName = type(self).__name__  # "TakerBuySell addData()"
            log.explanation = "INSERT INTO taker_buy_sell"
            log.addData()

    def getData(self,
                url=None,
                accessToken=None,
                exchange=None,
                window=None,
                fromDate=None,
                toDate=None,
                limit=1,
                returnFormat=None):

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
            # if cursor is None:
            #     print("Http Error:", errh)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errh.response.status_code
            log.errorMessage = errh.response.text
            log.moduleName = "TakerBuySell getData()"
            log.explanation = "Http Error: " + errh.response.url
            log.addData()
        except requests.exceptions.ConnectionError as errc:
            # if cursor is None:
            #     print("Error Connecting:", errc)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errc.response.status_code
            log.errorMessage = errc.response.text
            log.moduleName = "TakerBuySell getData()"
            log.explanation = "Error Connecting: " + errc.response.url
            log.addData()
        except requests.exceptions.Timeout as errt:
            # if cursor is None:
            #     print("Timeout Error:", errt)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = errt.response.status_code
            log.errorMessage = errt.response.text
            log.moduleName = "TakerBuySell getData()"
            log.explanation = "Timeout Error: " + errt.response.url
            log.addData()
        except requests.exceptions.RequestException as err:
            # if cursor is None:
            #     print(err)
            # else:
            log = ErrorLog()
            log.cursor = cursor
            log.errorNo = err.response.status_code
            log.errorMessage = err.response.text
            log.moduleName = "TakerBuySell getData()"
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
