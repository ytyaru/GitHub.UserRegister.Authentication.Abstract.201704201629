#!python3
#encoding:utf-8
import subprocess
import shlex
import time
import requests
import json

class Commiter:
    def __init__(self, db, client, authData, repo):
        self.__db = db
        self.__client = client
        self.__authData = authData
        self.__repo = repo
        self.__userRepo = self.__db.Repositories[self.__authData.Username]

    def ShowCommitFiles(self):
        subprocess.call(shlex.split("git add -n ."))

    def AddCommitPush(self, commit_message):
        subprocess.call(shlex.split("git add ."))
        subprocess.call(shlex.split("git commit -m '{0}'".format(commit_message)))
        subprocess.call(shlex.split("git push origin master"))
        time.sleep(3)
        self.__InsertLanguages(self.__client.Repositories.list_languages())

    def __InsertLanguages(self, j):
        self.__userRepo.begin()
        repo_id = self.__userRepo['Repositories'].find_one(Name=self.__repo.Name)['Id']
        self.__userRepo['Languages'].delete(RepositoryId=repo_id)
        for key in j.keys():
            self.__userRepo['Languages'].insert(dict(
                RepositoryId=repo_id,
                Language=key,
                Size=j[key]
            ))
        self.__userRepo.commit()

