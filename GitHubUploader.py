#!/usr/bin/python3
#!python3
#encoding:utf-8
import sys
import os.path
import subprocess
import configparser
import argparse
import web.service.github.api.v3.AuthenticationsCreator
import web.service.github.api.v3.AuthenticationData
#import web.service.github.api.v3.CurrentUser
import web.service.github.api.v3.CurrentRepository
import web.service.github.api.v3.Client
import database.src.Database
import cui.uploader.Main

class Main:
    def __init__(self):
        pass

    def Run(self):
        parser = argparse.ArgumentParser(
            description='GitHub Repository Uploader.',
        )
        parser.add_argument('path_dir_pj')
        parser.add_argument('-u', '--username')
        parser.add_argument('-d', '--description')
        parser.add_argument('-l', '--homepage', '--link', '--url')
        args = parser.parse_args()
#        print(args)
#        print('path_dir_pj: {0}'.format(args.path_dir_pj))
#        print('-u: {0}'.format(args.username))
#        print('-d: {0}'.format(args.description))
#        print('-l: {0}'.format(args.homepage))

        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))
        path_dir_db = os.path.abspath(config['Path']['DB'])
        print(path_dir_db)
        
        if None is args.username:
            args.username = config['GitHub']['User']
#            print('default-username: {0}'.format(args.username))
#        print(os.path.join(path_dir_db, 'GitHub.Accounts.sqlite3'))
#        print(os.path.join(path_dir_db, 'GitHub.Repositories.{0}.sqlite3'.format(args.username)))
        
        self.__db = database.src.Database.Database()
        self.__db.Initialize()
        
        if None is self.__db.Accounts['Accounts'].find_one(Username=args.username):
            print('指定したユーザ {0} はDBに存在しません。GitHubUserRegister.pyで登録してください。')
            return
        
        creator = web.service.github.api.v3.AuthenticationsCreator.AuthenticationsCreator(self.__db, args.username)
        authentications = creator.Create()
#        user = web.service.github.api.v3.CurrentUser.CurrentUser(self.__db, args.username)
        repo = web.service.github.api.v3.CurrentRepository.CurrentRepository(self.__db, args.path_dir_pj, description=args.description, homepage=args.homepage)
        authData = web.service.github.api.v3.AuthenticationData.AuthenticationData()
        authData.Load(self.__db.Accounts, args.username)
        client = web.service.github.api.v3.Client.Client(self.__db, authentications, authData=authData, repo=repo)
        main = cui.uploader.Main.Main(self.__db, client, authData, repo)
        main.Run()


if __name__ == '__main__':
    main = Main()
    main.Run()
