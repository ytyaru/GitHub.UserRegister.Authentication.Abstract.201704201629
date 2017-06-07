#!python3
#encoding:utf-8
import os.path
import configparser
import shlex
import subprocess
import dataset
from web.service.github.api.v3.authentication.BasicAuthentication import BasicAuthentication
from web.service.github.api.v3.authentication.TwoFactorAuthentication import TwoFactorAuthentication
from web.service.github.api.v3.authentication.OAuthAuthentication import OAuthAuthentication
import web.service.github.api.v3.AuthenticationData
import web.service.github.api.v3.Client
import database.src.language.insert.Main
import database.src.api.Main
import database.src.gnu_license.create.Main
import database.src.gnu_license.insert.main
import database.src.license.Main
import database.src.license.insert.Main
import database.src.other_repo.insert.Main
import database.src.account.Main
import database.src.repo.insert.command.repositories.Inserter

class Database:
    def __init__(self):
        self.__path_dir_this = os.path.abspath(os.path.dirname(__file__))
        self.__files = {
            'lang': 'GitHub.Languages.sqlite3',
            'api': 'GitHub.Apis.sqlite3',
            'gnu_license': 'GNU.Licenses.sqlite3',
            'account': 'GitHub.Accounts.sqlite3',
            'license': 'GitHub.Licenses.sqlite3',
            'other_repo': 'GitHub.Repositories.__other__.sqlite3',
            'repo': 'GitHub.Repositories.{user}.sqlite3',
        }        
        self.__lang = None
        self.__api = None
        self.__gnu_license = None
        self.__account = None
        self.__license = None
        self.__other_repo = None
        self.__repo = None
        self.__repos = {}

#    def __GetPaths(self):
#        return self.__files
#    Paths = property(__GetPaths)
    @property
    def Paths(self):
        return self.__files
    @property
    def Languages(self):
        return self.__lang
    @property
    def Apis(self):
        return self.__api
    @property
    def GnuLicenses(self):
        return self.__gnu_license
    @property
    def Accounts(self):
        return self.__account
    @property
    def Licenses(self):
        return self.__license
    @property
    def OtherRepositories(self):
        return self.__other_repo
    @property
    def Repositories(self):
        return self.__repos

    # 1. 全DBのファイルパス作成
    # 2. マスターDBファイルがないなら
    # 2-1. マスターDBファイル作成
    # 2-2. マスターDBデータ挿入
    # 3. アカウントDBがないなら
    # 3-1. アカウントDBファイル作成
    def Initialize(self):
        config = configparser.ConfigParser()
        config.read('./config.ini')
        print(config['Path']['DB'])
        print(os.path.abspath(config['Path']['DB']))
        self.dir_db = os.path.abspath(config['Path']['DB'])
        for key in self.__files.keys():
            self.__files[key] = os.path.join(self.dir_db, self.__files[key])
        self.__OpenDb()

    def __OpenDb(self):
        # マスターDB生成（ファイル、テーブル、データ挿入）
        if None is self.__lang:
            if not os.path.isfile(self.__files['lang']):
                m = database.src.language.Main.Main(self.__files['lang'])
                m.Run()
            self.__lang = dataset.connect('sqlite:///' + self.__files['lang'])
        if None is self.__api:
            self.__api = dataset.connect('sqlite:///' + self.__files['api'])
            if not os.path.isfile(self.__files['api']):
                m = database.src.api.Main.Main(self.__files['api'])
                m.Run()
            self.__api = dataset.connect('sqlite:///' + self.__files['api'])
        if None is self.__gnu_license:
            self.__gnu_license = dataset.connect('sqlite:///' + self.__files['gnu_license'])
            if not os.path.isfile(self.__files['gnu_license']):
                m = database.src.gnu_license.Main.Main(self.__files['gnu_license'])
                m.Run()
            self.__gnu_license = dataset.connect('sqlite:///' + self.__files['gnu_license'])

        # アカウントDB生成（ファイル、テーブル作成。データ挿入はCUIにて行う）
        if None is self.__account:
            self.__account = dataset.connect('sqlite:///' + self.__files['account'])
            if not os.path.isfile(self.__files['account']):
                m = database.src.account.Main.Main(self.__files['account'])
                m.Create()
            self.__account = dataset.connect('sqlite:///' + self.__files['account'])

        # DB作成にTokenが必要なもの
        if 0 < self.__account['Accounts'].count():
            # ライセンスDB生成（ファイル、テーブル作成。データ挿入）
            if not(os.path.isfile(self.__files['license'])):
                print(self.__files['license'])
                account = self.__account['Accounts'].find().next()
                twofactor = self.__account['TwoFactors'].find_one(AccountId=account['Id'])
                authentications = []
                if None is not twofactor:
                    authentications.append(TwoFactorAuthentication(account['Username'], account['Password'], twofactor['Secret']))
                else:
                    authentications.append(BasicAuthentication(account['Username'], account['Password']))
                client = web.service.github.api.v3.Client.Client(self, authentications)
                l = database.src.license.Main.Main(self, client)
                l.Create()
                self.__license = dataset.connect('sqlite:///' + self.__files['license'])
                l.Insert()
            self.__license = dataset.connect('sqlite:///' + self.__files['license'])
            # 自分アカウントのリポジトリDB生成（ファイル、テーブル作成。データ挿入）
            for account in self.__account['Accounts'].find():
                self.__OpenRepo(account['Username'])
            # 他者アカウントのリポジトリDB生成（ファイル、テーブル作成。データ挿入）

    def __OpenRepo(self, username):
        is_create = False
        path = self.__files['repo'].replace('{user}', username)
        if not(os.path.isfile(path)):
            # DBテーブル作成
            path_sh = os.path.join(self.__path_dir_this, 'repo/create/Create.sh')
            subprocess.call(shlex.split("bash \"{0}\" \"{1}\"".format(path_sh, path)))
            self.__repos[username] = dataset.connect('sqlite:///' + path)
            # DBレコード挿入
            authData = web.service.github.api.v3.AuthenticationData.AuthenticationData()
            authData.Load(self.__account, username)
            # ダミー引数を渡す
            account = self.__account['Accounts'].find_one(Username=username)
            twofactor = self.__account['TwoFactors'].find_one(AccountId=account['Id'])
            authentications = []
            if None is not twofactor:
                authentications.append(TwoFactorAuthentication(account['Username'], account['Password'], twofactor['Secret']))
            else:
                authentications.append(BasicAuthentication(account['Username'], account['Password']))
            client = web.service.github.api.v3.Client.Client(self, authentications)
            inserter = database.src.repo.insert.command.repositories.Inserter.Inserter(self, username, client)
            inserter.Insert()
        if not(username in self.__repos.keys()):
            self.__repos[username] = dataset.connect('sqlite:///' + path)

