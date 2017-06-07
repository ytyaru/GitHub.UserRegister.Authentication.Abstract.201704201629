#!python3
#encoding:utf-8
import os
import time
import pytz
import requests
import json
import datetime

class Editor:
    def __init__(self, db, client, authData, repo):
        self.__db = db
        self.__client = client
        self.__authData = authData
        self.__repo = repo
        self.__userRepo = self.__db.Repositories[self.__authData.Username]

    def Edit(self, name, description, homepage):
        j = self.__client.Repositories.edit(name, description, homepage)
        self.__EditDb(j)
        # リポジトリ名の変更が成功したら、ディレクトリ名も変更する
        if self.__repo.Name != name:
            os.rename("../" + self.__repo.Name, "../" + name)

    def __EditDb(self, j):
        repo = self.__userRepo['Repositories'].find_one(Name=self.__repo.Name)
        data = {}
        data['Id'] = repo['Id']
        data['Name'] = j['name']
        if not(None is j['description'] or '' == j['description']):
            data['Description'] = j['description']
        if not(None is j['homepage'] or '' == j['homepage']):
            data['Homepage'] = j['homepage']
        data['CreatedAt']=j['created_at']
        data['PushedAt']=j['pushed_at']
        data['UpdatedAt']=j['updated_at']
        data['CheckedAt']="{0:%Y-%m-%dT%H:%M:%SZ}".format(datetime.datetime.now(pytz.utc))
        self.__userRepo['Repositories'].update(data, ['Id'])
