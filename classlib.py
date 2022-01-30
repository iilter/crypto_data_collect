from configparser import ConfigParser
import mariadb
import requests


class ConfigFile:
    def __init__(self, filename='config/config.ini', section='mariadb'):
        self.filename = filename
        self.section = section

    def readConfig(self):
        # create parser and read ini configuration file
        parser = ConfigParser()
        parser.read(self.filename)

        # get section, default to mysql
        db = {}
        if parser.has_section(self.section):
            items = parser.items(self.section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(self.section, self.filename))
        return db


class FearAndGreed:
    def __init__(self, cursor=None, indexDate=None, indexValue=None, classification=None):
        self.cursor = cursor
        self.indexDate = indexDate
        self.indexValue = indexValue
        self.classification = classification

    def addData(self):
        print("addData")
        try:
            self.cursor.execute("INSERT INTO feargreed (index_date, index_value, classification) VALUES (?, ?, ?)",
                                (self.indexDate, self.indexValue, self.classification))
        except mariadb.Error as e:
            print(f"Error: {e}")

    @staticmethod
    def getData(periodCount):
        print("getData method")
        url = 'https://api.alternative.me/fng/'
        prm = {'limit': periodCount}
        response = requests.get(url, params=prm)
        records = response.json()
        #    print('Type:', type(records))
        return records['data']
