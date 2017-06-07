#!python3
#encoding:utf-8
import time
import pytz
import requests
import json
import datetime
import web.service.github.api.v3.Response
class Licenses:
    def __init__(self, db, client):
        self.__db = db
        self.__response = web.service.github.api.v3.Response.Response()
        self.__client = client

    """
    ライセンスDBを一覧表示する。
    """
    def Show(self):
        print("{0},{1}".format('Key','Name'))
        for license in self.__db.Licenses['Licenses'].find(order_by=['Id']):
            print("{0},{1}".format(license['Key'],license['Name']))

    """
    指定したkeyに一致するライセンスが存在するなら、マスターDBに挿入する。
    @param {string} keyはライセンスのキー。https://developer.github.com/v3/licenses/#get-an-individual-license
    """
    def InsertOne(self, key):
        print(key)
        print(self.__db)
        print(self.__db.Licenses)
        print(self.__db.Licenses['Licenses'])
        if None is not self.__db.Licenses['Licenses'].find_one(Key=key):
            return
        try:
            self.__InsertUpdateLicenses(self.__client.Licenses.GetLicense(key))
        except Exception as e:
            print('%r' % e)

    """
    ライセンスを一覧取得してマスターDBに挿入する。
    https://developer.github.com/v3/licenses/#list-all-licenses
    """
    def Update(self):
        self.__db.Licenses.begin()
        licenses = self.__client.Licenses.GetLicenses()
        for l in licenses:
            license = self.__client.Licenses.GetLicense(l['key'])
            self.__InsertUpdateLicenses(license)
        self.__db.Licenses.commit()

    def __InsertUpdateLicenses(self, j):
        record = self.__db.Licenses['Licenses'].find_one(Key=j['key'])
        if None is record:
            self.__db.Licenses['Licenses'].insert(self.__CreateRecord(j))
        else:
            self.__db.Licenses['Licenses'].update(self.__CreateRecord(j), ['Key'])

    def __CreateRecord(self, j):
        return dict(
            Key=j['key'],
            Name=j['name'],
            SpdxId=j['spdx_id'],
            Url=j['url'],
            HtmlUrl=j['html_url'],
            Featured=self.__BoolToInt(j['featured']),
            Description=j['description'],
            Implementation=j['implementation'],
            Permissions=self.__ArrayToString(j['permissions']),
            Conditions=self.__ArrayToString(j['conditions']),
            Limitations=self.__ArrayToString(j['limitations']),
            Body=j['body']
        )

    def __BoolToInt(self, bool_value):
        if True == bool_value:
            return 1
        else:
            return 0

    def __ArrayToString(self, array):
        ret = ""
        for v in array:
            ret = v + ','
        return ret[:-1]
