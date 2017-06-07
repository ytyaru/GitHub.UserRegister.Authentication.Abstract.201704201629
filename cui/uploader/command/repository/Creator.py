#!python3
#encoding:utf-8
import subprocess
import shlex
import datetime
import time
import pytz
import requests
import json

class Creator:
    def __init__(self, db, client, authData, repo):
        self.__db = db
        self.__client = client
        self.__authData = authData
        self.__repo = repo
        self.__userRepo = self.__db.Repositories[self.__authData.Username]

    def Create(self):
        self.__CreateLocalRepository()
        j = self.__client.Repositories.create(self.__repo.Name, description=self.__repo.Description, homepage=self.__repo.Homepage)
        self.__InsertRemoteRepository(j)

    def __CreateLocalRepository(self):
        subprocess.call(shlex.split("git init"))
        subprocess.call(shlex.split("git config --local user.name '{0}'".format(self.__authData.Username)))
        subprocess.call(shlex.split("git config --local user.email '{0}'".format(self.__authData.MailAddress)))
        subprocess.call(shlex.split("git remote add origin git@{0}:{1}/{2}.git".format(self.__authData.SshHost, self.__authData.Username, self.__repo.Name)))
    
    def __InsertRemoteRepository(self, j):
        self.__userRepo.begin()
        repo = self.__userRepo['Repositories'].find_one(Name=j['name'])
        # Repositoriesテーブルに挿入する
        if None is repo:
            self.__userRepo['Repositories'].insert(self.__CreateRecordRepositories(j))
            repo = self.__userRepo['Repositories'].find_one(Name=j['name'])
        # 何らかの原因でローカルDBに既存の場合はそのレコードを更新する
        else:
            self.__userRepo['Repositories'].update(self.__CreateRecordRepositories(j), ['Name'])

        # Countsテーブルに挿入する
        cnt = self.__userRepo['Counts'].count(RepositoryId=repo['Id'])
        if 0 == cnt:
            self.__userRepo['Counts'].insert(self.__CreateRecordCounts(self.__userRepo['Repositories'].find_one(Name=j['name'])['Id'], j))
        # 何らかの原因でローカルDBに既存の場合はそのレコードを更新する
        else:
            self.__userRepo['Counts'].update(self.__CreateRecordCounts(repo['Id'], j), ['RepositoryId'])
        self.__userRepo.commit()

    def __CreateRecordRepositories(self, j):
        return dict(
            IdOnGitHub=j['id'],
            Name=j['name'],
            Description=j['description'],
            Homepage=j['homepage'],
            CreatedAt=j['created_at'],
            PushedAt=j['pushed_at'],
            UpdatedAt=j['updated_at'],
            CheckedAt="{0:%Y-%m-%dT%H:%M:%SZ}".format(datetime.datetime.now(pytz.utc))
        )

    def __CreateRecordCounts(self, repo_id, j):
        return dict(
            RepositoryId=repo_id,
            Forks=j['forks_count'],
            Stargazers=j['stargazers_count'],
            Watchers=j['watchers_count'],
            Issues=j['open_issues_count']
        )
