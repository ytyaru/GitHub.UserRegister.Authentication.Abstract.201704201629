#!python3
#encoding:utf-8
import os
import subprocess
import shlex
import shutil
import time
import pytz
import requests
import json
import datetime

class Deleter:
    def __init__(self, db, client, authData, repo):
        self.__db = db
        self.__client = client
        self.__authData = authData
        self.__repo = repo
        self.__userRepo = self.__db.Repositories[self.__authData.Username]

    def ShowDeleteRecords(self):
        repo = self.__userRepo['Repositories'].find_one(Name=self.__repo.Name)
        print(repo)
        print(self.__userRepo['Counts'].find_one(RepositoryId=repo['Id']))
        for record in self.__userRepo['Languages'].find(RepositoryId=repo['Id']):
            print(record)

    def Delete(self):
        self.__DeleteLocalRepository()
        self.__client.Repositories.delete()
        self.__DeleteDb()

    def __DeleteLocalRepository(self):
        shutil.rmtree('.git')

    def __DeleteDb(self):
        repo = self.__userRepo['Repositories'].find_one(Name=self.__repo.Name)
        self.__userRepo.begin()
        self.__userRepo['Repositories'].delete(Id=repo['Id'])
        self.__userRepo['Counts'].delete(RepositoryId=repo['Id'])
        self.__userRepo['Languages'].delete(RepositoryId=repo['Id'])
        self.__userRepo.commit()

